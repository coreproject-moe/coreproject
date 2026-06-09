"""Tests for Redis singleton and exceptions."""
import pytest
from coreproject_tracker.exceptions import RedisNotInitialized
from coreproject_tracker.singletons.redis import RedisHandler, get_redis


def test_redis_not_initialized():
    handler = RedisHandler("redis://localhost:6379/0")
    with pytest.raises(RedisNotInitialized):
        handler.get_connection()


def test_redis_handler_uri():
    handler = RedisHandler("redis://test:1234/5")
    assert handler.redis_uri == "redis://test:1234/5"
    assert handler.connection_attempts == 3


def test_get_redis_raises_when_empty():
    from coreproject_tracker.singletons.redis import RedisHandler
    RedisHandler._connection = None
    with pytest.raises(RedisNotInitialized):
        get_redis()
