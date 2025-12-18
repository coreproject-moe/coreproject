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
    hmget,
    zrandmember,
)
from coreproject_tracker.singletons import get_redis
from coreproject_tracker.transaction import rollback_on_exception

ws_blueprint = Blueprint("websocket", __name__)


@ws_blueprint.websocket("/announce")
async def ws():
    """
    WebSocket endpoint that uses Redis Pub/Sub for message dissemination.
    """

    @copy_current_websocket_context
    async def parse_websocket():
        initial_message = await websocket.receive_json()
        scoped_client_ip, client_port = websocket.scope.get("client")  # type: ignore

        # Change the client IP to the one from the headers if available
        client_ip = websocket.headers.get("X-Real-IP", scoped_client_ip)

        _data = {
            "ip": client_ip,
            "port": client_port,
            "addr": f"{client_ip}:{client_port}",
            "info_hash_raw": initial_message["info_hash"],
            "action": initial_message["action"],
            "peer_id": initial_message["peer_id"],
            "numwant": initial_message.get("numwant"),
            "uploaded": initial_message.get("uploaded"),
            "offers": initial_message.get("offers", []),
            "left": initial_message.get("left"),
        }

        if initial_message.get("answer"):
            _data |= {
                "answer": initial_message["answer"],
                "to_peer_id": initial_message["to_peer_id"],
                "offer_id": initial_message["offer_id"],
            }

        if event := initial_message.get("event"):
            _data |= {
                "event": await convert_event_name_to_event_enum(event),
            }

        return WebsocketDatastructure(**_data)

    @copy_current_websocket_context
    async def listen_pubsub():
        while True:
            message = await pubsub.get_message(
                ignore_subscribe_messages=True, timeout=1.0
            )
            if message and message["type"] == "message":
                await websocket.send_json(json.loads(message["data"]))

    # Explicitly define the `WebsocketDatastructure` cause the decorator fucks with type
    data: WebsocketDatastructure = await parse_websocket()

    task: asyncio.Task | None = None
    redis = get_redis()
    pubsub = redis.pubsub()

    # There will always be a `peer_id` in data
    if not data.peer_id:
        raise ValueError("WEBSOCKET: `peer_id` is required for subscription to redis")

    # Not using `peer:data.peer_id.hex()`
    # because using `peer:data.peer_id.hex()` causes phantom errors
    await pubsub.subscribe(f"peer:{data.peer_id.hex()}")

    try:
        task = asyncio.create_task(listen_pubsub())

        while True:
            if data.event == EVENT_NAMES.STOP:
                await websocket.close(1000, "Server is received `stop` event")
                break

            response = {"action": data.action}
            if not data.peer_id:
                raise ValueError("WEBSOCKET: `peer_id` is required for saving to redis")

            redis_storage = RedisDatastructure(
                info_hash=data.info_hash,
                type="websocket",
                peer_id=data.peer_id.hex(),
                peer_ip=data.ip,
                port=data.port,
                left=int(data.left) if data.left is not None else None,
            )
            await redis_storage.save()

            seeders = leechers = MutableBox[int](0)

            random_peer_keys = await zrandmember(
                hash_key=data.info_hash,
                numwant=data.numwant,
                namespace=REDIS_NAMESPACE_ENUM.WEBSOCKET,
            )
            peer_json_list = await hmget(
                hash_key=data.info_hash,
                fields=random_peer_keys,
                namespace=REDIS_NAMESPACE_ENUM.WEBSOCKET,
            )

            for peer in peer_json_list:
                if peer:
                    try:
                        with rollback_on_exception(seeders, leechers):
                            peer_info = RedisDatastructure(**json.loads(peer))
                            if peer_info.left == 0:
                                seeders.value += 1
                            else:
                                leechers.value += 1
                    except TypeError:
                        pass

            response |= {"completed": seeders.value, "incompleted": leechers.value}

            if data.action == ACTIONS.ANNOUNCE:
                response |= {
                    "info_hash": await hex_str_to_bin_str(data.info_hash),
                    "interval": WEBSOCKET_INTERVAL,
                }
                await websocket.send_json(response)

            if not data.answer:
                await websocket.send_json(response)

            # Handle offers by publishing to respective peers
            if offers := data.offers:
                for value in peer_json_list:
                    if value:
                        peer_info = RedisDatastructure(**json.loads(value))
                        for offer in offers:
                            message = json.dumps(
                                {
                                    "action": "announce",
                                    "offer": offer["offer"],
                                    "offer_id": offer["offer_id"],
                                    "peer_id": await bytes_to_bin_str(data.peer_id),
                                    "info_hash": await hex_str_to_bin_str(
                                        data.info_hash
                                    ),
                                }
                            )
                            await redis.publish(f"peer:{peer_info.peer_id}", message)

            # Handle answers by publishing to the target peer
            if data.answer:
                if not data.to_peer_id:
                    raise ValueError("WEBSOCKET: `to_peer_id` is required for answer")

                message = json.dumps(
                    {
                        "action": "announce",
                        "answer": data.answer,
                        "offer_id": data.offer_id,
                        "peer_id": await bytes_to_bin_str(data.peer_id),
                        "info_hash": await hex_str_to_bin_str(data.info_hash),
                    }
                )
                await redis.publish(f"peer:{data.to_peer_id.hex()}", message)

            # Log the event
            logging.info(
                f"Sent `Websocket` response for {data.info_hash}. Event: {data.event}."
            )

            # Wait for next message from client
            data: WebsocketDatastructure = await parse_websocket()

    except asyncio.CancelledError:
        logging.info(f"WebSocket disconneted for `{data.ip}:{data.port}`")
        raise
    finally:
        # Cleanup
        if task:
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task

        if pubsub:
            if not data.peer_id:
                raise ValueError(
                    "WEBSOCKET: `peer_id` is required for unsubscription from redis"
                )

            await pubsub.unsubscribe(f"peer:{data.peer_id.hex()}")
            await pubsub.close()
        await hdel(data.info_hash, data.addr, namespace=REDIS_NAMESPACE_ENUM.WEBSOCKET)
