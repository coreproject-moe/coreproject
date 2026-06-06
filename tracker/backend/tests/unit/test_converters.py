"""Tests for converter functions."""
import pytest
from coreproject_tracker.converters import (
    convert_binary_string_to_bytes,
    convert_ip,
    convert_str_int_to_float,
    convert_to_url_bytes,
)


def test_convert_binary_string_to_bytes():
    assert convert_binary_string_to_bytes("hello") == b"hello"
    assert convert_binary_string_to_bytes("") == b""
    assert convert_binary_string_to_bytes(None) is None


def test_convert_ip_valid():
    assert convert_ip("192.168.1.1") == "192.168.1.1"
    assert convert_ip("10.0.0.1") == "10.0.0.1"


def test_convert_ip_invalid():
    with pytest.raises(ValueError):
        convert_ip("bad-ip")


def test_convert_str_int_to_float():
    assert convert_str_int_to_float("100") == 100.0
    assert convert_str_int_to_float(50) == 50.0
    assert convert_str_int_to_float(None) is None


def test_convert_to_url_bytes():
    assert convert_to_url_bytes("%00%01%02") == b"\x00\x01\x02"
    assert convert_to_url_bytes("hello") == b"hello"
