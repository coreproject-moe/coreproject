from attrs import asdict, define, field, validators
from quart import json

from coreproject_tracker.bep.announce_lifecycle import (
    AnnounceEvent,
    AnnounceState,
    next_announce_event,
)
from coreproject_tracker.constants import PEER_TTL, WEBSOCKET_PEER_TTL
from coreproject_tracker.converters import convert_str_int_to_float
from coreproject_tracker.enums import REDIS_NAMESPACE_ENUM
from coreproject_tracker.functions import (
    calculate_weight,
    hset,
    save_peer_pipeline,
    zadd,
)
from coreproject_tracker.validators import validate_ip, validate_port


@define
class RedisDatastructure:
    info_hash: str = field(
        validator=validators.instance_of(str), metadata={"asdict": False}
    )
    type: str = field(validator=validators.instance_of(str))
    peer_id: str = field(validator=validators.instance_of(str))
    peer_ip: str = field(validator=[validate_ip])
    port: int = field(converter=int, validator=[validate_port])
    left: float | None = field(converter=convert_str_int_to_float)
    downloaded: int = field(default=0)
    uploaded: int = field(default=0)
    country: str | None = field(default=None)

    async def save(self) -> None:
        match self.type:
            case "websocket":
                expire_time = WEBSOCKET_PEER_TTL
                redis_namespace = REDIS_NAMESPACE_ENUM.WEBSOCKET
            case "http" | "udp":
                expire_time = PEER_TTL
                redis_namespace = REDIS_NAMESPACE_ENUM.HTTP_UDP
            case _:
                raise ValueError(f"{self.type} is not a valid type")

        peer_key = f"{self.peer_ip}:{self.port}"
        peer_json = json.dumps(asdict(self, recurse=True))

        await save_peer_pipeline(
            self.info_hash,
            peer_key,
            peer_json,
            calculate_weight(self),
            expire_time,
            redis_namespace,
        )

        # Track announce lifecycle state
        await _update_announce_state(self.info_hash, peer_key, redis_namespace)


async def _update_announce_state(
    info_hash: str, peer_key: str, namespace: REDIS_NAMESPACE_ENUM
) -> None:
    """Update announce lifecycle state for a peer in Redis.

    Tracks that the peer successfully announced, updating the timestamp
    and event state for interval enforcement.
    """
    from coreproject_tracker.singletons import get_redis

    r = get_redis()
    state_key = f"{namespace.value}:{info_hash}:announce:{peer_key}"

    # Load existing state
    raw_state = await r.hgetall(state_key)
    if raw_state:
        state = AnnounceState(
            last_event=AnnounceEvent(int(raw_state.get(b"last_event", 0))),
            interval=int(raw_state.get(b"interval", 1800)),
            num_peers=int(raw_state.get(b"num_peers", 0)),
            announced=True,
        )
    else:
        state = AnnounceState(announced=False)

    # Compute next event
    result = next_announce_event(state, torrent_active=True)
    state.announced = True
    state.last_event = result.event
    state.last_ok_time = __import__("datetime").datetime.now(
        __import__("datetime").timezone.utc
    )

    # Persist state
    await r.hset(state_key, mapping={
        "last_event": str(state.last_event),
        "interval": str(state.interval),
        "num_peers": str(state.num_peers),
        "announced": "1",
    })
    await r.expire(state_key, PEER_TTL)