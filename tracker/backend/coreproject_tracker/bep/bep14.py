"""BEP14 Local Peer Discovery — clean room port from anacrolix/torrent bep14.go.

Server-side LPD message handling: packet parsing, peer registry,
and MTU-compliant announce packet construction.
"""

import re
from attrs import define
from datetime import datetime, timezone

LPD_HOST4: str = "239.192.152.143"
LPD_PORT: int = 6771
LPD_HOST6: str = "ff15::efc0:988f"
LPD_MAX_PACKET_SIZE: int = 1400
LPD_LONG_TIMEOUT: int = 10
LPD_SHORT_TIMEOUT: int = 1
LPD_PEER_EXPIRY: int = LPD_LONG_TIMEOUT * 2


@define
class LPDPacket:
    peer_host: str
    peer_port: int
    infohashes: list[bytes]


def parse_lpd_packet(data: bytes, sender_ip: str = "0.0.0.0") -> LPDPacket:
    """Parse a BT-SEARCH LPD announce packet.

    Validates method, extracts Port and Infohash headers.
    Raises ValueError for malformed packets (wrong method, missing required headers).
    """
    text = data.decode("utf-8", errors="replace")
    if not text:
        raise ValueError("empty LPD packet")

    lines = text.split("\r\n")

    header_map: dict[str, list[str]] = {}
    request_line = lines[0]

    for line in lines[1:]:
        if line == "":
            break
        match = re.match(r"^([^:]+):\s*(.*)", line)
        if match:
            key = match.group(1).strip().lower()
            value = match.group(2).strip()
            header_map.setdefault(key, []).append(value)

    parts = request_line.split()
    if not parts[0]:  # pragma: no cover
        raise ValueError("missing request method")

    method = parts[0]
    if method != "BT-SEARCH":
        raise ValueError(f"invalid LPD method: {method}, expected BT-SEARCH")

    if "port" not in header_map:
        raise ValueError("missing Port header in LPD packet")

    try:
        peer_port = int(header_map["port"][0])
    except (ValueError, IndexError):
        raise ValueError("invalid Port value in LPD packet")

    if "infohash" not in header_map:
        raise ValueError("missing Infohash header in LPD packet")

    infohashes: list[bytes] = []
    for ih_hex in header_map["infohash"]:
        try:
            infohashes.append(bytes.fromhex(ih_hex))
        except ValueError:
            raise ValueError(f"invalid infohash hex: {ih_hex}")

    return LPDPacket(
        peer_host=sender_ip,
        peer_port=peer_port,
        infohashes=infohashes,
    )


class LPDPeerStore:
    """In-memory LPD peer registry with deduplication and expiry."""

    def __init__(self) -> None:
        self._peers: dict[str, datetime] = {}

    def add_peer(self, addr: str, ts: datetime | None = None) -> None:
        """Register or refresh a peer. Same address overwrites timestamp."""
        if ts is None:
            ts = datetime.now(timezone.utc)
        self._peers[addr] = ts

    def refresh(self, now: datetime | None = None) -> None:
        """Remove peers stale for more than LPD_PEER_EXPIRY seconds."""
        if now is None:
            now = datetime.now(timezone.utc)
        cutoff = now.timestamp() - LPD_PEER_EXPIRY
        self._peers = {
            addr: ts for addr, ts in self._peers.items()
            if ts.timestamp() > cutoff
        }

    def get_peers(self) -> dict[str, datetime]:
        """Return a copy of the current peer registry."""
        return dict(self._peers)

    @property
    def peer_count(self) -> int:
        return len(self._peers)


def build_lpd_packet(
    host: str,
    port: int,
    infohash_queue: list[bytes] | None,
    max_size: int = LPD_MAX_PACKET_SIZE,
) -> tuple[bytes | None, int, bool]:
    """Build MTU-compliant LPD announce packets.

    Returns (packet_bytes, next_index, rotated_flag).
    If queue is None or empty, returns (None, 0, True).
    Large queues are fragmented across multiple packets under max_size.
    Call iteratively: use next_index as start for the next call.
    """
    if not infohash_queue:
        return None, 0, True

    header = f"BT-SEARCH * HTTP/1.1\r\nHost: {host}:{port}\r\nPort: {port}\r\n"
    header_bytes = header.encode("utf-8")
    terminator = b"\r\n\r\n"
    available = max_size - len(header_bytes) - len(terminator)

    packet_infohashes: list[bytes] = []
    next_idx = 0
    rotated = False

    for i, ih in enumerate(infohash_queue):
        ih_line = f"Infohash: {ih.hex()}\r\n".encode("utf-8")
        current_size = sum(len(f"Infohash: {x.hex()}\r\n".encode()) for x in packet_infohashes)
        if current_size + len(ih_line) > available and packet_infohashes:
            next_idx = i
            break
        packet_infohashes.append(ih)
        next_idx = i + 1

    if next_idx == len(infohash_queue):
        rotated = True

    if not packet_infohashes:  # pragma: no cover
        return None, 0, False

    body = header_bytes
    for ih in packet_infohashes:
        body += f"Infohash: {ih.hex()}\r\n".encode("utf-8")
    body += terminator

    return body, next_idx, rotated
