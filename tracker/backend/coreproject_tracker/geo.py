import asyncio
import logging
import os
from pathlib import Path
from typing import Optional

import geoip2.database

from coreproject_tracker.constants import HASH_EXPIRE_TIME
from coreproject_tracker.singletons import get_redis

logger = logging.getLogger(__name__)

_GEOIP_DB_PATH = os.environ.get("GEOIP_DB_PATH", "./GeoLite2-Country.mmdb")
_geo_reader: Optional[geoip2.database.Reader] = None
_geo_available = False


def _init_geoip() -> bool:
    global _geo_reader, _geo_available
    if _geo_reader is not None:
        return _geo_available
    try:
        if Path(_GEOIP_DB_PATH).exists():
            _geo_reader = geoip2.database.Reader(_GEOIP_DB_PATH)
            _geo_available = True
            logger.info("GeoIP database loaded from %s", _GEOIP_DB_PATH)
        else:
            logger.warning("GeoIP database not found at %s, geo lookups disabled", _GEOIP_DB_PATH)
    except Exception:
        logger.warning("Failed to load GeoIP database: %s", _GEOIP_DB_PATH)
    return _geo_available


def _close_geoip() -> None:
    global _geo_reader
    if _geo_reader:
        _geo_reader.close()
        _geo_reader = None


def _resolve_country_local(ip: str) -> Optional[str]:
    if not _geo_available:
        _init_geoip()
    try:
        if _geo_reader:
            response = _geo_reader.country(ip)
            return response.country.iso_code
    except Exception:
        pass
    return None


async def resolve_country(ip: str) -> Optional[str]:
    """Resolve IP to ISO 3166-1 alpha-2 country code.

    Checks Redis cache first, then GeoIP DB, then caches result.
    Non-blocking: returns None if all lookups fail.
    """
    r = get_redis()

    # Check Redis cache first (single round-trip)
    cached = await r.get(f"geo:{ip}")
    if cached:
        await r.expire(f"geo:{ip}", HASH_EXPIRE_TIME)
        return cached.decode() if isinstance(cached, bytes) else str(cached)

    # Resolve via GeoIP
    country = await asyncio.to_thread(_resolve_country_local, ip)

    if country:
        await r.set(f"geo:{ip}", country, ex=HASH_EXPIRE_TIME)
    elif _geo_available:
        # Cache miss sentinel (short TTL to avoid thrashing)
        await r.set(f"geo:{ip}", "__MISS__", ex=3600)

    return country


async def resolve_countries_batch(ips: list[str]) -> dict[str, Optional[str]]:
    """Batch resolve IPs to countries with Redis pipeline.

    Pipeline: MGET all -> resolve missing -> MSET results.
    Minimizes Redis round-trips to 3 max regardless of batch size.
    """
    if not ips:
        return {}

    r = get_redis()
    cache_keys = [f"geo:{ip}" for ip in ips]

    # Pipeline MGET
    pipe = await r.pipeline()
    for key in cache_keys:
        await pipe.get(key)
    cached_values = await pipe.execute()

    resolved: dict[str, Optional[str]] = {}
    to_resolve: list[tuple[str, str]] = []  # (cache_key, ip)

    for (ip, val), key in zip(zip(ips, cached_values), cache_keys):
        if val is None:
            to_resolve.append((key, ip))
        else:
            country = val.decode() if isinstance(val, bytes) else str(val)
            await r.expire(key, HASH_EXPIRE_TIME)
            resolved[ip] = None if country == "__MISS__" else country

    # Resolve uncached IPs (run in thread to not block event loop)
    if to_resolve:
        results = await asyncio.to_thread(
            _batch_resolve_local, [ip for _, ip in to_resolve]
        )
        # Pipeline MSET
        if results:
            pipe = await r.pipeline()
            for (key, ip), country in zip(to_resolve, results):
                if country:
                    await pipe.set(key, country, ex=HASH_EXPIRE_TIME)
                else:
                    await pipe.set(key, "__MISS__", ex=3600)
                resolved[ip] = country
            await pipe.execute()

    return resolved


def _batch_resolve_local(ips: list[str]) -> list[Optional[str]]:
    _init_geoip()
    results: list[Optional[str]] = []
    for ip in ips:
        results.append(_resolve_country_local(ip))
    return results
