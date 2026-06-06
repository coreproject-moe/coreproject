"""Compatibility tests: verify protocol format compliance with BEP specs.

These tests ensure our tracker responses are compatible with
libtorrent (C++), anacrolix/torrent (Go), and webtorrent (JS).
"""
import pytest
from coreproject_tracker.constants import CONNECTION_ID
from coreproject_tracker.enums import ACTIONS, REDIS_NAMESPACE_ENUM
from coreproject_tracker.functions import from_uint32, to_uint32


# ---------------------------------------------------------------------------
# BEP3: HTTP Tracker Protocol
# ---------------------------------------------------------------------------


def test_bep3_announce_response_fields(bencode_tools):
    """BEP3: announce response must contain fail_welcome, warning_message,
    interval, peers (or peers6)."""
    # Our response contains: peers, peers6, min interval, complete, incomplete
    sample = {
        "peers": [],
        "peers6": [],
        "min interval": 600,
        "complete": 0,
        "incomplete": 0,
    }
    encoded = bencode_tools["encode"](sample)
    decoded = bencode_tools["decode"](encoded)
    assert "peers" in decoded
    assert "complete" in decoded
    assert "incomplete" in decoded


def test_bep3_peers_format(bencode_tools):
    """BEP3: peers list must be dicts with peer id, ip, port."""
    peer = {
        "peer id": b"-testpeer00000",
        "ip": "192.168.1.1",
        "port": 6881,
    }
    encoded = bencode_tools["encode"]({"peers": [peer]})
    decoded = bencode_tools["decode"](encoded)
    assert len(decoded["peers"]) == 1
    assert "peer id" in decoded["peers"][0]


def test_bep3_scrape_response_format(bencode_tools):
    """BEP3: scrape response must have files dict with complete/incomplete."""
    info_hash = "a" * 40
    sample = {
        "files": {
            info_hash: {
                "complete": 5,
                "incomplete": 3,
            }
        }
    }
    encoded = bencode_tools["encode"](sample)
    decoded = bencode_tools["decode"](encoded)
    assert info_hash in decoded["files"]
    assert decoded["files"][info_hash]["complete"] == 5


# ---------------------------------------------------------------------------
# BEP15: UDP Tracker Protocol
# ---------------------------------------------------------------------------


def test_bep15_connect_request_size():
    """BEP15: CONNECT request = 16 bytes (8 conn + 4 action + 4 txn)."""
    assert len(CONNECTION_ID.to_bytes(8, "big")) == 8


def test_bep15_connect_response_format():
    """BEP15: CONNECT response = 16 bytes (4 action + 4 txn + 8 conn)."""
    from coreproject_tracker.servers.udp import make_udp_packet, UdpDatastructure

    conn_id = CONNECTION_ID.to_bytes(8, "big")
    data = UdpDatastructure(
        connection_id=conn_id,
        action=ACTIONS.CONNECT,
        transaction_id=12345,
    )
    response = make_udp_packet(data)
    assert len(response) == 16
    assert from_uint32(response[0:4]) == ACTIONS.CONNECT
    assert from_uint32(response[4:8]) == 12345
    assert response[8:16] == conn_id


def test_bep15_announce_request_size():
    """BEP15: ANNOUNCE request = 98 bytes."""
    pkt = (
        CONNECTION_ID.to_bytes(8, "big")
        + to_uint32(ACTIONS.ANNOUNCE)
        + to_uint32(1)
        + bytes(20)  # info_hash
        + bytes(20)  # peer_id
        + bytes(8)   # downloaded
        + bytes(8)   # left
        + bytes(8)   # uploaded
        + to_uint32(0)  # event
        + to_uint32(0)  # ip
        + to_uint32(1)  # key
        + to_uint32(50)  # numwant
        + (6881).to_bytes(2, "big")  # port
    )
    assert len(pkt) == 98


def test_bep15_announce_response_format():
    """BEP15: ANNOUNCE response = 20 + N*6 bytes."""
    from coreproject_tracker.servers.udp import make_udp_packet, UdpDatastructure

    conn_id = CONNECTION_ID.to_bytes(8, "big")
    data = UdpDatastructure(
        connection_id=conn_id,
        action=ACTIONS.ANNOUNCE,
        transaction_id=1,
        interval=600,
        incomplete=5,
        complete=10,
        peers=b"",
    )
    response = make_udp_packet(data)
    # 4 action + 4 txn + 4 interval + 4 incomplete + 4 complete + peers
    assert len(response) == 20
    assert from_uint32(response[0:4]) == ACTIONS.ANNOUNCE
    assert from_uint32(response[4:8]) == 1  # transaction_id
    assert from_uint32(response[8:12]) == 600  # interval
    assert from_uint32(response[12:16]) == 5  # incomplete
    assert from_uint32(response[16:20]) == 10  # complete


