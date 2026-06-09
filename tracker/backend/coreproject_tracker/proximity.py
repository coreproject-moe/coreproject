"""BEP40 network proximity and geo distance scoring.

Ported from inspirations/torrent bep40 implementation.
Lower scores = closer proximity (better for peer ranking).
"""

import ipaddress
import struct

import coreproject_tracker.constants.regions as regions


def _same_subnet(ones: int, bits: int, a: bytes, b: bytes) -> bool:
    mask = struct.pack("!B", (0xff << (8 - ones % 8)) & 0xff) if ones % 8 else b"\xff"
    full_mask_len = ones // 8
    mask_bytes = b"\xff" * full_mask_len + mask if ones % 8 else b"\xff" * full_mask_len
    return a[:len(mask_bytes)] == b[:len(mask_bytes)]


def _ipv4_mask(a: bytes, b: bytes) -> int:
    if not _same_subnet(16, 32, a, b):
        return 2
    if not _same_subnet(24, 32, a, b):
        return 3
    return 4


def _ipv6_mask(a: bytes, b: bytes) -> int:
    for prefix_bytes in range(6, 17):
        if _same_subnet(prefix_bytes * 8, 128, a, b):
            continue
        return prefix_bytes
    return 16


def _ip_to_bytes(ip_str: str) -> tuple[bytes, int]:
    try:
        ip = ipaddress.ip_address(ip_str.strip("[]"))
    except ValueError:
        return b"", 0
    return ip.packed, ip.version


def bep40_proximity(ip_a: str, ip_b: str) -> float:
    """Compute network proximity between two IPs.

    Ported from BEP40 in inspirations/torrent/bep40.go.
    Lower score = closer network proximity.
    Returns 0.0-10.0 range.
    """
    bytes_a, ver_a = _ip_to_bytes(ip_a)
    bytes_b, ver_b = _ip_to_bytes(ip_b)

    if not bytes_a or not bytes_b:
        return 10.0

    if ver_a != ver_b:
        return 10.0

    if ver_a == 4:
        mask_len = _ipv4_mask(bytes_a, bytes_b)
    else:
        mask_len = _ipv6_mask(bytes_a, bytes_b)

    # Normalize: more mask bytes = closer = lower score
    if ver_a == 4:
        return max(0.0, 10.0 - (mask_len / 4) * 10.0)
    return max(0.0, 10.0 - (mask_len / 16) * 10.0)


def geo_distance(country_a: str | None, country_b: str | None) -> float:
    """Compute geo distance penalty between two country codes.

    Lower = closer. Uses adjacency map then continent fallback.
    """
    if not country_a or not country_b:
        return regions.GEO_UNKNOWN

    if country_a == country_b:
        return regions.GEO_SAME_COUNTRY

    adj_a = regions.COUNTRY_ADJACENCY.get(country_a, set())
    adj_b = regions.COUNTRY_ADJACENCY.get(country_b, set())

    if country_b in adj_a or country_a in adj_b:
        return regions.GEO_ADJACENT

    cont_a = regions.COUNTRY_CONTINENT.get(country_a)
    cont_b = regions.COUNTRY_CONTINENT.get(country_b)

    if cont_a and cont_b and cont_a == cont_b:
        return regions.GEO_SAME_CONTINENT

    return regions.GEO_DIFFERENT_CONTINENT
