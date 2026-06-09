"""BEP14 Local Peer Discovery — clean room port from anacrolix/torrent bep14_test.go.

Verifies LPD packet parsing, peer store behavior, and packet fragmentation.
"""

import pytest
from datetime import datetime, timezone, timedelta

from coreproject_tracker.bep.bep14 import (
    LPD_PEER_EXPIRY,
    LPD_MAX_PACKET_SIZE,
    LPD_PORT,
    LPDPeerStore,
    build_lpd_packet,
    parse_lpd_packet,
)

pytestmark = pytest.mark.integration


def _make_lpd_packet(
    method: str = "BT-SEARCH",
    host: str = "239.192.152.143:6771",
    port: str = "6881",
    infohashes: list[str] | None = None,
) -> bytes:
    """Build an LPD packet for testing."""
    lines = [
        f"{method} * HTTP/1.1",
        f"Host: {host}",
        f"Port: {port}",
    ]
    if infohashes:
        for ih in infohashes:
            lines.append(f"Infohash: {ih}")
    return ("\r\n".join(lines) + "\r\n\r\n").encode("utf-8")


class TestParseLpdPacket:
    def test_multi_infohash_parsing(self):
        data = _make_lpd_packet(
            infohashes=["AABBCCDD11223344AABBCCDD11223344AABBCCDD", "1111222233334444111122223333444411112222"]
        )
        packet = parse_lpd_packet(data, sender_ip="192.168.1.100")
        assert packet.peer_host == "192.168.1.100"
        assert packet.peer_port == 6881
        assert len(packet.infohashes) == 2
        assert packet.infohashes[0] == bytes.fromhex("AABBCCDD11223344AABBCCDD11223344AABBCCDD")

    def test_single_infohash(self):
        data = _make_lpd_packet(infohashes=["0" * 40])
        packet = parse_lpd_packet(data, sender_ip="10.0.0.1")
        assert len(packet.infohashes) == 1
        assert packet.infohashes[0] == b"\x00" * 20

    def test_wrong_method_rejected(self):
        data = _make_lpd_packet(method="GET", infohashes=["A" * 40], port="9999")
        with pytest.raises(ValueError, match="method"):
            parse_lpd_packet(data)

    def test_missing_infohash_rejected(self):
        data = _make_lpd_packet(infohashes=None)
        with pytest.raises(ValueError, match="Infohash"):
            parse_lpd_packet(data)

    def test_missing_port_rejected(self):
        raw = (
            "BT-SEARCH * HTTP/1.1\r\n"
            "Host: 239.192.152.143:6771\r\n"
            "Infohash: AABBCCDD11223344AABBCCDD11223344AABBCCDD\r\n"
            "\r\n\r\n"
        )
        with pytest.raises(ValueError, match="Port"):
            parse_lpd_packet(raw.encode("utf-8"))

    def test_malformed_get_method(self):
        raw = (
            "GET * HTTP/1.1\r\n"
            "Host: 239.192.152.143:6771\r\n"
            "Port: 9999\r\n"
            "Infohash: AABBCCDD11223344AABBCCDD11223344AABBCCDD\r\n"
            "\r\n\r\n"
        )
        with pytest.raises(ValueError):
            parse_lpd_packet(raw.encode("utf-8"))

    def test_malformed_missing_infohash(self):
        raw = (
            "BT-SEARCH * HTTP/1.1\r\n"
            "Host: 239.192.152.143:6771\r\n"
            "Port: 9999\r\n"
            "\r\n\r\n"
        )
        with pytest.raises(ValueError):
            parse_lpd_packet(raw.encode("utf-8"))

    def test_malformed_missing_port(self):
        raw = (
            "BT-SEARCH * HTTP/1.1\r\n"
            "Host: 239.192.152.143:6771\r\n"
            "Infohash: AABBCCDD11223344AABBCCDD11223344AABBCCDD\r\n"
            "\r\n\r\n"
        )
        with pytest.raises(ValueError):
            parse_lpd_packet(raw.encode("utf-8"))

    def test_invalid_port_value(self):
        raw = (
            "BT-SEARCH * HTTP/1.1\r\n"
            "Host: 239.192.152.143:6771\r\n"
            "Port: notanumber\r\n"
            "Infohash: AABBCCDD11223344AABBCCDD11223344AABBCCDD\r\n"
            "\r\n\r\n"
        )
        with pytest.raises(ValueError, match="Port"):
            parse_lpd_packet(raw.encode("utf-8"))

    def test_invalid_infohash_hex(self):
        raw = (
            "BT-SEARCH * HTTP/1.1\r\n"
            "Host: 239.192.152.143:6771\r\n"
            "Port: 6881\r\n"
            "Infohash: NOTHEXDATA\r\n"
            "\r\n\r\n"
        )
        with pytest.raises(ValueError, match="infohash"):
            parse_lpd_packet(raw.encode("utf-8"))

    def test_no_headers(self):
        raw = "BT-SEARCH * HTTP/1.1\r\n\r\n\r\n"
        with pytest.raises(ValueError, match="Port"):
            parse_lpd_packet(raw.encode("utf-8"))

    def test_malformed_header_skipped(self):
        raw = (
            "BT-SEARCH * HTTP/1.1\r\n"
            "MalformedHeaderWithNoColon\r\n"
            "Port: 6881\r\n"
            "Infohash: AABBCCDD11223344AABBCCDD11223344AABBCCDD\r\n"
            "\r\n\r\n"
        )
        packet = parse_lpd_packet(raw.encode("utf-8"))
        assert packet.peer_port == 6881
        assert len(packet.infohashes) == 1

    def test_empty_data(self):
        with pytest.raises(ValueError, match="empty"):
            parse_lpd_packet(b"")

    def test_request_line_only_no_headers(self):
        raw = "BT-SEARCH * HTTP/1.1"
        with pytest.raises(ValueError, match="Port"):
            parse_lpd_packet(raw.encode("utf-8"))


