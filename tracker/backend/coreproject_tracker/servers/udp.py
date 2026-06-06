import logging
import sys
from contextlib import asynccontextmanager
from typing import cast

import anyio
from quart import json

from coreproject_tracker.constants import (
    ANNOUNCE_INTERVAL,
    CONNECTION_ID,
)
from coreproject_tracker.datastructures import (
    MutableBox,
    RedisDatastructure,
    UdpDatastructure,
)
from coreproject_tracker.enums import ACTIONS, EVENT_NAMES, REDIS_NAMESPACE_ENUM
from coreproject_tracker.envs import REDIS_URI
from coreproject_tracker.functions import (
    addrs_to_compact,
    convert_event_id_to_event_enum,
    from_uint16,
    from_uint32,
    from_uint64,
    hdel,
    select_peers,
    to_uint32,
)
from coreproject_tracker.geo import resolve_country
from coreproject_tracker.singletons import RedisHandler
from coreproject_tracker.transaction import rollback_on_exception
from coreproject_tracker.validators import check_rate_limit, is_blocked


@asynccontextmanager
async def redis_lifecycle():
    redis = RedisHandler(REDIS_URI)
    await redis.init_redis()
    try:
        yield redis
    finally:
        await redis.close_redis()


def make_udp_packet(params: UdpDatastructure) -> bytes:
    if params.action == ACTIONS.CONNECT:
        return b"".join([
            to_uint32(ACTIONS.CONNECT),
            to_uint32(params.transaction_id),
            params.connection_id,
        ])

    if params.action == ACTIONS.ANNOUNCE:
        return b"".join([
            to_uint32(ACTIONS.ANNOUNCE),
            to_uint32(params.transaction_id),
            to_uint32(params.interval),
            to_uint32(params.incomplete),
            to_uint32(params.complete),
            params.peers,
        ])

    if params.action == ACTIONS.SCRAPE:
        return b"".join([
            to_uint32(ACTIONS.SCRAPE),
            to_uint32(params.transaction_id),
            params.scrape_data,
        ])

    raise ValueError(f"Action not implemented: {params.action}")


async def _handle_announce(
    data: UdpDatastructure,
    host: str,
    port: int,
) -> tuple[bytes, bool]:
    peer_key = f"{data.ip}:{data.port}"

    # Resolve country (non-blocking, cached in Redis)
    country = await resolve_country(data.ip)

    redis_storage = RedisDatastructure(
        info_hash=data.info_hash.hex(),
        type="udp",
        peer_id=data.peer_id,
        peer_ip=data.ip,
        port=data.port,
        left=data.left,
        country=country,
    )
    await redis_storage.save()

    # Geo-aware peer selection with oversampling + ranking
    ranked_peers = await select_peers(
        requester_ip=data.ip,
        info_hash=data.info_hash.hex(),
        numwant=data.numwant,
        namespace=REDIS_NAMESPACE_ENUM.HTTP_UDP,
    )

    peers = MutableBox[list[str]]([])
    seeders = MutableBox[int](0)
    leechers = MutableBox[int](0)

    for ranked in ranked_peers:
        try:
            with rollback_on_exception(peers, seeders, leechers):
                if ranked.left == 0:
                    seeders.value += 1
                else:
                    leechers.value += 1
                peers.value.append(f"{ranked.peer_ip}:{ranked.port}")
        except TypeError:
            logging.error(f"Error in peer data, deleting: {data.peer_id}")
            await hdel(
                data.info_hash.hex(),
                peer_key,
                namespace=REDIS_NAMESPACE_ENUM.HTTP_UDP,
            )

    compact_peers = addrs_to_compact(peers.value)

    if data.event_name == EVENT_NAMES.STOP:
        await hdel(
            data.info_hash.hex(),
            peer_key,
            namespace=REDIS_NAMESPACE_ENUM.HTTP_UDP,
        )
        should_delete = True
    else:
        should_delete = False

    packet = b"".join([
        to_uint32(ACTIONS.ANNOUNCE),
        to_uint32(data.transaction_id),
        to_uint32(data.interval),
        to_uint32(leechers.value),
        to_uint32(seeders.value),
        compact_peers,
    ])

    logging.info(
        f"UDP announce {data.info_hash.hex()} v4={len(peers.value)} "
        f"s={seeders.value} l={leechers.value}"
    )
    return packet, should_delete


