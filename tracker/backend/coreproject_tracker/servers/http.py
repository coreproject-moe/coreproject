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
    hmget,
    zrandmember,
)
from coreproject_tracker.singletons import get_redis
from coreproject_tracker.transaction import rollback_on_exception
from coreproject_tracker.validators import check_rate_limit, is_blocked

http_blueprint = Blueprint("http", __name__)


async def get_ip():
    return request.headers.get("X-Real-IP", request.remote_addr)


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

    redis_storage = RedisDatastructure(
        info_hash=data.info_hash,
        type="http",
        peer_id=data.peer_id,
        peer_ip=data.peer_ip,
        port=data.port,
        left=data.left,
    )

    await redis_storage.save()

    peers = MutableBox[list[dict[str, str]]]([])
    peers6 = MutableBox[list[dict[str, str]]]([])
    seeders = MutableBox[int](0)
    leechers = MutableBox[int](0)

    random_peer_keys = await zrandmember(
        hash_key=data.info_hash,
        numwant=data.numwant,
        namespace=REDIS_NAMESPACE_ENUM.HTTP_UDP,
    )
    peer_json_list = await hmget(
        hash_key=data.info_hash,
        fields=random_peer_keys,
        namespace=REDIS_NAMESPACE_ENUM.HTTP_UDP,
    )

    for peer in peer_json_list:
        if not peer:
            continue
        try:
            with rollback_on_exception(peers, peers6, seeders, leechers):
                peer_data = RedisDatastructure(**json.loads(peer))

                if peer_data.left == 0:
                    seeders.value += 1
                else:
                    leechers.value += 1

                appendable_data = {
                    "peer id": peer_data.peer_id,
                    "ip": peer_data.peer_ip,
                    "port": peer_data.port,
                }

                if (ip_type := check_ip_type(peer_data.peer_ip)):
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

    seeders = 0
    leechers = 0

    peer_keys = await zrandmember(
        hash_key=info_hash,
        numwant=999999,
        namespace=REDIS_NAMESPACE_ENUM.HTTP_UDP,
    )
    if peer_keys:
        peer_json_list = await hmget(
            hash_key=info_hash,
            fields=peer_keys,
            namespace=REDIS_NAMESPACE_ENUM.HTTP_UDP,
        )
        for peer in peer_json_list:
            if peer:
                try:
                    peer_data = RedisDatastructure(**json.loads(peer))
                    if peer_data.left == 0:
                        seeders += 1
                    else:
                        leechers += 1
                except TypeError:
                    pass

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