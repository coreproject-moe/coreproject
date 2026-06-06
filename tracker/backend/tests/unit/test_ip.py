"""Tests for IP utility functions."""
import pytest
import struct
from coreproject_tracker.enums import IP
from coreproject_tracker.functions import (
    addr_to_ip_port,
    addrs_to_compact,
    check_ip_type,
    convert_ipv4_coded_ipv6_to_ipv4,
    convert_str_to_ip_object,
)


def test_convert_str_to_ip_valid():
    assert convert_str_to_ip_object("192.168.1.1") is not False
    assert convert_str_to_ip_object("2001:db8::1") is not False
    assert convert_str_to_ip_object("[2001:db8::1]") is not False


def test_convert_str_to_ip_invalid():
    assert convert_str_to_ip_object("not-an-ip") is False
    assert convert_str_to_ip_object("") is False
    assert convert_str_to_ip_object("256.256.256.256") is False


def test_addr_to_ip_port():
    ip, port = addr_to_ip_port("192.168.1.1:8080")
    assert ip == "192.168.1.1" and port == 8080


def test_addr_to_ip_port_invalid():
    with pytest.raises(ValueError):
        addr_to_ip_port("192.168.1.1")
    with pytest.raises(ValueError):
        addr_to_ip_port(12345)  # type: ignore


def test_addrs_to_compact():
    assert len(addrs_to_compact(["192.168.1.1:8080"])) == 6
    assert len(addrs_to_compact(["10.0.0.1:1000", "10.0.0.2:2000"])) == 12
    assert addrs_to_compact([]) == b""
    assert len(addrs_to_compact("10.0.0.1:1000")) == 6


def test_addrs_to_compact_structure():
    compact = addrs_to_compact("192.168.1.1:80")
    assert compact[:4] == b"\xc0\xa8\x01\x01"
    assert struct.unpack("!H", compact[4:])[0] == 80


def test_convert_ipv4_mapped():
    assert convert_ipv4_coded_ipv6_to_ipv4("192.168.1.1") is None
    assert convert_ipv4_coded_ipv6_to_ipv4("::ffff:c0a8:101") == "192.168.1.1"
    assert convert_ipv4_coded_ipv6_to_ipv4("not-an-ip") is False


def test_check_ip_type():
    assert check_ip_type("192.168.1.1") == IP.IPV4
    assert check_ip_type("2001:db8::1") == IP.IPV6
    assert check_ip_type("not-an-ip") is False
    assert check_ip_type("[2001:db8::1]") == IP.IPV6
