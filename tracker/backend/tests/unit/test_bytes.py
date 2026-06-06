"""Tests for uint conversion functions."""
from coreproject_tracker.functions import from_uint16, from_uint32, from_uint64, to_uint32


def test_to_uint32_zero():
    assert to_uint32(0) == b"\x00\x00\x00\x00"


def test_to_uint32_one():
    assert to_uint32(1) == b"\x00\x00\x00\x01"


def test_to_uint32_max():
    assert to_uint32(0xFFFFFFFF) == b"\xFF\xFF\xFF\xFF"


def test_to_uint32_typical():
    assert to_uint32(65535) == b"\x00\x00\xFF\xFF"


def test_to_uint32_type_and_length():
    result = to_uint32(42)
    assert isinstance(result, bytes) and len(result) == 4


def test_from_uint16_values():
    assert from_uint16(b"\x00\x00") == 0
    assert from_uint16(b"\x00\x01") == 1
    assert from_uint16(b"\xFF\xFF") == 65535


def test_from_uint16_roundtrip():
    assert from_uint16((5000).to_bytes(2, "big")) == 5000


def test_from_uint32_values():
    assert from_uint32(b"\x00\x00\x00\x00") == 0
    assert from_uint32(b"\x00\x00\x00\x01") == 1
    assert from_uint32(b"\xFF\xFF\xFF\xFF") == 0xFFFFFFFF


def test_from_uint32_roundtrip():
    assert from_uint32(to_uint32(12345)) == 12345


def test_from_uint64_values():
    assert from_uint64(b"\x00" * 8) == 0
    assert from_uint64(b"\x00\x00\x00\x00\x00\x00\x00\x01") == 1
    assert from_uint64(b"\xFF" * 8) == 0xFFFFFFFFFFFFFFFF


def test_from_uint64_typical():
    assert from_uint64((1_000_000).to_bytes(8, "big")) == 1_000_000
