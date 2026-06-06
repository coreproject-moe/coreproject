"""Tests for coreproject_tracker.functions.convertion - bytes/hex conversions."""
import pytest
from coreproject_tracker.functions import bytes_to_bin_str, hex_str_to_bin_str


class TestBytesToBinStr:
    def test_ascii_bytes(self):
        assert bytes_to_bin_str(b"hello") == "hello"

    def test_empty_bytes(self):
        assert bytes_to_bin_str(b"") == ""

    def test_latin1_chars(self):
        result = bytes_to_bin_str(b"\xff\xfe")
        assert result == "\xff\xfe"
        assert len(result) == 2

    def test_full_byte_range(self):
        data = bytes(range(256))
        result = bytes_to_bin_str(data)
        assert len(result) == 256

    def test_roundtrip(self):
        original = "test-peer-id"
        encoded = original.encode("latin-1")
        decoded = bytes_to_bin_str(encoded)
        assert decoded == original


class TestHexStrToBinStr:
    def test_simple_hex(self):
        result = hex_str_to_bin_str("48656c6c6f")  # "Hello"
        assert result == "Hello"

    def test_empty_hex(self):
        result = hex_str_to_bin_str("")
        assert result == ""

    def test_info_hash_length(self):
        hex_str = "a" * 40  # 20 bytes as hex
        result = hex_str_to_bin_str(hex_str)
        assert len(result) == 20

    def test_peer_id_length(self):
        hex_str = "b" * 40  # 20 bytes as hex
        result = hex_str_to_bin_str(hex_str)
        assert len(result) == 20

    def test_odd_length_raises(self):
        with pytest.raises(ValueError):
            hex_str_to_bin_str("abc")

    def test_invalid_hex_raises(self):
        with pytest.raises(ValueError):
            hex_str_to_bin_str("ZZZZ")

    def test_mixed_case_hex(self):
        result = hex_str_to_bin_str("4F")
        assert result == "O"