class TestLpdPeerStore:
    def test_peer_deduplication(self):
        store = LPDPeerStore()
        ts = datetime.now(timezone.utc)
        store.add_peer("1.2.3.4:6881", ts)
        store.add_peer("1.2.3.4:6881", ts)
        assert store.peer_count == 1

    def test_peer_expiry(self):
        store = LPDPeerStore()
        now = datetime.now(timezone.utc)
        stale = now - timedelta(seconds=LPD_PEER_EXPIRY + 10)
        fresh = now - timedelta(seconds=5)

        store.add_peer("1.2.3.4:6881", stale)
        store.add_peer("5.6.7.8:6882", fresh)
        assert store.peer_count == 2

        store.refresh(now)
        assert store.peer_count == 1
        assert "5.6.7.8:6882" in store.get_peers()

    def test_peer_no_expiry_when_fresh(self):
        store = LPDPeerStore()
        now = datetime.now(timezone.utc)
        store.add_peer("1.2.3.4:6881", now)
        store.refresh(now)
        assert store.peer_count == 1

    def test_peer_discovery(self):
        store = LPDPeerStore()
        ts = datetime.now(timezone.utc)
        store.add_peer("192.168.1.1:6881", ts)
        store.add_peer("192.168.1.2:6882", ts)
        assert store.peer_count == 2
        peers = store.get_peers()
        assert "192.168.1.1:6881" in peers
        assert "192.168.1.2:6882" in peers

    def test_get_peers_returns_copy(self):
        store = LPDPeerStore()
        ts = datetime.now(timezone.utc)
        store.add_peer("1.2.3.4:6881", ts)
        copy = store.get_peers()
        copy.clear()
        assert store.peer_count == 1

    def test_add_peer_default_timestamp(self):
        store = LPDPeerStore()
        store.add_peer("1.2.3.4:6881")
        assert store.peer_count == 1

    def test_refresh_default_now(self):
        store = LPDPeerStore()
        store.add_peer("1.2.3.4:6881")
        store.refresh()
        assert store.peer_count == 1


class TestBuildLpdPacket:
    def test_empty_queue(self):
        packet, next_idx, rotated = build_lpd_packet("239.192.152.143", LPD_PORT, None)
        assert packet is None
        assert next_idx == 0
        assert rotated is True

    def test_empty_list_queue(self):
        packet, next_idx, rotated = build_lpd_packet(
            "239.192.152.143", LPD_PORT, []
        )
        assert packet is None
        assert next_idx == 0
        assert rotated is True

    def test_single_packet_fits(self):
        infohashes = [bytes.fromhex("A" * 40), bytes.fromhex("B" * 40)]
        packet, next_idx, rotated = build_lpd_packet(
            "239.192.152.143", LPD_PORT, infohashes
        )
        assert packet is not None
        assert next_idx == 2
        assert rotated is True
        assert b"Infohash: " in packet

    def test_fragmentation_large_queue(self):
        infohashes = [bytes.fromhex(f"{i:040x}") for i in range(40)]
        all_infohashes = set()
        next_idx = 0
        packet_count = 0

        while next_idx < len(infohashes):
            packet, next_idx, rotated = build_lpd_packet(
                "239.192.152.143", LPD_PORT, infohashes[packet_count * 10:]
            )
            if packet is None:
                break
            assert len(packet) <= LPD_MAX_PACKET_SIZE + 200
            packet_count += 1

        assert packet_count > 0

    def test_packet_contains_infohashes(self):
        ih1 = bytes.fromhex("AA" * 20)
        ih2 = bytes.fromhex("BB" * 20)
        packet, _, _ = build_lpd_packet("239.192.152.143", LPD_PORT, [ih1, ih2])
        assert packet is not None
        assert ih1.hex().encode() in packet
        assert ih2.hex().encode() in packet

    def test_packet_format(self):
        infohashes = [bytes.fromhex("A" * 40)]
        packet, _, _ = build_lpd_packet("239.192.152.143", LPD_PORT, infohashes)
        assert packet is not None
        assert packet.startswith(b"BT-SEARCH * HTTP/1.1")
        assert packet.endswith(b"\r\n\r\n")
