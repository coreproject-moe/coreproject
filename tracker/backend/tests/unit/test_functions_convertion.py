"""Tests for coreproject_tracker.functions.convertion - bytes/hex conversions."""
import pytest
from coreproject_tracker.functions import bytes_to_bin_str, hex_str_to_bin_str


def test_bytes_to_bin_str_ascii():
    assert bytes_to_bin_str(b"hello") == "hello"


def test_bytes_to_bin_str_empty():
    assert bytes_to_bin_str(b"") == ""


def test_bytes_to_bin_str_latin1():
    result = bytes_to_bin_str(b"\xff\xfe")
    assert result == "\xff\xfe"
    assert len(result) == 2


def test_bytes_to_bin_str_full_range():
    data = bytes(range(256))
    result = bytes_to_bin_str(data)
    assert len(result) == 256


def test_bytes_to_bin_str_roundtrip():
    original = "test-peer-id"
    encoded = original.encode("latin-1")
    decoded = bytes_to_bin_str(encoded)
    assert decoded == original


def test_hex_str_to_bin_str_simple():
    result = hex_str_to_bin_str("48656c6c6f")
    assert result == "Hello"


def test_hex_str_to_bin_str_empty():
    result = hex_str_to_bin_str("")
    assert result == ""


def test_hex_str_to_bin_str_info_hash_length():
    hex_str = "a" * 40
    result = hex_str_to_bin_str(hex_str)
    assert len(result) == 20


def test_hex_str_to_bin_str_peer_id_length():
    hex_str = "b" * 40
    result = hex_str_to_bin_str(hex_str)
    assert len(result) == 20


def test_hex_str_to_bin_str_odd_length_raises():
    with pytest.raises(ValueError):
        hex_str_to_bin_str("abc")


def test_hex_str_to_bin_str_invalid_hex_raises():
    with pytest.raises(ValueError):
        hex_str_to_bin_str("ZZZZ")


def test_hex_str_to_bin_str_mixed_case():
    result = hex_str_to_bin_str("4F")
    assert result == "O"
