"""Tests for environment variable configurations."""
import pytest
from coreproject_tracker.envs import (
    BLOCKLIST_PATH,
    RATE_LIMIT_REQUESTS,
    RATE_LIMIT_WINDOW,
    REDIS_DATABASE,
    REDIS_HOST,
    REDIS_PORT,
    REDIS_URI,
    WORKERS_COUNT,
)


def test_redis_defaults():
    assert REDIS_HOST == "localhost"
    assert REDIS_PORT == 6379
    assert REDIS_DATABASE == 0
    assert REDIS_URI.startswith("redis://")


def test_rate_limit_defaults():
    assert RATE_LIMIT_REQUESTS > 0
    assert RATE_LIMIT_WINDOW > 0


def test_workers_count():
    assert WORKERS_COUNT >= 2


def test_blocklist_path_type():
    assert isinstance(BLOCKLIST_PATH, (str, type(None)))
