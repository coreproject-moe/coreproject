import asyncio
import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import redis.asyncio

# Ensure the backend package is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# ---------------------------------------------------------------------------
# Test data factories
# ---------------------------------------------------------------------------

def make_info_hash(length: int = 20) -> bytes:
    """Create a valid info_hash of the given length (default SHA-1: 20 bytes)."""
    return bytes(range(length))


def make_peer_id() -> str:
    """Create a valid 20-byte peer_id as latin-1 string."""
    return "-".join([f"{i:02x}" for i in range(20)])


def make_valid_ipv4() -> str:
    return "192.168.1.1"


def make_valid_ipv6() -> str:
    return "2001:db8::1"


# ---------------------------------------------------------------------------
# Redis fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def redis_uri():
    """Redis URI for testing - uses localhost:6379 or env override."""
    return os.environ.get("REDIS_URI", "redis://localhost:6379/0")


@pytest.fixture
async def redis_connection(redis_uri):
    """Real Redis connection for integration tests. Skipped if Redis unavailable."""
    try:
        r = redis.asyncio.from_url(redis_uri)
        await r.ping()
        await r.flushdb()
        yield r
        await r.flushdb()
        await r.aclose()
    except ConnectionError:
        pytest.skip("Redis not available for integration tests")


@pytest.fixture
def mock_redis():
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
def mock_redis_pipeline(mock_redis):
    """Mock Redis pipeline."""
    pipeline = AsyncMock()
    pipeline.execute = AsyncMock(return_value=[0, 0, 0, 0, 0])
    mock_redis.pipeline.return_value = pipeline
    return pipeline


# ---------------------------------------------------------------------------
# Redis singleton patching
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def reset_redis_singleton():
    """Ensure Redis singleton is clean between tests."""
    from coreproject_tracker.singletons.redis import RedisHandler
    RedisHandler._connection = None
    yield
    RedisHandler._connection = None


# ---------------------------------------------------------------------------
# GeoIP fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_geoip_available():
    """Mock GeoIP as unavailable (no database)."""
    with patch("coreproject_tracker.geo._geo_available", False):
        with patch("coreproject_tracker.geo._geo_reader", None):
            yield


@pytest.fixture
def mock_geoip_reader():
    """Mock GeoIP reader that returns country codes."""
    mock_reader = MagicMock()
    mock_response = MagicMock()
    mock_response.country.iso_code = "US"
    mock_reader.country.return_value = mock_response
    mock_reader.close = MagicMock()
    return mock_reader


# ---------------------------------------------------------------------------
# Blocklist fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def temp_blocklist_file(tmp_path):
    """Create a temporary blocklist file."""
    blocklist = tmp_path / "blocklist.txt"
    blocklist.write_text("10.0.0.0/8\n172.16.0.0/12\n# comment\n\n192.168.1.100\n")
    return str(blocklist)


# ---------------------------------------------------------------------------
# Quart app fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
async def quart_app(mock_redis, mock_geoip_available, redis_uri):
    """Create a Quart test app with mocked Redis."""
    from coreproject_tracker.app import make_app

    with patch("coreproject_tracker.singletons.redis.RedisHandler._connection", mock_redis):
        app = make_app()
        yield app


@pytest.fixture
async def quart_test_client(quart_app):
    """Quart test client for HTTP endpoint testing."""
    async with quart_app.test_app():
        client = quart_app.test_client()
        yield client


@pytest.fixture
async def live_quart_app(redis_connection, mock_geoip_available):
    """Create a Quart test app with real Redis for integration tests."""
    from coreproject_tracker.app import make_app
    from coreproject_tracker.singletons.redis import RedisHandler

    RedisHandler._connection = redis_connection
    app = make_app()
    async with app.test_app():
        yield app
    RedisHandler._connection = None


@pytest.fixture
async def live_quart_test_client(live_quart_app):
    """Quart test client with real Redis for integration tests."""
    async with live_quart_app.test_app():
        client = live_quart_app.test_client()
        yield client


# ---------------------------------------------------------------------------
# UDP server fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def connection_id_bytes():
    """The expected CONNECTION_ID as 8 bytes."""
    from coreproject_tracker.constants import CONNECTION_ID
    return CONNECTION_ID.to_bytes(8, "big")


@pytest.fixture
def sample_udp_connect_packet(connection_id_bytes):
    """A valid UDP CONNECT request packet."""
    import struct
    return b"".join([
        connection_id_bytes,
        struct.pack(">I", 0),       # action: CONNECT
        struct.pack(">I", 12345),   # transaction_id
    ])


@pytest.fixture
def sample_udp_announce_packet(connection_id_bytes):
    """A valid UDP ANNOUNCE request packet (98 bytes)."""
    import struct
    info_hash = make_info_hash()
    peer_id = bytes(range(20))
    return b"".join([
        connection_id_bytes,        # 0-7: connection_id
        struct.pack(">I", 1),       # 8-11: action ANNOUNCE
        struct.pack(">I", 54321),   # 12-15: transaction_id
        info_hash,                  # 16-35: info_hash
        peer_id,                    # 36-55: peer_id
        struct.pack(">Q", 0),       # 56-63: downloaded
        struct.pack(">Q", 1000),    # 64-71: left
        struct.pack(">Q", 500),     # 72-79: uploaded
        struct.pack(">I", 0),       # 80-83: event (0=started)
        struct.pack(">I", 0),       # 84-87: ip (0=fill from sender)
        struct.pack(">I", 1),       # 88-91: key
        struct.pack(">I", 50),      # 92-95: numwant
        struct.pack(">H", 6881),    # 96-97: port
    ])


@pytest.fixture
def sample_udp_scrape_packet(connection_id_bytes):
    """A valid UDP SCRAPE request packet."""
    import struct
    info_hash = make_info_hash()
    return b"".join([
        connection_id_bytes,        # 0-7: connection_id
        struct.pack(">I", 2),       # 8-11: action SCRAPE
        struct.pack(">I", 99999),   # 12-15: transaction_id
        info_hash,                  # 16-35: info_hash
    ])


# ---------------------------------------------------------------------------
# WebSocket fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def ws_announce_message():
    """A valid WebSocket announce message."""
    return {
        "info_hash": "a" * 40,  # hex-encoded 20 bytes
        "action": "announce",
        "peer_id": "b" * 40,    # hex-encoded 20 bytes
        "ip": "192.168.1.1",
        "port": 6881,
        "addr": "192.168.1.1:6881",
        "numwant": 50,
        "left": 1000,
        "uploaded": 500,
    }


# ---------------------------------------------------------------------------
# Environment fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def tracker_env():
    """Set tracker environment variables for testing."""
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
    # Restore
    for key in env:
        os.environ.pop(key, None)
    os.environ.update(old)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

@pytest.fixture
def bencode():
    """bencodepy encode/decode helpers."""
    import bencodepy
    return {"encode": bencodepy.bencode, "decode": bencodepy.bdecode}
