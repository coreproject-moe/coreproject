"""Integration tests for UDP packet format handling."""
import pytest

pytestmark = pytest.mark.integration


def test_udp_connect_packet_format(udp_connect_packet):
    """Verify CONNECT request packet structure (BEP15)."""
    pkt = udp_connect_packet
    assert len(pkt) == 16  # 8 conn_id + 4 action + 4 txn_id
    assert pkt[8:12] == b"\x00\x00\x00\x00"  # action CONNECT


def test_udp_announce_packet_format(udp_announce_packet):
    """Verify ANNOUNCE request packet structure (BEP15)."""
    pkt = udp_announce_packet
    assert len(pkt) == 98
    assert pkt[8:12] == b"\x00\x00\x00\x01"  # action ANNOUNCE
    # info_hash at offset 16 (20 bytes)
    assert len(pkt[16:36]) == 20
    # peer_id at offset 36 (20 bytes)
    assert len(pkt[36:56]) == 20


def test_udp_scrape_packet_format(udp_scrape_packet):
    """Verify SCRAPE request packet structure (BEP15)."""
    pkt = udp_scrape_packet
    assert len(pkt) == 36  # 8 + 4 + 4 + 20
    assert pkt[8:12] == b"\x00\x00\x00\x02"  # action SCRAPE


def test_udp_make_connect_response(udp_connect_packet, udp_connection_id):
    """Verify CONNECT response packet (BEP15)."""
    from coreproject_tracker.constants import CONNECTION_ID
    from coreproject_tracker.enums import ACTIONS
    from coreproject_tracker.functions import from_uint32, to_uint32
    from coreproject_tracker.servers.udp import make_udp_packet, UdpDatastructure

    data = UdpDatastructure(
        connection_id=udp_connection_id,
        action=ACTIONS.CONNECT,
        transaction_id=from_uint32(udp_connect_packet[12:16]),
    )
    response = make_udp_packet(data)
    assert response[0:4] == to_uint32(ACTIONS.CONNECT)
    assert response[8:16] == udp_connection_id


def test_udp_make_announce_response(udp_announce_packet, udp_connection_id):
    """Verify ANNOUNCE response packet structure."""
    from coreproject_tracker.enums import ACTIONS
    from coreproject_tracker.functions import from_uint32, to_uint32
    from coreproject_tracker.servers.udp import make_udp_packet, UdpDatastructure

    data = UdpDatastructure(
        connection_id=udp_connection_id,
        action=ACTIONS.ANNOUNCE,
        transaction_id=from_uint32(udp_announce_packet[12:16]),
        interval=600,
        incomplete=5,
        complete=10,
        peers=b"",
    )
    response = make_udp_packet(data)
    assert response[0:4] == to_uint32(ACTIONS.ANNOUNCE)


def test_udp_make_scrape_response(udp_scrape_packet, udp_connection_id):
    """Verify SCRAPE response packet structure."""
    from coreproject_tracker.enums import ACTIONS
    from coreproject_tracker.functions import from_uint32, to_uint32
    from coreproject_tracker.servers.udp import make_udp_packet, UdpDatastructure

    data = UdpDatastructure(
        connection_id=udp_connection_id,
        action=ACTIONS.SCRAPE,
        transaction_id=from_uint32(udp_scrape_packet[12:16]),
        scrape_data=b"d8:torrentse",
    )
    response = make_udp_packet(data)
    assert response[0:4] == to_uint32(ACTIONS.SCRAPE)


def test_udp_make_unknown_action_raises(udp_connection_id):
    """Unknown action should raise ValueError."""
    from coreproject_tracker.enums import ACTIONS
    from coreproject_tracker.servers.udp import make_udp_packet, UdpDatastructure

    data = UdpDatastructure(
        connection_id=udp_connection_id,
        action=ACTIONS.ERROR,
        transaction_id=1,
    )
    with pytest.raises(ValueError, match="not implemented"):
        make_udp_packet(data)
