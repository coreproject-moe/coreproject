"""
GeoIP resolution using IPLocate.io CSV data.

IP geolocation database powered by IPLocate.io
Licensed under CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/)
Data source: IPLocate Country GeoIP Compatibility Database
Attribution: IP address data powered by <a href="https://iplocate.io">IPLocate.io</a>

This database is licensed under the CC BY-SA 4.0 license.
You can use, share, and adapt these databases for any purpose, including
commercially, as long as you give credit to IPLocate.io on your application,
product, or website where the data is used.

Architecture:
 - CSV parsed on first request, network index loaded into Redis with TTL
 - Individual IP→country lookups cached in Redis (24h TTL, auto-evict)
 - Lightweight in-memory network index for fallback (not full DB)
 - Non-blocking: returns None on any failure, never raises
"""

import asyncio
import csv
import ipaddress
import logging
import time
from pathlib import Path
from typing import Optional

from coreproject_tracker.constants import HASH_EXPIRE_TIME
from coreproject_tracker.singletons import get_redis

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# IPLocate CSV paths
# ---------------------------------------------------------------------------

_GEO_DATA_DIR = Path(__file__).parent / "geo_data"
_IPV4_BLOCKS_PATH = _GEO_DATA_DIR / "IPLocate-Country-GeoIPCompat-Blocks-IPv4.csv"
_IPV6_BLOCKS_PATH = _GEO_DATA_DIR / "IPLocate-Country-GeoIPCompat-Blocks-IPv6.csv"
_LOCATIONS_PATH = _GEO_DATA_DIR / "IPLocate-Country-GeoIPCompat-Locations-en.csv"

# ---------------------------------------------------------------------------
# Lightweight in-memory network index (loaded on first request, not at startup)
# Only stores network ranges + geoname_id, not full peer data.
# ---------------------------------------------------------------------------

_ipv4_networks: "list[ipaddress.IPv4Network]" = []
_ipv6_networks: "list[ipaddress.IPv6Network]" = []
_geoname_to_country: dict[int, str] = {}
_geoname_to_continent: dict[int, str] = {}
_geo_loaded = False
_geo_loading = False

# ---------------------------------------------------------------------------
# Redis geo cache TTLs
# ---------------------------------------------------------------------------

GEO_CACHE_TTL = HASH_EXPIRE_TIME  # 24h for active IPs
GEO_MISS_TTL = 3600  # 1h for miss sentinel
GEO_MISS_SENTINEL = "__MISS__"


# ---------------------------------------------------------------------------
# CSV parsers — streamed, minimal memory
# ---------------------------------------------------------------------------


