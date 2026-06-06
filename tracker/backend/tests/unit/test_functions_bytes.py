"""Tests for coreproject_tracker.functions.bytes - uint conversions."""
from coreproject_tracker.functions import from_uint16, from_uint32, from_uint64, to_uint32


def test_to_uint32_zero():
    assert to_uint32(0) == b"\x00\x00\x00\x00"


def test_to_uint32_one():
    assert to_uint32(1) == b"\x00\x00\x00\x01"


def test_to_uint32_max():
    assert to_uint32(0xFFFFFFFF) == b"\xFF\xFF\xFF\xFF"


def test_to_uint32_typical():
    assert to_uint32(65535) == b"\x00\x00\xFF\xFF"


def test_to_uint32_returns_bytes():
    assert isinstance(to_uint32(42), bytes)


def test_to_uint32_length_four():
    assert len(to_uint32(123)) == 4


def test_from_uint16_zero():
    assert from_uint16(b"\x00\x00") == 0


def test_from_uint16_one():
    assert from_uint16(b"\x00\x01") == 1


def test_from_uint16_max():
    assert from_uint16(b"\xFF\xFF") == 65535


def test_from_uint16_typical_port():
    assert from_uint16(b"\x1A\xB1") == 6833


def test_from_uint16_roundtrip():
    original = 5000
    packed = original.to_bytes(2, "big")
    assert from_uint16(packed) == original


def test_from_uint32_zero():
    assert from_uint32(b"\x00\x00\x00\x00") == 0


def test_from_uint32_one():
    assert from_uint32(b"\x00\x00\x00\x01") == 1


def test_from_uint32_max():
    assert from_uint32(b"\xFF\xFF\xFF\xFF") == 0xFFFFFFFF


def test_from_uint32_roundtrip():
    original = 12345
    packed = to_uint32(original)
    assert from_uint32(packed) == original


def test_from_uint32_connection_id_range():
    from coreproject_tracker.constants import CONNECTION_ID
    packed = to_uint32(CONNECTION_ID >> 32)
    assert from_uint32(packed) == (CONNECTION_ID >> 32)


def test_from_uint64_zero():
    assert from_uint64(b"\x00" * 8) == 0


def test_from_uint64_one():
    assert from_uint64(b"\x00\x00\x00\x00\x00\x00\x00\x01") == 1


def test_from_uint64_max():
    assert from_uint64(b"\xFF" * 8) == 0xFFFFFFFFFFFFFFFF


def test_from_uint64_typical_download():
    data = (1_000_000).to_bytes(8, "big")
    assert from_uint64(data) == 1_000_000