async def _handle_scrape(data: UdpDatastructure, info_hashes: list[bytes]) -> bytes:
    torrents = bytearray()
    for info_hash_bytes in info_hashes:
        info_hash_hex = info_hash_bytes.hex()
        seeders = 0
        leechers = 0

        # Use select_peers with large numwant to get all peers for scrape
        ranked_peers = await select_peers(
            requester_ip="0.0.0.0",
            info_hash=info_hash_hex,
            numwant=999999,
            namespace=REDIS_NAMESPACE_ENUM.HTTP_UDP,
        )
        for ranked in ranked_peers:
            if ranked.left == 0:
                seeders += 1
            else:
                leechers += 1

        ih_bencoded = f"{len(info_hash_hex)}:{info_hash_hex}".encode()
        stats = f"l5:completei{seeders}e8:incompletei{leechers}ee"
        torrents.extend(ih_bencoded + stats.encode())

    scrape_body = b"d8:torrents" + torrents + b"e"
    logging.info(f"UDP scrape {len(info_hashes)} torrents")
    return b"".join([
        to_uint32(ACTIONS.SCRAPE),
        to_uint32(data.transaction_id),
        scrape_body,
    ])


async def run_udp_server(server_host: str, server_port: int):
    logging.info(f"Running UDP server on udp://{server_host}:{server_port}")
    opts: dict[str, str | int | bool] = {
        "local_host": server_host,
        "local_port": server_port,
    }
    if sys.platform != "win32":
        opts |= {"reuse_port": True}

    redis_manager = RedisHandler(REDIS_URI)
    await redis_manager.init_redis()

    async with redis_lifecycle():
        async with await anyio.create_udp_socket(**opts) as udp:
            async for packet, (host, port) in udp:
                if len(packet) < 16:
                    await udp.sendto("Too small payload".encode(), host, port)
                    continue

                _data = {
                    "connection_id": packet[0:8],
                    "action": from_uint32(packet[8:12]),
                    "transaction_id": from_uint32(packet[12:16]),
                }
                data = UdpDatastructure(**_data)

                if is_blocked(host):
                    continue
                if not await check_rate_limit(host):
                    continue

                # CONNECT
                if data.action == ACTIONS.CONNECT:
                    packet = make_udp_packet(data)
                    await udp.sendto(packet, host, port)
                    continue

                # ANNOUNCE
                if data.action == ACTIONS.ANNOUNCE and len(packet) >= 98:
                    _data |= {
                        "info_hash": packet[16:36],
                        "peer_id": packet[36:56].hex(),
                        "downloaded": from_uint64(packet[56:64]),
                        "left": from_uint64(packet[64:72]),
                        "uploaded": from_uint64(packet[72:80]),
                        "event_name": convert_event_id_to_event_enum(
                            from_uint32(packet[80:84]),
                        ),
                        "ip": from_uint32(packet[84:88]) or host,
                        "key": from_uint32(packet[88:92]),
                        "numwant": from_uint32(packet[92:96]),
                        "port": from_uint16(packet[96:98]) or port,
                    }
                    data = UdpDatastructure(**_data)

                    resp_packet, _ = await _handle_announce(data, host, port)
                    await udp.sendto(resp_packet, host, port)
                    continue

                # SCRAPE
                if data.action == ACTIONS.SCRAPE:
                    pos = 16
                    info_hashes = []
                    while pos + 20 <= len(packet):
                        info_hashes.append(packet[pos:pos + 20])
                        pos += 20

                    if info_hashes:
                        resp_packet = await _handle_scrape(data, info_hashes)
                        await udp.sendto(resp_packet, host, port)
                        continue

                # Unknown action or malformed
                error_packet = b"".join([
                    to_uint32(ACTIONS.ERROR),
                    to_uint32(data.transaction_id),
                    b"The server understands the action but the request violates its constrain",
                ])
                await udp.sendto(error_packet, host, port)

        await redis_manager.close_redis()