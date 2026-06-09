"""Tests for geo module."""
import pytest
from coreproject_tracker.geo import (
    GEO_CACHE_TTL,
    GEO_MISS_SENTINEL,
    GEO_MISS_TTL,
    get_country_info,
    get_geo_stats,
)


def test_geo_stats_not_loaded():
    stats = get_geo_stats()
    assert stats["provider"] == "IPLocate.io"
    assert stats["license"] == "CC BY-SA 4.0"
    assert stats["loaded"] in (True, False)


def test_geo_stats_fields():
    stats = get_geo_stats()
    assert "countries_count" in stats
    assert "ipv4_blocks_count" in stats
    assert "ipv6_blocks_count" in stats
    assert "attribution_url" in stats


def test_country_info_unknown():
    info = get_country_info("ZZ")
    assert info["code"] == "ZZ"
    assert info["continent"] == ""


def test_ttl_constants():
    assert GEO_CACHE_TTL > 0
    assert GEO_MISS_TTL > 0
    assert GEO_MISS_SENTINEL == "__MISS__"
