"""Tests for validator functions."""
import pytest
from coreproject_tracker.constants import CONNECTION_ID
from coreproject_tracker.validators import (
    _load_blocklist,
    is_blocked,
    validate_connection_id,
    validate_ip,
    validate_info_hash_length,
    validate_peer_length,
    validate_port,
)


class _Dummy:
    def __init__(self, val):
        self.val = val


class _Attr:
    name = "test"


def test_validate_ip_ok():
    validate_ip(_Dummy("192.168.1.1"), _Attr(), "192.168.1.1")
    validate_ip(_Dummy("10.0.0.1"), _Attr(), "10.0.0.1")


def test_validate_ip_bad():
    with pytest.raises(ValueError):
        validate_ip(_Dummy("bad"), _Attr(), "bad")


def test_validate_port_ok():
    validate_port(_Dummy(80), _Attr(), 80)
    validate_port(_Dummy(65534), _Attr(), 65534)


def test_validate_port_bad():
    with pytest.raises(ValueError):
        validate_port(_Dummy(0), _Attr(), 0)
    with pytest.raises(ValueError):
        validate_port(_Dummy(65535), _Attr(), 65535)
    with pytest.raises(ValueError):
        validate_port(_Dummy(-1), _Attr(), -1)


def test_validate_info_hash_length_ok():
    validate_info_hash_length(_Dummy(bytes(20)), _Attr(), bytes(20))
    validate_info_hash_length(_Dummy(bytes(32)), _Attr(), bytes(32))


def test_validate_info_hash_length_bad():
    with pytest.raises(ValueError):
        validate_info_hash_length(_Dummy(bytes(10)), _Attr(), bytes(10))


def test_validate_connection_id_ok():
    validate_connection_id(
        _Dummy(CONNECTION_ID.to_bytes(8, "big")),
        _Attr(),
        CONNECTION_ID.to_bytes(8, "big"),
    )


def test_validate_connection_id_bad():
    with pytest.raises(ValueError):
        validate_connection_id(_Dummy(b"\x00" * 8), _Attr(), b"\x00" * 8)


def test_validate_peer_length_ok():
    validate_peer_length(_Dummy("a" * 20), _Attr(), "a" * 20)


def test_validate_peer_length_bad():
    with pytest.raises(ValueError):
        validate_peer_length(_Dummy("short"), _Attr(), "short")


def test_blocklist_load_and_check(tmp_path):
    blocklist_file = tmp_path / "blocks.txt"
    blocklist_file.write_text("10.0.0.0/8\n172.16.0.0/12\n# comment\n\n192.168.1.100\n")
    _load_blocklist(str(blocklist_file))
    assert is_blocked("10.0.0.1") is True
    assert is_blocked("172.16.0.1") is True
    assert is_blocked("192.168.1.100") is True
    assert is_blocked("8.8.8.8") is False


def test_blocklist_empty():
    # After loading empty, should return False for all
    _load_blocklist("/nonexistent/path/file.txt")
    assert is_blocked("any.ip.addr.ess") is False
