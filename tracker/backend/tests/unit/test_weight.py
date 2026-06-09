"""Tests for peer weight calculation and ranking."""
import pytest
from attrs import define
from coreproject_tracker.functions.weight import (
    RankedPeer,
    calculate_weight,
    rank_peers,
)


@define
class _PeerStub:
    left: float = 0
    downloaded: int = 0
    uploaded: int = 0


def test_calculate_weight_default():
    assert calculate_weight(_PeerStub(left=100)) == pytest.approx(2.5)


def test_calculate_weight_seeder():
    assert calculate_weight(_PeerStub(left=0)) == pytest.approx(1.5)


def test_calculate_weight_downloaded():
    assert calculate_weight(_PeerStub(left=100, downloaded=1000)) == pytest.approx(2.0)


def test_calculate_weight_uploaded():
    assert calculate_weight(_PeerStub(left=100, uploaded=500)) == pytest.approx(2.2)


def test_calculate_weight_all_bonuses():
    assert calculate_weight(_PeerStub(left=0, downloaded=1000, uploaded=500)) == pytest.approx(0.7)


def test_calculate_weight_non_negative():
    assert calculate_weight(_PeerStub(left=0, downloaded=1000, uploaded=500)) >= 0.0


def test_ranked_peer_defaults():
    rp = RankedPeer(peer_key="1.2.3.4:80", peer_ip="1.2.3.4", port=80)
    assert rp.peer_id == "" and rp.country is None
    assert rp.base_score == 0.0 and rp.combined_score == 0.0


def test_rank_peers_empty():
    assert rank_peers("1.2.3.4", "US", [], {}, 50) == []


def test_rank_peers_orders_by_score():
    pool = [
        ("10.0.0.1:1000", 2.0),
        ("10.0.0.2:2000", 1.0),
        ("10.0.0.3:3000", 3.0),
    ]
    data = {
        "10.0.0.1:1000": {"peer_ip": "10.0.0.1", "port": 1000, "country": "US"},
        "10.0.0.2:2000": {"peer_ip": "10.0.0.2", "port": 2000, "country": "US"},
        "10.0.0.3:3000": {"peer_ip": "10.0.0.3", "port": 3000, "country": "US"},
    }
    ranked = rank_peers("10.0.0.1", "US", pool, data, 3)
    assert len(ranked) == 3
    assert ranked[0].base_score <= ranked[1].base_score


def test_rank_peers_numwant_limit():
    pool = [(f"10.0.0.{i}:{i}", 1.0) for i in range(10)]
    data = {
        f"10.0.0.{i}:{i}": {"peer_ip": f"10.0.0.{i}", "port": i, "country": "US"}
        for i in range(10)
    }
    assert len(rank_peers("10.0.0.1", "US", pool, data, 3)) == 3


def test_rank_peers_skips_bad_ip():
    pool = [("bad:0", 1.0)]
    data = {"bad:0": {"peer_ip": "", "port": 0, "country": "US"}}
    assert len(rank_peers("1.2.3.4", "US", pool, data, 10)) == 0


def test_rank_peers_geo_preference():
    pool = [("same:1000", 2.0), ("diff:2000", 2.0)]
    data = {
        "same:1000": {"peer_ip": "10.0.0.1", "port": 1000, "country": "US"},
        "diff:2000": {"peer_ip": "10.0.0.2", "port": 2000, "country": "JP"},
    }
    ranked = rank_peers("10.0.0.1", "US", pool, data, 2)
    assert ranked[0].country == "US"
