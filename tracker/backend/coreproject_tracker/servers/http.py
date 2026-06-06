import logging
import platform
from http import HTTPStatus
from importlib.metadata import version
from typing import cast

import bencodepy
from quart import Blueprint, json, jsonify, request

from coreproject_tracker.constants import ANNOUNCE_INTERVAL
from coreproject_tracker.datastructures import (
    HttpDatastructure,
    MutableBox,
    RedisDatastructure,
)
from coreproject_tracker.enums import EVENT_NAMES, IP, REDIS_NAMESPACE_ENUM
from coreproject_tracker.functions import (
    check_ip_type,
    convert_event_name_to_event_enum,
    decode_dictionary,
    get_all_hash_keys,
    hdel,
    select_peers,
)
from coreproject_tracker.geo import resolve_country
from coreproject_tracker.singletons import get_redis
from coreproject_tracker.transaction import rollback_on_exception
from coreproject_tracker.validators import check_rate_limit, is_blocked

http_blueprint = Blueprint("http", __name__)


async def get_ip() -> str:
    """Extract real client IP from various reverse proxy headers.

    Supports: nginx (X-Real-IP, X-Forwarded-For), Caddy (Forwarded),
    Apache (X-Forwarded-For), HAProxy (X-Forwarded-For),
    Cloudflare (CF-Connecting-IP, True-Client-IP),
    Fly.io (Fly-Client-IP), Plesk (X-Cluster-Client-IP).

    Returns the first (client) IP from comma-separated chains to prevent spoofing.
    """
    # Try each proxy header in priority order
    for header in (
        "X-Real-IP",           # nginx
        "CF-Connecting-IP",   # Cloudflare
        "True-Client-IP",     # Cloudflare/Akamai
        "X-Cluster-Client-IP",  # Plesk
        "Fly-Client-IP",      # Fly.io
        "X-Forwarded-For",    # nginx/Apache/HAProxy/Caddy
        "Forwarded",          # RFC 7239 (Caddy/Apache)
    ):
        value = request.headers.get(header)
        if value:
            # Handle "Forwarded: for=1.2.3.4" format (RFC 7239)
            if header == "Forwarded":
                # for=1.2.3.4,for=5.6.7.8
                for part in value.split(","):
                    part = part.strip()
                    if part.startswith("for="):
                        ip = part.split("=", 1)[1].strip()
                        return ip or request.remote_addr or "0.0.0.0"
            # Handle comma-separated chains (X-Forwarded-For: client, proxy1, proxy2)
            # First IP = original client
            elif "," in value:
                return value.split(",")[0].strip()
            return value.strip()

    return request.remote_addr or "0.0.0.0"


@http_blueprint.route("/")
async def home_endpoint(extra: str = "") -> str:
    if ip := await get_ip():
        return f"""
🐟🐈 ⸜(｡˃ ᵕ ˂ )⸝♡
<br/>
{ip}
<br/>
{extra}
"""
    return "hello"


@http_blueprint.route("/announce")
async def http_endpoint():
    if not request.args:
        return await home_endpoint("hello from announce")

    ip = await get_ip()
    if is_blocked(ip):
        logging.warning(f"Blocked IP attempted announce: {ip}")
        return "blocked", HTTPStatus.FORBIDDEN
    if not await check_rate_limit(ip):
        logging.warning(f"Rate limit exceeded: {ip}")
        return "rate limited", HTTPStatus.TOO_MANY_REQUESTS

    try:
        _data = {
            "info_hash_raw": request.args.get("info_hash"),
            "port": request.args.get("port"),
            "left": request.args.get("left"),
            "numwant": request.args.get("numwant"),
            "peer_ip": ip,
            "peer_id": request.args.get("peer_id"),
        }
        if event := request.args.get("event"):
            _data |= {"event_name": convert_event_name_to_event_enum(event)}
        data = HttpDatastructure(**_data)  # type: ignore[call-arg]

    except Exception as e:
        logging.error(f"HTTP announce parse error: {e}")
        return str(e), HTTPStatus.BAD_REQUEST

    if data.event_name == EVENT_NAMES.STOP:
        await hdel(
            data.info_hash,
            f"{data.peer_ip}:{data.port}",
            namespace=REDIS_NAMESPACE_ENUM.HTTP_UDP,
        )
        return ""

    # Resolve country (non-blocking, cached in Redis)
    country = await resolve_country(ip)

    redis_storage = RedisDatastructure(
        info_hash=data.info_hash,
        type="http",
        peer_id=data.peer_id,
        peer_ip=data.peer_ip,
        port=data.port,
        left=data.left,
        country=country,
    )

    await redis_storage.save()

    # Geo-aware peer selection with oversampling + ranking
    ranked_peers = await select_peers(
        requester_ip=ip,
        info_hash=data.info_hash,
        numwant=data.numwant,
        namespace=REDIS_NAMESPACE_ENUM.HTTP_UDP,
    )

    peers = MutableBox[list[dict[str, str]]]([])
    peers6 = MutableBox[list[dict[str, str]]]([])
    seeders = MutableBox[int](0)
    leechers = MutableBox[int](0)

    for ranked in ranked_peers:
        try:
            with rollback_on_exception(peers, peers6, seeders, leechers):
                if ranked.left == 0:
                    seeders.value += 1
                else:
                    leechers.value += 1

                appendable_data = {
                    "peer id": ranked.peer_id,
                    "ip": ranked.peer_ip,
                    "port": ranked.port,
                }

                if (ip_type := check_ip_type(ranked.peer_ip)):
                    if ip_type == IP.IPV4:
                        peers.value.append(appendable_data)
                    else:
                        peers6.value.append(appendable_data)

        except TypeError:
            logging.error(f"Error in peer data, deleting: {data.peer_id}")
            await hdel(
                data.info_hash,
                f"{data.peer_ip}:{data.port}",
                namespace=REDIS_NAMESPACE_ENUM.HTTP_UDP,
            )

    output = {
        "peers": peers.value,
        "peers6": peers6.value,
        "min interval": ANNOUNCE_INTERVAL,
        "complete": seeders.value,
        "incomplete": leechers.value,
    }
    logging.info(
        f"HTTP announce {data.info_hash} event={data.event_name} "
        f"v4={len(peers.value)} v6={len(peers6.value)} "
        f"s={seeders.value} l={leechers.value}"
    )
    return bencodepy.bencode(output)


