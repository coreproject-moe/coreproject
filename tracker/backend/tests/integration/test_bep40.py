"""BEP40 proximity cross-validation against Go reference values.

Clean room port from inspirations/torrent/bep40_test.go.
Verifies CRC32 Castagnoli peer priority matches anacrolix/torrent output.
"""

import pytest

from coreproject_tracker.bep.bep40 import (
    _crc32c,
    bep40_priority,
    bep40_priority_bytes,
)


pytestmark = pytest.mark.integration


class TestCrc32Castagnoli:
    def test_rfc4960_vector(self):
        crc = _crc32c(b"123456789")
        assert crc == 0xE3069283

    def test_empty_data(self):
        crc = _crc32c(b"")
        assert crc == 0x00000000

    def test_single_byte(self):
        crc = _crc32c(b"\x00")
        assert isinstance(crc, int)
        assert 0 <= crc <= 0xFFFFFFFF


class TestBep40PriorityReference:
    def test_different_first_16_bits(self):
        assert bep40_priority("123.213.32.10", "98.76.54.32") == 0xEC2D7224

    def test_commutativity(self):
        a = bep40_priority("123.213.32.10", "98.76.54.32")
        b = bep40_priority("98.76.54.32", "123.213.32.10")
        assert a == b

    def test_same_24_subnet(self):
        assert bep40_priority("123.213.32.10", "123.213.32.234") == 0x99568189

    def test_different_24_subnet(self):
        assert bep40_priority("206.248.98.111", "142.147.89.224") == 0x2B41D456

    def test_same_ip_zero_port(self):
        data = bep40_priority_bytes("123.213.32.234", "123.213.32.234", 0, 0)
        assert data == b"\x00\x00\x00\x00"

    def test_same_ip_different_ports(self):
        data = bep40_priority_bytes("10.0.0.1", "10.0.0.1", 6881, 8080)
        assert data == (6881).to_bytes(2, "big") + (8080).to_bytes(2, "big")

    def test_mixed_ip_version_raises(self):
        with pytest.raises(ValueError, match="incomparable"):
            bep40_priority("192.168.1.1", "2001:db8::1")

    def test_same_16_different_24_subnet(self):
        a = bep40_priority("192.168.1.1", "192.168.2.1")
        assert isinstance(a, int)
        assert 0 <= a <= 0xFFFFFFFF

    def test_ipv6_same_prefix(self):
        a = bep40_priority("2001:db8::1", "2001:db8::2")
        b = bep40_priority("2001:db8::2", "2001:db8::1")
        assert a == b
        assert isinstance(a, int)

    def test_ipv6_different_prefix(self):
        a = bep40_priority("2001:db8::1", "2001:db9::1")
        assert isinstance(a, int)
        assert 0 <= a <= 0xFFFFFFFF


class TestBep40NormalizedScore:
    def test_priority_normalized_to_range(self):
        normalized = (bep40_priority("10.0.0.1", "192.168.5.1") & 0xFFFFFFFF) / 0xFFFFFFFF * 10.0
        assert 0.0 <= normalized <= 10.0

    def test_same_ip_has_lowest_priority(self):
        same = bep40_priority("10.0.0.1", "10.0.0.1")
        assert same == 0  # CRC32C of 4 zero bytes

    def test_priority_is_deterministic(self):
        a = bep40_priority("1.2.3.4", "5.6.7.8")
        b = bep40_priority("1.2.3.4", "5.6.7.8")
        assert a == b
