"""Tests for immutable data structures."""
import pytest
from coreproject_tracker.datastructures import (
    HttpDatastructure,
    MutableBox,
    UdpDatastructure,
    WebsocketDatastructure,
)
from coreproject_tracker.constants import CONNECTION_ID


def test_http_datastructure_valid():
    data = HttpDatastructure(
        info_hash_raw=bytes(20),
        port=6881,
        left=1000,
        numwant=50,
        peer_id="-" * 20,
        peer_ip="192.168.1.1",
    )
    assert data.info_hash == "0" * 40
    assert data.numwant <= 82


def test_http_datastructure_bad_ip():
    with pytest.raises(ValueError):
        HttpDatastructure(
            info_hash_raw=bytes(20),
            port=6881,
            left=0,
            numwant=50,
            peer_id="x" * 20,
            peer_ip="bad-ip",
        )


def test_udp_datastructure_connect():
    data = UdpDatastructure(
        connection_id=CONNECTION_ID.to_bytes(8, "big"),
        action=0,
        transaction_id=12345,
    )
    assert data.interval > 0
    assert data.numwant <= 82


def test_udp_datastructure_bad_connection_id():
    with pytest.raises(ValueError):
        UdpDatastructure(
            connection_id=b"\x00" * 8,
            action=0,
            transaction_id=1,
        )


def test_websocket_datastructure_valid():
    data = WebsocketDatastructure(
        info_hash_raw=bytes(20),
        action="announce",
        peer_id="a" * 20,
        ip="192.168.1.1",
        port=6881,
        addr="192.168.1.1:6881",
    )
    assert data.info_hash == "00" * 20


def test_websocket_datastructure_bad_ip():
    with pytest.raises(ValueError):
        WebsocketDatastructure(
            info_hash_raw=bytes(20),
            action="announce",
            peer_id="a" * 20,
            ip="bad",
            port=6881,
            addr="bad:6881",
        )


def test_mutable_box():
    box = MutableBox[int](0)
    assert box.value == 0
    box.value = 42
    assert box.value == 42


def test_mutable_box_generic():
    box = MutableBox[list[str]]([])
    box.value.append("hello")
    assert box.value == ["hello"]
