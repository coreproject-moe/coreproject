"""Tests for constant values."""
from coreproject_tracker.constants import (
    ANNOUNCE_INTERVAL,
    ANNOUNCE_INTERVAL_MAX,
    ANNOUNCE_INTERVAL_MIN,
    CONNECTION_ID,
    DEFAULT_ANNOUNCE_PEERS,
    HASH_EXPIRE_TIME,
    MAX_ANNOUNCE_PEERS,
    PEER_TTL,
    WEBSOCKET_INTERVAL,
    WEBSOCKET_PEER_TTL,
)


def test_announce_interval():
    assert ANNOUNCE_INTERVAL == 600  # 10 minutes


def test_announce_interval_range():
    assert ANNOUNCE_INTERVAL_MIN < ANNOUNCE_INTERVAL < ANNOUNCE_INTERVAL_MAX


def test_peer_defaults():
    assert DEFAULT_ANNOUNCE_PEERS == 50
    assert MAX_ANNOUNCE_PEERS == 82


def test_connection_id():
    # BEP15 connection ID
    assert CONNECTION_ID == (0x417 << 32) | 0x27101980


def test_ttl_values():
    assert PEER_TTL == 3600  # 1 hour
    assert HASH_EXPIRE_TIME == 86400  # 24 hours
    assert WEBSOCKET_PEER_TTL == 60  # 1 minute
    assert WEBSOCKET_INTERVAL == 30  # 30 seconds
