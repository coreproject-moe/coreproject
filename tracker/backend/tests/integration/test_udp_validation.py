"""UDP packet validation — clean room port from libtorrent tracker_manager.cpp.

Tests that the UDP server correctly validates packets per libtorrent patterns:
minimum size, action codes, transaction IDs, and connection IDs.
"""

import struct

import pytest

from coreproject_tracker.constants import CONNECTION_ID
from coreproject_tracker.enums import ACTIONS

pytestmark = pytest.mark.integration


def _connect_packet(conn_id: int = CONNECTION_ID, txn_id: int = 1) -> bytes:
    return (
        conn_id.to_bytes(8, "big")
        + struct.pack(">I", ACTIONS.CONNECT)
        + struct.pack(">I", txn_id)
    )


def _announce_packet(
    conn_id: int = CONNECTION_ID,
    txn_id: int = 1,
    info_hash: bytes | None = None,
) -> bytes:
    ih = info_hash or bytes(range(20))
    return (
        conn_id.to_bytes(8, "big")
        + struct.pack(">I", ACTIONS.ANNOUNCE)
        + struct.pack(">I", txn_id)
        + ih
        + bytes(20)
        + struct.pack(">Q", 0)
        + struct.pack(">Q", 1000)
        + struct.pack(">Q", 500)
        + struct.pack(">I", 0)
        + struct.pack(">I", 0)
        + struct.pack(">I", 1)
        + struct.pack(">I", 50)
        + struct.pack(">H", 6881)
    )


def _scrape_packet(
    conn_id: int = CONNECTION_ID,
    txn_id: int = 1,
    info_hash: bytes | None = None,
) -> bytes:
    ih = info_hash or bytes(range(20))
    return (
        conn_id.to_bytes(8, "big")
        + struct.pack(">I", ACTIONS.SCRAPE)
        + struct.pack(">I", txn_id)
        + ih
    )


class TestUdpPacketSize:
    def test_connect_packet_size(self):
        assert len(_connect_packet()) == 16

    def test_announce_packet_size(self):
        assert len(_announce_packet()) == 98

    def test_scrape_packet_size(self):
        assert len(_scrape_packet()) == 36

    def test_packet_too_small_8_bytes(self):
        small = CONNECTION_ID.to_bytes(8, "big")
        assert len(small) == 8

    def test_packet_too_small_4_bytes(self):
        small = struct.pack(">I", ACTIONS.CONNECT)
        assert len(small) == 4

    def test_packet_too_small_1_byte(self):
        small = b"\x00"
        assert len(small) == 1


class TestUdpActionCodeValidation:
    def test_valid_action_connect(self):
        pkt = _connect_packet()
        action = struct.unpack(">I", pkt[8:12])[0]
        assert action == ACTIONS.CONNECT
        assert 0 <= action <= 3

    def test_valid_action_announce(self):
        pkt = _announce_packet()
        action = struct.unpack(">I", pkt[8:12])[0]
        assert action == ACTIONS.ANNOUNCE
        assert 0 <= action <= 3

    def test_valid_action_scrape(self):
        pkt = _scrape_packet()
        action = struct.unpack(">I", pkt[8:12])[0]
        assert action == ACTIONS.SCRAPE
        assert 0 <= action <= 3

    def test_valid_action_error(self):
        pkt = (
            CONNECTION_ID.to_bytes(8, "big")
            + struct.pack(">I", ACTIONS.ERROR)
            + struct.pack(">I", 1)
        )
        action = struct.unpack(">I", pkt[8:12])[0]
        assert action == ACTIONS.ERROR
        assert 0 <= action <= 3

    def test_invalid_action_code_4(self):
        pkt = (
            CONNECTION_ID.to_bytes(8, "big")
            + struct.pack(">I", 4)
            + struct.pack(">I", 1)
        )
        action = struct.unpack(">I", pkt[8:12])[0]
        assert action == 4
        assert action > 3

    def test_invalid_action_code_max_uint32(self):
        pkt = (
            CONNECTION_ID.to_bytes(8, "big")
            + struct.pack(">I", 0xFFFFFFFF)
            + struct.pack(">I", 1)
        )
        action = struct.unpack(">I", pkt[8:12])[0]
        assert action == 0xFFFFFFFF


class TestUdpTransactionId:
    def test_transaction_id_preserved(self):
        txn = 12345
        pkt = _connect_packet(txn_id=txn)
        extracted = struct.unpack(">I", pkt[12:16])[0]
        assert extracted == txn

    def test_transaction_id_zero(self):
        txn = 0
        pkt = _connect_packet(txn_id=txn)
        extracted = struct.unpack(">I", pkt[12:16])[0]
        assert extracted == txn

    def test_transaction_id_max(self):
        txn = 0xFFFFFFFE
        pkt = _connect_packet(txn_id=txn)
        extracted = struct.unpack(">I", pkt[12:16])[0]
        assert extracted == txn


class TestUdpConnectionId:
    def test_connection_id_format(self):
        conn_bytes = CONNECTION_ID.to_bytes(8, "big")
        assert len(conn_bytes) == 8
        extracted = int.from_bytes(conn_bytes, "big")
        assert extracted == CONNECTION_ID

    def test_wrong_connection_id(self):
        wrong_id = 0xDEADBEEFDEADBEEF
        pkt = _connect_packet(conn_id=wrong_id)
        extracted_id = int.from_bytes(pkt[0:8], "big")
        assert extracted_id != CONNECTION_ID

    def test_zero_connection_id(self):
        pkt = _connect_packet(conn_id=0)
        extracted_id = int.from_bytes(pkt[0:8], "big")
        assert extracted_id == 0


class TestUdpAnnounceFields:
    def test_announce_info_hash_position(self):
        ih = bytes(range(20))
        pkt = _announce_packet(info_hash=ih)
        assert pkt[16:36] == ih

    def test_announce_peer_id_position(self):
        pkt = _announce_packet()
        peer_id = pkt[36:56]
        assert len(peer_id) == 20

    def test_announce_downloaded_position(self):
        pkt = _announce_packet()
        downloaded = struct.unpack(">Q", pkt[56:64])[0]
        assert downloaded == 0

    def test_announce_left_position(self):
        pkt = _announce_packet()
        left = struct.unpack(">Q", pkt[64:72])[0]
        assert left == 1000

    def test_announce_uploaded_position(self):
        pkt = _announce_packet()
        uploaded = struct.unpack(">Q", pkt[72:80])[0]
        assert uploaded == 500

    def test_announce_event_position(self):
        pkt = _announce_packet()
        event = struct.unpack(">I", pkt[80:84])[0]
        assert event == 0

    def test_announce_numwant_position(self):
        pkt = _announce_packet()
        numwant = struct.unpack(">I", pkt[92:96])[0]
        assert numwant == 50

    def test_announce_port_position(self):
        pkt = _announce_packet()
        port = struct.unpack(">H", pkt[96:98])[0]
        assert port == 6881
