"""Tests for coreproject_tracker.functions.ip - IP utilities."""
import pytest
from coreproject_tracker.enums import IP
from coreproject_tracker.functions import (
    addr_to_ip_port,
    addrs_to_compact,
    check_ip_type,
    convert_ipv4_coded_ipv6_to_ipv4,
    convert_str_to_ip_object,
)


def test_convert_str_to_ip_object_valid_ipv4():
    result = convert_str_to_ip_object("192.168.1.1")
    assert result is not False
    assert str(result) == "192.168.1.1"


def test_convert_str_to_ip_object_valid_ipv6():
    result = convert_str_to_ip_object("2001:db8::1")
    assert result is not False
    assert str(result) == "2001:db8::1"


def test_convert_str_to_ip_object_bracketed_ipv6():
    result = convert_str_to_ip_object("[2001:db8::1]")
    assert result is not False
    assert str(result) == "2001:db8::1"


def test_convert_str_to_ip_object_invalid():
    assert convert_str_to_ip_object("not-an-ip") is False


def test_convert_str_to_ip_object_empty():
    assert convert_str_to_ip_object("") is False


def test_convert_str_to_ip_object_oversized_octet():
    assert convert_str_to_ip_object("256.256.256.256") is False


def test_addr_to_ip_port_ipv4():
    ip, port = addr_to_ip_port("192.168.1.1:8080")
    assert ip == "192.168.1.1"
    assert port == 8080


def test_addr_to_ip_port_ipv6_bracketed():
    ip, port = addr_to_ip_port("[::1]:443")
    assert ip == "[::1]"
    assert port == 443


def test_addr_to_ip_port_plain_ipv6():
    ip, port = addr_to_ip_port("::1:80")
    assert ip == "::1"
    assert port == 80


def test_addr_to_ip_port_invalid_format():
    with pytest.raises(ValueError, match="Invalid address format"):
        addr_to_ip_port("192.168.1.1")


def test_addr_to_ip_port_non_string():
    with pytest.raises(ValueError, match="must be a string"):
        addr_to_ip_port(12345)  # type: ignore


def test_addrs_to_compact_single_ipv4():
    compact = addrs_to_compact(["192.168.1.1:8080"])
    assert len(compact) == 6


def test_addrs_to_compact_multiple():
    compact = addrs_to_compact(["10.0.0.1:1000", "10.0.0.2:2000"])
    assert len(compact) == 12


def test_addrs_to_compact_string_input():
    compact = addrs_to_compact("10.0.0.1:1000")
    assert len(compact) == 6


def test_addrs_to_compact_empty_list():
    compact = addrs_to_compact([])
    assert compact == b""


def test_addrs_to_compact_structure():
    import struct
    compact = addrs_to_compact("192.168.1.1:80")
    assert compact[:4] == b"\xc0\xa8\x01\x01"
    assert struct.unpack("!H", compact[4:])[0] == 80


def test_convert_ipv4_coded_ipv6_plain_ipv4():
    result = convert_ipv4_coded_ipv6_to_ipv4("192.168.1.1")
    assert result is None


def test_convert_ipv4_coded_ipv6_mapped():
    result = convert_ipv4_coded_ipv6_to_ipv4("::ffff:c0a8:101")
    assert result == "192.168.1.1"


def test_convert_ipv4_coded_ipv6_invalid():
    assert convert_ipv4_coded_ipv6_to_ipv4("not-an-ip") is False


def test_convert_ipv4_coded_ipv6_plain_ipv6():
    result = convert_ipv4_coded_ipv6_to_ipv4("2001:db8::1")
    assert result is None


def test_check_ip_type_ipv4():
    assert check_ip_type("192.168.1.1") == IP.IPV4


def test_check_ip_type_ipv6():
    assert check_ip_type("2001:db8::1") == IP.IPV6


def test_check_ip_type_invalid():
    assert check_ip_type("not-an-ip") is False


def test_check_ip_type_bracketed_ipv6():
    assert check_ip_type("[2001:db8::1]") == IP.IPV6