def _parse_locations() -> None:
    """Parse locations CSV (9KB) into geoname→country/continent maps."""
    if not _LOCATIONS_PATH.exists():
        logger.warning("IPLocate locations file not found: %s", _LOCATIONS_PATH)
        return

    with open(_LOCATIONS_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            geoname_id = int(row["geoname_id"])
            _geoname_to_country[geoname_id] = row.get("country_iso_code", "")
            _geoname_to_continent[geoname_id] = row.get("continent_code", "")

    logger.info(
        "Loaded %d IPLocate location entries (CC BY-SA 4.0)",
        len(_geoname_to_country),
    )


def _parse_network_blocks() -> None:
    """Parse IPv4+IPv6 blocks CSV into lightweight network index.

    Each network object stores only the CIDR range + geoname_id.
    IPv4: ~200K blocks, IPv6: ~1K blocks. Total index: ~50MB.
    """
    # IPv4 blocks
    if _IPV4_BLOCKS_PATH.exists():
        count = 0
        with open(_IPV4_BLOCKS_PATH, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                network = ipaddress.IPv4Network(row["network"], strict=False)
                geoname_id = int(row["registered_country_geoname_id"])
                network.geoname_id = geoname_id  # type: ignore[attr-defined]
                _ipv4_networks.append(network)
                count += 1
        logger.info("Loaded %d IPLocate IPv4 blocks (CC BY-SA 4.0)", count)
    else:
        logger.warning("IPLocate IPv4 blocks not found: %s", _IPV4_BLOCKS_PATH)

    # IPv6 blocks
    if _IPV6_BLOCKS_PATH.exists():
        count = 0
        with open(_IPV6_BLOCKS_PATH, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                network = ipaddress.IPv6Network(row["network"], strict=False)
                geoname_id = int(row["registered_country_geoname_id"])
                network.geoname_id = geoname_id  # type: ignore[attr-defined]
                _ipv6_networks.append(network)
                count += 1
        logger.info("Loaded %d IPLocate IPv6 blocks (CC BY-SA 4.0)", count)
    else:
        logger.warning("IPLocate IPv6 blocks not found: %s", _IPV6_BLOCKS_PATH)


def _load_geo_csv() -> bool:
    """Load IPLocate CSV into memory index. Called once on first request."""
    global _geo_loaded, _geo_loading

    if _geo_loaded:
        return True
    if _geo_loading:
        return False  # Another coroutine is loading

    _geo_loading = True
    start = time.monotonic()
    try:
        _parse_locations()
        _parse_network_blocks()
        _geo_loaded = True
        elapsed = time.monotonic() - start
        logger.info(
            "IPLocate geo index loaded in %.2fs (%d countries, "
            "%d IPv4 blocks, %d IPv6 blocks)",
            elapsed,
            len(_geoname_to_country),
            len(_ipv4_networks),
            len(_ipv6_networks),
        )
    except Exception as e:
        logger.warning("Failed to load IPLocate geo index: %s", e)
        _geo_loaded = False
    finally:
        _geo_loading = False

    return _geo_loaded


# ---------------------------------------------------------------------------
# IP → country lookup
# ---------------------------------------------------------------------------


def _lookup_network_geoname(
    ip: ipaddress.IPv4Address | ipaddress.IPv6Address,
) -> Optional[int]:
    """Find geoname_id for an IP by scanning the network index.

    CSV is sorted by network address, so we stop when network start > IP.
    Last matching network = longest prefix (most specific).
    """
    matched: Optional[int] = None
    ip_int = int(ip)
    networks = _ipv4_networks if ip.version == 4 else _ipv6_networks

    for net in networks:
        if int(net.network_address) > ip_int:
            break
        if ip in net:
            matched = getattr(net, "geoname_id", None)

    return matched


def _sync_resolve_country(ip: str) -> Optional[str]:
    """Synchronous IP→country (safe for asyncio.to_thread)."""
    if not _geo_loaded:
        return None
    try:
        addr = ipaddress.ip_address(ip.strip("[]"))
        geoname_id = _lookup_network_geoname(addr)
        if geoname_id is not None:
            return _geoname_to_country.get(geoname_id)
    except (ValueError, KeyError):
        pass
    return None


# ---------------------------------------------------------------------------
# Public async API (Redis-cached)
# ---------------------------------------------------------------------------


async def resolve_country(ip: str) -> Optional[str]:
    """Resolve IP to ISO 3166-1 alpha-2 country code.

    Checks Redis cache first, then IPLocate index, then caches result.
    Redis TTL ensures frequently-used IPs stay hot, unused auto-evict.
    Non-blocking: returns None on any failure.
    """
    if not _geo_loaded:
        _load_geo_csv()

    r = get_redis()

    # Redis cache (single round-trip)
    cached = await r.get(f"geo:{ip}")
    if cached:
        await r.expire(f"geo:{ip}", GEO_CACHE_TTL)
        value = cached.decode() if isinstance(cached, bytes) else str(cached)
        return None if value == GEO_MISS_SENTINEL else value

    # Resolve via IPLocate index (thread to not block event loop)
    country = await asyncio.to_thread(_sync_resolve_country, ip)

    if country:
        await r.set(f"geo:{ip}", country, ex=GEO_CACHE_TTL)
    elif _geo_loaded:
        await r.set(f"geo:{ip}", GEO_MISS_SENTINEL, ex=GEO_MISS_TTL)

    return country


async def resolve_countries_batch(ips: list[str]) -> dict[str, Optional[str]]:
    """Batch resolve IPs to countries with Redis pipeline."""
    if not ips:
        return {}

    if not _geo_loaded:
        _load_geo_csv()

    r = get_redis()
    cache_keys = [f"geo:{ip}" for ip in ips]

    # Pipeline MGET
    pipe = await r.pipeline()
    for key in cache_keys:
        await pipe.get(key)
    cached_values = await pipe.execute()

    resolved: dict[str, Optional[str]] = {}
    to_resolve: list[tuple[str, str]] = []

    for (ip, val), key in zip(zip(ips, cached_values), cache_keys):
        if val is None:
            to_resolve.append((key, ip))
        else:
            country = val.decode() if isinstance(val, bytes) else str(val)
            await r.expire(key, GEO_CACHE_TTL)
            resolved[ip] = None if country == GEO_MISS_SENTINEL else country

    if to_resolve:
        results = await asyncio.to_thread(
            _batch_sync_resolve, [ip for _, ip in to_resolve]
        )
        if results:
            pipe = await r.pipeline()
            for (key, ip), country in zip(to_resolve, results):
                if country:
                    await pipe.set(key, country, ex=GEO_CACHE_TTL)
                else:
                    await pipe.set(key, GEO_MISS_SENTINEL, ex=GEO_MISS_TTL)
                resolved[ip] = country
            await pipe.execute()

    return resolved


def _batch_sync_resolve(ips: list[str]) -> list[Optional[str]]:
    """Synchronous batch resolve (safe for asyncio.to_thread)."""
    return [_sync_resolve_country(ip) for ip in ips]


# ---------------------------------------------------------------------------
# Stats / info for API endpoint
# ---------------------------------------------------------------------------


def get_geo_stats() -> dict:
    """Return geo database stats for the /api endpoint."""
    return {
        "provider": "IPLocate.io",
        "license": "CC BY-SA 4.0",
        "attribution_url": "https://iplocate.io",
        "loaded": _geo_loaded,
        "countries_count": len(_geoname_to_country),
        "ipv4_blocks_count": len(_ipv4_networks),
        "ipv6_blocks_count": len(_ipv6_networks),
    }


def get_country_info(country_code: str) -> dict:
    """Get country name and continent from geoname data."""
    for geoname_id, code in _geoname_to_country.items():
        if code == country_code:
            return {
                "code": country_code,
                "continent": _geoname_to_continent.get(geoname_id, ""),
            }
    return {"code": country_code, "continent": ""}