@http_blueprint.route("/scrape")
async def scrape_endpoint():
    if not request.args:
        return await home_endpoint("hello from scrape")

    ip = await get_ip()
    if is_blocked(ip):
        return "blocked", HTTPStatus.FORBIDDEN
    if not await check_rate_limit(ip):
        return "rate limited", HTTPStatus.TOO_MANY_REQUESTS

    info_hash_raw = request.args.get("info_hash")
    if not info_hash_raw:
        return "info_hash required", HTTPStatus.BAD_REQUEST

    info_hash = info_hash_raw if isinstance(info_hash_raw, str) else info_hash_raw.hex()

    # Use select_peers with large numwant to get all peers for scrape
    ranked_peers = await select_peers(
        requester_ip=ip,
        info_hash=info_hash,
        numwant=999999,
        namespace=REDIS_NAMESPACE_ENUM.HTTP_UDP,
    )
    for ranked in ranked_peers:
        if ranked.left == 0:
            seeders += 1
        else:
            leechers += 1

    response = {
        "files": {
            info_hash: {
                "complete": seeders,
                "incomplete": leechers,
            }
        }
    }
    logging.info(f"HTTP scrape {info_hash} s={seeders} l={leechers}")
    return bencodepy.bencode(response)


@http_blueprint.route("/api")
async def api_endpoint():
    r = get_redis()

    redis_information = await r.info()
    redis_server_version = redis_information["redis_version"]
    redis_client_version = version("redis")

    quart_version = version("quart")
    python_version = platform.python_version()

    hash_keys = await get_all_hash_keys()
    pipe = await r.pipeline()
    for hash_key in hash_keys:
        await pipe.hgetall(hash_key)  # type: ignore[no-untyped-call]
    hash_data = await pipe.execute()

    result = dict(zip(hash_keys, hash_data))
    result = await decode_dictionary(result)

    data = {
        "quart_version": quart_version,
        "redis_version": {
            "client": redis_client_version,
            "server": redis_server_version,
        },
        "python_version": python_version,
        "redis_data": result,
    }
    return jsonify(data), HTTPStatus.OK


@http_blueprint.route("/api/geo")
async def geo_api_endpoint():
    """Return geo database stats for the frontend."""
    from coreproject_tracker.geo import get_geo_stats

    stats = get_geo_stats()
    return jsonify(stats), HTTPStatus.OK


@http_blueprint.route("/api/tracker_data")
async def tracker_data_endpoint():
    """Return all swarm peer data with country codes for the radar map.

    Frontend uses this to render connection lines on the map.
    Heavily cached in Redis - geo lookups use TTL cache.
    """
    from coreproject_tracker.geo import resolve_countries_batch

    r = get_redis()

    # Get all hash keys (swarms)
    hash_keys = await get_all_hash_keys()

    # Decode all hash data
    pipe = await r.pipeline()
    for hash_key in hash_keys:
        await pipe.hgetall(hash_key)
    raw_hash_data = await pipe.execute()

    decoded = await decode_dictionary(dict(zip(hash_keys, raw_hash_data)))

    # Collect all unique IPs for batch geo resolution
    all_ips: list[str] = []
    for swarm_key, peers in decoded.items():
        if not isinstance(peers, dict):
            continue
        for peer_key, peer_json_str in peers.items():
            if not isinstance(peer_json_str, dict):
                continue
            ip = peer_json_str.get("peer_ip", "")
            if ip and ip not in all_ips:
                all_ips.append(ip)

    # Batch resolve all IPs to countries (Redis-cached)
    country_map = await resolve_countries_batch(all_ips)

    # Build response: list of swarms with peer locations
    swarms = []
    total_peers = 0
    for swarm_key, peers in decoded.items():
        if not isinstance(peers, dict):
            continue
        peer_list = []
        for peer_key, peer_data in peers.items():
            if not isinstance(peer_data, dict):
                continue
            ip = peer_data.get("peer_ip", "")
            peer_list.append({
                "ip": ip,
                "port": peer_data.get("port", 0),
                "country": country_map.get(ip) or peer_data.get("country", ""),
                "continent": "",
                "seeders": 1 if peer_data.get("left", 1) == 0 else 0,
            })
            total_peers += 1
        swarms.append({
            "info_hash": swarm_key.replace("http_udp:", "").replace("websocket:", ""),
            "peers": peer_list,
            "peer_count": len(peer_list),
        })

    return jsonify({
        "swarms": swarms,
        "total_peers": total_peers,
        "total_swarms": len(swarms),
    }), HTTPStatus.OK