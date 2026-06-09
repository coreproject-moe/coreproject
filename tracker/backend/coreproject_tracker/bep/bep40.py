"""BEP40 peer priority — clean room port from anacrolix/torrent bep40.go.

Computes a CRC32 Castagnoli hash of masked IP bytes to produce a peer
priority uint32. Lower priority values indicate closer network proximity.
Cross-validated against Go reference values in test_bep40.py.
"""

import ipaddress
from typing import Final

_POLY_CASTAGNOLI: Final = 0x82F63B78
_MASK_PARTIAL: Final = 0x55
_MASK_FULL: Final = 0xFF

_crc32c_table: list[int] | None = None


def _build_crc32c_table() -> list[int]:
    """Build CRC32 Castagnoli lookup table (256 entries)."""
    table: list[int] = []
    for i in range(256):
        crc = i
        for _ in range(8):
            if crc & 1:
                crc = (_POLY_CASTAGNOLI ^ (crc >> 1)) & 0xFFFFFFFF
            else:
                crc >>= 1
        table.append(crc)
    return table


def _crc32c(data: bytes) -> int:
    """Compute CRC32 Castagnoli checksum. Pure Python, no external deps."""
    global _crc32c_table
    if _crc32c_table is None:
        _crc32c_table = _build_crc32c_table()
    crc = 0xFFFFFFFF
    for byte in data:
        crc = (_crc32c_table[(crc ^ byte) & 0xFF] ^ (crc >> 8)) & 0xFFFFFFFF
    return crc ^ 0xFFFFFFFF


def _get_ip_bytes(ip_str: str) -> tuple[bytes, int]:
    """Parse IP string to packed bytes and version."""
    ip = ipaddress.ip_address(ip_str.strip("[]"))
    return ip.packed, ip.version


def _ipv4_mask_len(a: bytes, b: bytes) -> int:
    """Determine mask length for two IPv4 addresses based on subnet overlap."""
    if a[:2] != b[:2]:
        return 2
    if a[:3] != b[:3]:
        return 3
    return 4


def _ipv6_mask_len(a: bytes, b: bytes) -> int:
    """Determine mask length for two IPv6 addresses based on common prefix."""
    for prefix_bytes in range(6, 17):
        if a[:prefix_bytes] != b[:prefix_bytes]:
            return prefix_bytes
    return 16  # pragma: no cover


def _apply_mask(ip_bytes: bytes, mask_len: int, total_len: int) -> bytes:
    """Apply proximity mask to IP bytes."""
    mask = bytearray(total_len)
    for i in range(mask_len):
        mask[i] = _MASK_FULL
    for i in range(mask_len, total_len):
        mask[i] = _MASK_PARTIAL
    return bytes(a & b for a, b in zip(ip_bytes, mask))


def _symmetrize(data: bytes) -> bytes:
    """Ensure left half <= right half lexicographically for commutativity."""
    half = len(data) // 2
    left = data[:half]
    right = data[half:]
    if left > right:
        left, right = right, left
    return left + right


def bep40_priority_bytes(
    ip_a: str, ip_b: str, port_a: int = 0, port_b: int = 0
) -> bytes:
    """Build the raw byte array per BEP40 spec before CRC32 hashing.

    Handles same-IP, IPv4, IPv6, and mixed version cases.
    Returns the symmetrized byte array ready for CRC32 hashing.
    Raises ValueError for incomparable (mixed IPv4/IPv6) inputs.
    """
    bytes_a, ver_a = _get_ip_bytes(ip_a)
    bytes_b, ver_b = _get_ip_bytes(ip_b)

    if bytes_a == bytes_b:
        return (
            port_a.to_bytes(2, "big") + port_b.to_bytes(2, "big")
        )

    if ver_a != ver_b:
        raise ValueError("incomparable IPs: mixed IPv4 and IPv6")

    if ver_a == 4:
        mask_len = _ipv4_mask_len(bytes_a, bytes_b)
        masked_a = _apply_mask(bytes_a, mask_len, 4)
        masked_b = _apply_mask(bytes_b, mask_len, 4)
    else:
        mask_len = _ipv6_mask_len(bytes_a, bytes_b)
        masked_a = _apply_mask(bytes_a, mask_len, 16)
        masked_b = _apply_mask(bytes_b, mask_len, 16)

    return _symmetrize(masked_a + masked_b)


def bep40_priority(ip_a: str, ip_b: str, port_a: int = 0, port_b: int = 0) -> int:
    """Compute BEP40 peer priority between two IPs.

    Returns a uint32 — lower values mean closer network proximity.
    Cross-validated against anacrolix/torrent Go reference values.
    """
    data = bep40_priority_bytes(ip_a, ip_b, port_a, port_b)
    return _crc32c(data)
