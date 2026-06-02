import asyncio
import logging as logger
from typing import Optional

from redis.asyncio import Redis, RedisError, from_url

from coreproject_tracker.exceptions import RedisNotInitialized


class RedisHandler:
    _connection: Optional[Redis] = None

    def __init__(self, redis_uri, connection_attempts=3):
        """
        :param app: the quart app, defaults to None
        :param redis_uri: the redis connection URI
        """
        self.redis_uri = redis_uri
        self.connection_attempts = connection_attempts

    @staticmethod
    async def __attempt_to_connect(conn: Redis, attempts: int):
        for attempt in range(1, attempts + 1):
            try:
                await conn.ping()  # pyrefly: ignore[not-async]
                logger.debug("Redis connection established")
                break
            except RedisError:
                logger.warning(
                    f"Redis connection attempt {attempt} of {attempts} failed"
                )
                if attempt == attempts:
                    logger.critical("Redis connection failed")
                    raise
                await asyncio.sleep(2)

    # Start method
    async def init_redis(self, **kwargs) -> None:
        RedisHandler._connection = from_url(self.redis_uri, **kwargs)
        if self.connection_attempts >= 0:
            await self.__attempt_to_connect(
                RedisHandler._connection,
                self.connection_attempts,
            )
        logger.info("Redis started")

    # End method
    async def close_redis(self) -> None:
        if RedisHandler._connection is not None:
            await RedisHandler._connection.aclose()
            logger.info("Redis shutdown")

    @classmethod
    def get_connection(cls) -> Redis:
        """
        get the shared redis connection

            :raises RedisNotInitialized: if redis has not been initialized
        """
        if cls._connection is None:
            raise RedisNotInitialized("Redis has not been initialized")
        return cls._connection


def get_redis() -> Redis:
    """
    get the shared redis connection

        :raises RedisNotInitialized: if redis has not been initialized
    """
    return RedisHandler.get_connection()
