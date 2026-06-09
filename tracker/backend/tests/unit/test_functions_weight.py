"""Tests for coreproject_tracker.functions.weight - peer ranking."""
import pytest
from attrs import define
from coreproject_tracker.functions.weight import (
    RankedPeer,
    calculate_base_weight,
    rank_peers,
)


@define
class _FakePeerData:
    left: float = 0
    downloaded: int = 0
    uploaded: int = 0


def test_calculate_base_weight_default():
    peer = _FakePeerData(left=100, downloaded=0, uploaded=0)
    assert calculate_base_weight(peer) == pytest.approx(2.5)


def test_calculate_base_weight_seeder_bonus():
    peer = _FakePeerData(left=0, downloaded=0, uploaded=0)
    assert calculate_base_weight(peer) == pytest.approx(1.5)


def test_calculate_base_weight_downloaded_bonus():
    peer = _FakePeerData(left=100, downloaded=1000, uploaded=0)
    assert calculate_base_weight(peer) == pytest.approx(2.0)


def test_calculate_base_weight_uploaded_bonus():
    peer = _FakePeerData(left=100, downloaded=0, uploaded=500)
    assert calculate_base_weight(peer) == pytest.approx(2.2)


def test_calculate_base_weight_all_bonuses():
    peer = _FakePeerData(left=0, downloaded=1000, uploaded=500)
    assert calculate_base_weight(peer) == pytest.approx(0.7)


def test_calculate_base_weight_zero_minimum():
    peer = _FakePeerData(left=0, downloaded=1000, uploaded=500)
    assert calculate_base_weight(peer) >= 0.0


def test_calculate_base_weight_none_left():
    peer = _FakePeerData(left=None, downloaded=0, uploaded=0)
    assert calculate_base_weight(peer) == pytest.approx(2.5)


def test_ranked_peer_creation():
    rp = RankedPeer(
        peer_key="1.2.3.4:8080",
        peer_ip="1.2.3.4",
        port=8080,
        peer_id="abc",
        country="US",
        base_score=1.5,
        combined_score=2.0,
        left=100,
        downloaded=500,
        uploaded=200,
    )
    assert rp.peer_key == "1.2.3.4:8080"
    assert rp.combined_score == 2.0
    assert rp.left == 100


def test_ranked_peer_defaults():
    rp = RankedPeer(peer_key="1.2.3.4:80", peer_ip="1.2.3.4", port=80)
    assert rp.peer_id == ""
    assert rp.country is None
    assert rp.base_score == 0.0
    assert rp.combined_score == 0.0
    assert rp.left is None


def test_rank_peers_empty_pool():
    assert rank_peers("1.2.3.4", "US", [], {}, 50) == []


def test_rank_peers_by_combined_score():
    peer_pool = [
        ("10.0.0.1:1000", 2.0),
        ("10.0.0.2:2000", 1.0),
        ("10.0.0.3:3000", 3.0),
    ]
    peer_data = {
        "10.0.0.1:1000": {"peer_ip": "10.0.0.1", "port": 1000, "country": "US"},
        "10.0.0.2:2000": {"peer_ip": "10.0.0.2", "port": 2000, "country": "US"},
        "10.0.0.3:3000": {"peer_ip": "10.0.0.3", "port": 3000, "country": "US"},
    }
    ranked = rank_peers("10.0.0.1", "US", peer_pool, peer_data, 3)
    assert len(ranked) == 3
    assert ranked[0].base_score <= ranked[1].base_score


def test_rank_peers_respects_numwant():
    peer_pool = [(f"10.0.0.{i}:{i}", 1.0) for i in range(10)]
    peer_data = {
        f"10.0.0.{i}:{i}": {"peer_ip": f"10.0.0.{i}", "port": i, "country": "US"}
        for i in range(10)
    }
    ranked = rank_peers("10.0.0.1", "US", peer_pool, peer_data, 3)
    assert len(ranked) == 3


def test_rank_peers_skips_missing_ip():
    peer_pool = [("bad:0", 1.0)]
    peer_data = {"bad:0": {"peer_ip": "", "port": 0, "country": "US"}}
    ranked = rank_peers("1.2.3.4", "US", peer_pool, peer_data, 10)
    assert len(ranked) == 0


def test_rank_peers_geo_favors_same_country():
    peer_pool = [
        ("same_country:1000", 2.0),
        ("diff_country:2000", 2.0),
    ]
    peer_data = {
        "same_country:1000": {"peer_ip": "10.0.0.1", "port": 1000, "country": "US"},
        "diff_country:2000": {"peer_ip": "10.0.0.2", "port": 2000, "country": "JP"},
    }
    ranked = rank_peers("10.0.0.1", "US", peer_pool, peer_data, 2)
    assert ranked[0].country == "US"


def test_rank_peers_includes_all_fields():
    peer_pool = [("10.0.0.1:8080", 1.5)]
    peer_data = {
        "10.0.0.1:8080": {
            "peer_ip": "10.0.0.1",
            "port": 8080,
            "peer_id": "test-peer-id",
            "country": "US",
            "left": 0,
            "downloaded": 1000,
            "uploaded": 500,
        }
    }
    ranked = rank_peers("10.0.0.1", "US", peer_pool, peer_data, 1)
    peer = ranked[0]
    assert peer.peer_id == "test-peer-id"
    assert peer.left == 0
    assert peer.downloaded == 1000
    assert peer.uploaded == 500