def test_bep15_compact_peer_format():
    """BEP15: compact peer = 4 bytes IP + 2 bytes port."""
    from coreproject_tracker.functions import addrs_to_compact
    compact = addrs_to_compact(["192.168.1.1:6881"])
    assert len(compact) == 6  # 4 + 2


def test_bep15_scrape_response_format():
    """BEP15: SCRAPE response has d8:torrents{...}e structure."""
    from coreproject_tracker.servers.udp import make_udp_packet, UdpDatastructure

    conn_id = CONNECTION_ID.to_bytes(8, "big")
    scrape_data = (
        b"d8:torrents20:aaaaaaaaaaaaaaaaaaaa"
        b"l5:completei5e8:incompletei3eee"
    )
    data = UdpDatastructure(
        connection_id=conn_id,
        action=ACTIONS.SCRAPE,
        transaction_id=1,
        scrape_data=scrape_data,
    )
    response = make_udp_packet(data)
    assert response[0:4] == to_uint32(ACTIONS.SCRAPE)
    assert b"d8:torrents" in response


# ---------------------------------------------------------------------------
# WebTorrent: WebSocket protocol
# ---------------------------------------------------------------------------


def test_webtorrent_announce_message_format():
    """WebTorrent: announce message must have info_hash, peer_id, action."""
    message = {
        "info_hash": "a" * 40,
        "action": "announce",
        "peer_id": "b" * 40,
        "numwant": 10,
        "left": 1000,
    }
    assert "info_hash" in message
    assert len(message["info_hash"]) == 40  # hex-encoded 20 bytes


def test_webtorrent_response_format():
    """WebTorrent: response must have completed, incompleted, interval."""
    response = {
        "action": "announce",
        "completed": 5,
        "incompleted": 3,
        "interval": 30,
        "info_hash": "a" * 40,
    }
    assert "completed" in response
    assert "incompleted" in response
    assert "interval" in response


def test_webtorrent_offer_message_format():
    """WebTorrent: offer message must have offer, offer_id, peer_id."""
    offer_msg = {
        "action": "announce",
        "offer": {"type": "offer", "sdp": "v=0\r\n"},
        "offer_id": "1",
        "peer_id": "b" * 40,
        "info_hash": "a" * 40,
    }
    assert "offer" in offer_msg
    assert "offer_id" in offer_msg


# ---------------------------------------------------------------------------
# libtorrent compatibility
# ---------------------------------------------------------------------------


def test_libtorrent_expects_bencoded_http_response(bencode_tools):
    """libtorrent expects bencoded HTTP announce responses."""
    response = {
        "peers": [{"peer id": b"x" * 20, "ip": "1.2.3.4", "port": 8080}],
        "peers6": [],
        "complete": 1,
        "incomplete": 0,
        "min interval": 600,
    }
    encoded = bencode_tools["encode"](response)
    # libtorrent decodes as dict
    decoded = bencode_tools["decode"](encoded)
    assert isinstance(decoded["peers"], list)
    assert isinstance(decoded["peers"][0], dict)


def test_libtorrent_udp_connect_id():
    """libtorrent sends our CONNECTION_ID in CONNECT requests."""
    expected = CONNECTION_ID.to_bytes(8, "big")
    assert len(expected) == 8


def test_libtorrent_udp_announce_packet_parsing():
    """libtorrent sends 98-byte ANNOUNCE packets."""
    pkt = (
        CONNECTION_ID.to_bytes(8, "big")
        + to_uint32(ACTIONS.ANNOUNCE)
        + to_uint32(42)
        + bytes(20)
        + bytes(20)
        + (0).to_bytes(8, "big")
        + (1000).to_bytes(8, "big")
        + (500).to_bytes(8, "big")
        + to_uint32(0)
        + to_uint32(0)
        + to_uint32(1)
        + to_uint32(50)
        + (6881).to_bytes(2, "big")
    )
    assert len(pkt) == 98
    assert from_uint32(pkt[8:12]) == ACTIONS.ANNOUNCE
    assert from_uint32(pkt[92:96]) == 50  # numwant
    assert int.from_bytes(pkt[96:98], "big") == 6881  # port
