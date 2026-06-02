import json
import time

from quart import json as quart_json

from coreproject_tracker.constants import HASH_EXPIRE_TIME
from coreproject_tracker.enums import REDIS_NAMESPACE_ENUM
from coreproject_tracker.singletons import get_redis


def _ns_key(namespace: REDIS_NAMESPACE_ENUM, key: str) -> str:
    return f"{namespace.value}:{key}"


def _ns_key_z(namespace: REDIS_NAMESPACE_ENUM, key: str) -> str:
    return f"{_ns_key(namespace, key)}:zset"


async def hset(
    hash_key: str,
    field: str,
    value: str,
    expire_time: int,
    namespace: REDIS_NAMESPACE_ENUM,
) -> None:
    r = get_redis()
    namespaced_key = _ns_key(namespace, hash_key)

    expiration = int(time.time() + expire_time)
    await r.hset(namespaced_key, field, value)  # type: ignore[no-untyped-call]
    await r.hexpireat(namespaced_key, expiration, field)
    await r.expire(namespaced_key, HASH_EXPIRE_TIME)


async def hgetall(
    hash_key: str,
    namespace: REDIS_NAMESPACE_ENUM,
) -> None | dict[str, str]:
    r = get_redis()
    namespaced_key = _ns_key(namespace, hash_key)

    data = await r.hgetall(namespaced_key)  # type: ignore[no-untyped-call]
    if not data:
        return None

    await r.expire(namespaced_key, HASH_EXPIRE_TIME)

    valid_fields = {}
    for field, value in data.items():
        try:
            decoded = quart_json.loads(value)
        except json.JSONDecodeError:
            continue
        if isinstance(decoded, dict):
            valid_fields[field] = value

    return valid_fields


async def hmget(
    hash_key: str,
    fields: list[str],
    namespace: REDIS_NAMESPACE_ENUM,
) -> list[str | None]:
    if not fields:
        return []

    r = get_redis()
    namespaced_key = _ns_key(namespace, hash_key)
    values = await r.hmget(namespaced_key, *fields)  # type: ignore[no-untyped-call]
    return values


async def hdel(
    hash_key: str,
    field_name: str,
    namespace: REDIS_NAMESPACE_ENUM,
) -> None:
    r = get_redis()
    namespaced_key = _ns_key(namespace, hash_key)
    namespaced_zkey = _ns_key_z(namespace, hash_key)
    pipe = await r.pipeline()
    await pipe.hdel(namespaced_key, field_name)  # type: ignore[no-untyped-call]
    await pipe.zrem(namespaced_zkey, field_name)
    await pipe.execute()


async def get_all_hash_keys():
    r = get_redis()
    cursor = 0
    hash_keys = []

    while True:
        cursor, keys = await r.scan(cursor, match="*", count=100_000)
        for key in keys:
            if await r.type(key) == b"hash":
                hash_keys.append(key)
        if cursor == 0:
            break

    return hash_keys


async def zadd(
    hash_key: str,
    field: str,
    weight: float,
    expire_time: int,
    namespace: REDIS_NAMESPACE_ENUM,
) -> None:
    r = get_redis()
    namespaced_key = _ns_key_z(namespace, hash_key)
    await r.zadd(namespaced_key, {field: weight})
    await r.expire(namespaced_key, expire_time)


async def save_peer_pipeline(
    hash_key: str,
    field: str,
    value: str,
    weight: float,
    expire_time: int,
    namespace: REDIS_NAMESPACE_ENUM,
) -> None:
    """Save hash field + zset member + TTLs in a single pipeline round-trip."""
    r = get_redis()
    namespaced_key = _ns_key(namespace, hash_key)
    namespaced_zkey = _ns_key_z(namespace, hash_key)
    expiration = int(time.time() + expire_time)

    pipe = await r.pipeline()
    await pipe.hset(namespaced_key, field, value)  # type: ignore[no-untyped-call]
    await pipe.hexpireat(namespaced_key, expiration, field)
    await pipe.expire(namespaced_key, HASH_EXPIRE_TIME)
    await pipe.zadd(namespaced_zkey, {field: weight})
    await pipe.expire(namespaced_zkey, expire_time)
    await pipe.execute()


async def zrandmember(
    hash_key: str,
    numwant: int,
    namespace: REDIS_NAMESPACE_ENUM,
) -> list[str]:
    r = get_redis()
    namespaced_key = _ns_key_z(namespace, hash_key)
    members = await r.zrandmember(namespaced_key, numwant, withscores=False)
    return members or []


async def zrem(
    hash_key: str,
    field: str,
    namespace: REDIS_NAMESPACE_ENUM,
) -> None:
    r = get_redis()
    namespaced_key = _ns_key_z(namespace, hash_key)
    await r.zrem(namespaced_key, field)


__all__ = [
    "hset", "hgetall", "hmget", "hdel",
    "zadd", "zrandmember", "zrem",
    "save_peer_pipeline", "get_all_hash_keys",
]