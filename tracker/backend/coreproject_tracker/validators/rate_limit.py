import time

from coreproject_tracker.envs import RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW
from coreproject_tracker.singletons import get_redis


async def check_rate_limit(ip: str) -> bool:
    r = get_redis()
    key = f"rate_limit:{ip}"
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW

    pipe = await r.pipeline()
    await pipe.zremrangebyscore(key, 0, window_start)
    await pipe.zcard(key)
    await pipe.zadd(key, {str(now): now})
    await pipe.expire(key, RATE_LIMIT_WINDOW + 1)
    results = await pipe.execute()

    current_count = results[1]
    if current_count >= RATE_LIMIT_REQUESTS:
        return False
    return True