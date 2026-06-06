"""Tests for bytes/hex conversion functions."""
import pytest
from coreproject_tracker.functions import bytes_to_bin_str, hex_str_to_bin_str


def test_bytes_to_bin_str():
    assert bytes_to_bin_str(b"hello") == "hello"
    assert bytes_to_bin_str(b"") == ""
    assert len(bytes_to_bin_str(bytes(range(256)))) == 256


def test_bytes_to_bin_str_roundtrip():
    original = "test-peer-id"
    assert bytes_to_bin_str(original.encode("latin-1")) == original


def test_hex_str_to_bin_str():
    assert hex_str_to_bin_str("48656c6c6f") == "Hello"
    assert hex_str_to_bin_str("") == ""
    assert len(hex_str_to_bin_str("a" * 40)) == 20


def test_hex_str_to_bin_str_errors():
    with pytest.raises(ValueError):
        hex_str_to_bin_str("abc")
    with pytest.raises(ValueError):
        hex_str_to_bin_str("ZZZZ")
