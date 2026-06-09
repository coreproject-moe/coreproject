"""Tests for BEP40 proximity and geo distance."""
import pytest
from coreproject_tracker.constants import regions
from coreproject_tracker.proximity import bep40_proximity, geo_distance


def test_bep40_same_ip():
    assert bep40_proximity("192.168.1.1", "192.168.1.1") == pytest.approx(0.0)


def test_bep40_same_subnet():
    # Same /24 subnet
    assert bep40_proximity("192.168.1.1", "192.168.1.2") == pytest.approx(0.0)


def test_bep40_different_subnet():
    # Different /16
    score = bep40_proximity("192.168.1.1", "10.0.0.1")
    assert 0.0 <= score <= 10.0


def test_bep40_ipv6_same():
    assert bep40_proximity("2001:db8::1", "2001:db8::1") == pytest.approx(0.0)


def test_bep40_mixed_version():
    assert bep40_proximity("192.168.1.1", "2001:db8::1") == pytest.approx(10.0)


def test_bep40_invalid_ip():
    assert bep40_proximity("bad", "192.168.1.1") == pytest.approx(10.0)


def test_geo_same_country():
    assert geo_distance("US", "US") == regions.GEO_SAME_COUNTRY


def test_geo_adjacent_countries():
    # DE and FR are adjacent
    assert geo_distance("DE", "FR") == regions.GEO_ADJACENT


def test_geo_same_continent():
    # US and CA are both NA
    assert geo_distance("US", "CA") == regions.GEO_SAME_CONTINENT


def test_geo_different_continent():
    # US (NA) and JP (AS)
    assert geo_distance("US", "JP") == regions.GEO_DIFFERENT_CONTINENT


def test_geo_unknown_country():
    assert geo_distance(None, "US") == regions.GEO_UNKNOWN
    assert geo_distance("ZZ", "US") == regions.GEO_DIFFERENT_CONTINENT
