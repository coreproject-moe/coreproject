"""Pytest configuration and shared fixtures."""

import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import redis.asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


# ---------------------------------------------------------------------------
# Test data helpers
# ---------------------------------------------------------------------------


def test_info_hash_bytes(length: int = 20) -> bytes:
    """Create valid info_hash bytes (SHA-1: 20 bytes, SHA-256: 32 bytes)."""
    return bytes(range(length))


def test_peer_id_string() -> str:
    """Create a valid 20-char peer_id."""
    return "-".join(f"{i:02x}" for i in range(20))


# ---------------------------------------------------------------------------
# Redis fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def redis_connection_uri():
    return os.environ.get("REDIS_URI", "redis://localhost:6379/0")


@pytest.fixture
async def real_redis(redis_connection_uri):
    """Real Redis for integration tests. Skips if unavailable."""
    try:
        client = redis.asyncio.from_url(redis_connection_uri)
        await client.ping()
        await client.flushdb()
        yield client
        await client.flushdb()
        await client.aclose()
    except ConnectionError:
        pytest.skip("Redis not available")


@pytest.fixture
def fake_redis():
    """Mock Redis async client for unit tests."""
    mock = AsyncMock(spec=redis.asyncio.Redis)
    mock.ping.return_value = True
    mock.info.return_value = {"redis_version": "7.4.2"}
    mock.hgetall.return_value = {}
    mock.hmget.return_value = []
    mock.zrandmember.return_value = []
    mock.zcard.return_value = 0
    mock.scan.return_value = [0, []]
    mock.get.return_value = None
    mock.type.return_value = b"hash"
    return mock


@pytest.fixture
def fake_redis_pipe(fake_redis):
    pipe = AsyncMock()
    pipe.execute = AsyncMock(return_value=[0, 0, 0, 0, 0])
    fake_redis.pipeline.return_value = pipe
    return pipe


@pytest.fixture(autouse=True)
def clear_redis_singleton():
    """Reset Redis singleton between tests."""
    from coreproject_tracker.singletons.redis import RedisHandler
    RedisHandler._connection = None
    yield
    RedisHandler._connection = None


# ---------------------------------------------------------------------------
# Geo fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def disable_geoip():
    """Mock geo as unavailable (no CSV loaded)."""
    with patch("coreproject_tracker.geo._geo_loaded", False):
        with patch("coreproject_tracker.geo._geo_loading", False):
            yield


@pytest.fixture
def enable_geoip():
    """Mock geo as available."""
    with patch("coreproject_tracker.geo._geo_loaded", True):
        yield


# ---------------------------------------------------------------------------
# Quart app fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
async def test_app(fake_redis, disable_geoip):
    """Quart test app with mocked Redis."""
    from coreproject_tracker.app import create_quart_app
    from coreproject_tracker.singletons.redis import RedisHandler

    with patch.object(RedisHandler, "_connection", fake_redis):
        app = create_quart_app()
        yield app


@pytest.fixture
async def http_client(test_app):
    """Test client for HTTP endpoints."""
    async with test_app.test_app():
        client = test_app.test_client()
        yield client


@pytest.fixture
async def live_test_app(real_redis, disable_geoip):
    """Quart test app with real Redis."""
    from coreproject_tracker.app import create_quart_app
    from coreproject_tracker.singletons.redis import RedisHandler

    RedisHandler._connection = real_redis
    app = create_quart_app()
    async with app.test_app():
        yield app
    RedisHandler._connection = None


@pytest.fixture
async def live_http_client(live_test_app):
    """Test client with real Redis."""
    async with live_test_app.test_app():
        client = live_test_app.test_client()
        yield client


# ---------------------------------------------------------------------------
# UDP packet fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def udp_connection_id():
    from coreproject_tracker.constants import CONNECTION_ID
    return CONNECTION_ID.to_bytes(8, "big")


@pytest.fixture
def udp_connect_packet(udp_connection_id):
    import struct
    return udp_connection_id + struct.pack(">I", 0) + struct.pack(">I", 12345)


@pytest.fixture
def udp_announce_packet(udp_connection_id):
    import struct
    ih = test_info_hash_bytes()
    pid = bytes(range(20))
    return (
        udp_connection_id
        + struct.pack(">I", 1)
        + struct.pack(">I", 54321)
        + ih
        + pid
        + struct.pack(">Q", 0)
        + struct.pack(">Q", 1000)
        + struct.pack(">Q", 500)
        + struct.pack(">I", 0)
        + struct.pack(">I", 0)
        + struct.pack(">I", 1)
        + struct.pack(">I", 50)
        + struct.pack(">H", 6881)
    )


@pytest.fixture
def udp_scrape_packet(udp_connection_id):
    import struct
    ih = test_info_hash_bytes()
    return udp_connection_id + struct.pack(">I", 2) + struct.pack(">I", 99999) + ih


# ---------------------------------------------------------------------------
# Environment fixture
# ---------------------------------------------------------------------------


@pytest.fixture
def tracker_env_vars():
    env = {
        "REDIS_HOST": "localhost",
        "REDIS_PORT": "6379",
        "REDIS_DATABASE": "0",
        "HOST": "127.0.0.1",
        "PORT": "5000",
        "WORKERS_COUNT": "1",
    }
    old = dict(os.environ)
    os.environ.update(env)
    yield env
    for key in env:
        os.environ.pop(key, None)
    os.environ.update(old)


# ---------------------------------------------------------------------------
# bencode helper
# ---------------------------------------------------------------------------


@pytest.fixture
def bencode_tools():
    import bencodepy
    return {"encode": bencodepy.bencode, "decode": bencodepy.bdecode}
