import asyncio
import contextlib
import logging

from quart import Blueprint, copy_current_websocket_context, json, websocket

from coreproject_tracker.constants import WEBSOCKET_INTERVAL
from coreproject_tracker.datastructures import (
    MutableBox,
    RedisDatastructure,
    WebsocketDatastructure,
)
from coreproject_tracker.enums import ACTIONS, EVENT_NAMES, REDIS_NAMESPACE_ENUM
from coreproject_tracker.functions import (
    bytes_to_bin_str,
    convert_event_name_to_event_enum,
    hdel,
    hex_str_to_bin_str,
    select_peers,
)
from coreproject_tracker.geo import resolve_country
from coreproject_tracker.singletons import get_redis
from coreproject_tracker.transaction import rollback_on_exception

ws_blueprint = Blueprint("websocket", __name__)


@ws_blueprint.websocket("/announce")
async def websocket_announce_handler():
    """WebSocket announce endpoint for WebRTC peer-to-peer.

    Handles peer registration, geo-aware peer selection, and WebRTC
    offer/answer exchange via Redis pub/sub.
    """

    @copy_current_websocket_context
    async def parse_incoming_message() -> WebsocketDatastructure:
        """Parse and validate an incoming WebSocket message."""
        message = await websocket.receive_json()
        scoped_client_ip, client_port = websocket.scope.get("client")  # type: ignore
        client_ip = websocket.headers.get("X-Real-IP", scoped_client_ip)

        payload = {
            "ip": client_ip,
            "port": client_port,
            "addr": f"{client_ip}:{client_port}",
            "info_hash_raw": message["info_hash"],
            "action": message["action"],
            "peer_id": message["peer_id"],
            "numwant": message.get("numwant"),
            "uploaded": message.get("uploaded"),
            "offers": message.get("offers", []),
            "left": message.get("left"),
        }

        if message.get("answer"):
            payload |= {
                "answer": message["answer"],
                "to_peer_id": message["to_peer_id"],
                "offer_id": message["offer_id"],
            }

        if event := message.get("event"):
            payload |= {"event": convert_event_name_to_event_enum(event)}

        return WebsocketDatastructure(**payload)

    @copy_current_websocket_context
    async def listen_incoming_pubsub():
        """Listen for messages published to this peer's Redis channel."""
        while True:
            redis_message = await pubsub.get_message(
                ignore_subscribe_messages=True, timeout=1.0
            )
            if redis_message and redis_message["type"] == "message":
                await websocket.send_json(json.loads(redis_message["data"]))

    peer_request: WebsocketDatastructure = await parse_incoming_message()

    pubsub_listener_task: asyncio.Task | None = None
    redis_connection = get_redis()
    pubsub = redis_connection.pubsub()

    if not peer_request.peer_id:
        raise ValueError(
            "WEBSOCKET: `peer_id` is required for subscription to redis"
        )

    await pubsub.subscribe(f"peer:{peer_request.peer_id.hex()}")

    try:
        pubsub_listener_task = asyncio.create_task(listen_incoming_pubsub())

        while True:
            if peer_request.event == EVENT_NAMES.STOP:
                await websocket.close(1000, "Server received `stop` event")
                break

            response_payload = {"action": peer_request.action}

            if not peer_request.peer_id:
                raise ValueError(
                    "WEBSOCKET: `peer_id` is required for saving to redis"
                )

            # Resolve country (non-blocking, cached in Redis)
            peer_country = await resolve_country(peer_request.ip)

            peer_record = RedisDatastructure(
                info_hash=peer_request.info_hash,
                type="websocket",
                peer_id=peer_request.peer_id.hex(),
                peer_ip=peer_request.ip,
                port=peer_request.port,
                left=int(peer_request.left)
                if peer_request.left is not None
                else None,
                country=peer_country,
            )
            await peer_record.save()

            # Geo-aware peer selection with oversampling + ranking
            ranked_peers = await select_peers(
                requester_ip=peer_request.ip,
                info_hash=peer_request.info_hash,
                numwant=peer_request.numwant,
                namespace=REDIS_NAMESPACE_ENUM.WEBSOCKET,
            )

            seeder_count = MutableBox[int](0)
            leecher_count = MutableBox[int](0)

            for ranked_peer in ranked_peers:
                try:
                    with rollback_on_exception(seeder_count, leecher_count):
                        if ranked_peer.left == 0:
                            seeder_count.value += 1
                        else:
                            leecher_count.value += 1
                except TypeError:
                    pass

            response_payload |= {
                "completed": seeder_count.value,
                "incompleted": leecher_count.value,
            }

            if peer_request.action == ACTIONS.ANNOUNCE:
                response_payload |= {
                    "info_hash": hex_str_to_bin_str(peer_request.info_hash),
                    "interval": WEBSOCKET_INTERVAL,
                }
                await websocket.send_json(response_payload)

            if not peer_request.answer:
                await websocket.send_json(response_payload)

            # Distribute WebRTC offers to ranked peers
            if offers := peer_request.offers:
                for ranked_peer in ranked_peers:
                    target_peer_id = ranked_peer.peer_id
                    for offer in offers:
                        offer_message = json.dumps({
                            "action": "announce",
                            "offer": offer["offer"],
                            "offer_id": offer["offer_id"],
                            "peer_id": bytes_to_bin_str(peer_request.peer_id),
                            "info_hash": hex_str_to_bin_str(
                                peer_request.info_hash
                            ),
                        })
                        await redis_connection.publish(
                            f"peer:{target_peer_id}", offer_message
                        )

            # Forward WebRTC answer to target peer
            if peer_request.answer:
                if not peer_request.to_peer_id:
                    raise ValueError(
                        "WEBSOCKET: `to_peer_id` is required for answer"
                    )
                answer_message = json.dumps({
                    "action": "announce",
                    "answer": peer_request.answer,
                    "offer_id": peer_request.offer_id,
                    "peer_id": bytes_to_bin_str(peer_request.peer_id),
                    "info_hash": hex_str_to_bin_str(peer_request.info_hash),
                })
                await redis_connection.publish(
                    f"peer:{peer_request.to_peer_id.hex()}", answer_message
                )

            logging.info(
                "WebSocket announce %s event=%s",
                peer_request.info_hash,
                peer_request.event,
            )

            peer_request: WebsocketDatastructure = (
                await parse_incoming_message()
            )

    except asyncio.CancelledError:
        logging.info(
            "WebSocket disconnected `%s:%s`",
            peer_request.ip,
            peer_request.port,
        )
        raise
    finally:
        if pubsub_listener_task:
            pubsub_listener_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await pubsub_listener_task

        if pubsub:
            if peer_request.peer_id:
                await pubsub.unsubscribe(
                    f"peer:{peer_request.peer_id.hex()}"
                )
                await pubsub.close()
            await hdel(
                peer_request.info_hash,
                peer_request.addr,
                namespace=REDIS_NAMESPACE_ENUM.WEBSOCKET,
            )
