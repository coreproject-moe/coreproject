import logging
import sys
from contextlib import asynccontextmanager
from typing import cast

import anyio
from quart import json

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
    hmget,
    to_uint32,
    zrandmember,
)
from coreproject_tracker.singletons import RedisHandler
from coreproject_tracker.transaction import rollback_on_exception


@asynccontextmanager
async def redis_lifecycle():
    redis = RedisHandler(REDIS_URI)
    await redis.init_redis()
    try:
        yield redis
    finally:
        await redis.close_redis()


async def make_udp_packet(params: UdpDatastructure) -> bytes:
    """
    Create UDP packets for BitTorrent tracker protocol.

    Args:
        params: Dictionary containing packet parameters including 'action' and other action-specific parameters.

    Returns:
        bytes: The constructed UDP packet

    Raises:
        ValueError: If the action is not implemented
    """

    if params.action == ACTIONS.CONNECT:
        packet = b"".join(
            [
                await to_uint32(ACTIONS.CONNECT),
                await to_uint32(params.transaction_id),
                params.connection_id,
            ]
        )

    elif params.action == ACTIONS.ANNOUNCE:
        packet = b"".join(
            [
                await to_uint32(ACTIONS.ANNOUNCE),
                await to_uint32(params.transaction_id),
                await to_uint32(params.interval),
                await to_uint32(params.incomplete),
                await to_uint32(params.complete),
                params.peers,
            ]
        )

    else:
        raise ValueError(f"Action not implemented: {params.action}")

    return packet


async def run_udp_server(server_host: str, server_port: int):
    logging.info(f"Running UDP server on udp://{server_host}:{server_port}")
    opts: dict[str, str | int | bool] = {
        "local_host": server_host,
        "local_port": server_port,
    }
    if sys.platform != "win32":
        opts |= {
            "reuse_port": True,
        }

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
                    "action": await from_uint32(packet[8:12]),
                    "transaction_id": await from_uint32(packet[12:16]),
                }
                data = UdpDatastructure(**_data)

                if data.action == ACTIONS.ANNOUNCE:
                    _data |= {
                        "info_hash": packet[16:36],  # 20 bytes
                        "peer_id": packet[36:56].hex(),  # 20 bytes
                        "downloaded": from_uint64(
                            packet[56:64]  # Convert 64-bit unsigned integer
                        ),
                        "left": from_uint64(
                            packet[64:72]  # Convert 64-bit unsigned integer
                        ),
                        "uploaded": from_uint64(
                            packet[72:80]  # Convert 64-bit unsigned integer
                        ),
                        "event_name": await convert_event_id_to_event_enum(
                            await from_uint32(
                                packet[80:84]  # Read 4-byte unsigned int (big-endian)
                            ),
                        ),
                        "ip": await from_uint32(packet[84:88]) or host,
                        "key": await from_uint32(packet[88:92]),
                        "numwant": await from_uint32(packet[92:96]),
                        "port": await from_uint16(packet[96:98]) or port,
                    }
                    data = UdpDatastructure(**_data)
                    redis_stroage = RedisDatastructure(
                        info_hash=data.info_hash.hex(),
                        type="udp",
                        peer_id=data.peer_id,
                        peer_ip=data.ip,
                        port=data.port,
                        left=data.left,
                    )

                    await redis_stroage.save()

                    random_peer_keys = await zrandmember(
                        hash_key=data.info_hash.hex(),
                        numwant=data.numwant,
                        namespace=REDIS_NAMESPACE_ENUM.HTTP_UDP,
                    )
                    peer_json_list = await hmget(
                        hash_key=data.info_hash.hex(),
                        fields=random_peer_keys,
                        namespace=REDIS_NAMESPACE_ENUM.HTTP_UDP,
                    )

                    peers = MutableBox[list[str]]([])
                    seeders = leechers = MutableBox[int](0)

                    for peer in peer_json_list:
                        peer = cast(str, peer)

                        try:
                            with rollback_on_exception(peers, seeders, leechers):
                                peer_data = RedisDatastructure(**json.loads(peer))
                                if peer_data.left == 0:
                                    seeders.value += 1
                                else:
                                    leechers.value += 1

                                peers.value.append(
                                    f"{peer_data.peer_ip}:{peer_data.port}"
                                )

                        except TypeError:
                            # Error in the peer data, delete the peer
                            logging.error(
                                f"Error in peer data, deleting the peer: {data.peer_id}"
                            )
                            await hdel(
                                data.info_hash.hex(),
                                f"{data.ip}:{data.port}",
                                namespace=REDIS_NAMESPACE_ENUM.HTTP_UDP,
                            )

                    _data |= {
                        "peers": await addrs_to_compact(peers.value),
                        "complete": seeders.value,
                        "incomplete": leechers.value,
                    }
                    data = UdpDatastructure(**_data)

                if data.event_name == EVENT_NAMES.STOP:
                    await hdel(
                        data.info_hash.hex(),
                        f"{data.ip}:{data.port}",
                        namespace=REDIS_NAMESPACE_ENUM.HTTP_UDP,
                    )

                packet = await make_udp_packet(data)
                logging.info(f"Sent UDP packet for {host}:{port}")
                await udp.sendto(packet, host, port)

        await redis_manager.close_redis()
