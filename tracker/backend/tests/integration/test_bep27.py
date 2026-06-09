"""BEP27 private torrent semantics — clean room port from anacrolix/torrent.

Verifies private torrent detection and announce validation.
"""

import pytest

from coreproject_tracker.bep.bep27 import (
    AnnounceParams,
    TorrentInfo,
    is_private,
    validate_private_torrent_announce,
)

pytestmark = pytest.mark.integration


class TestIsPrivate:
    def test_no_info_returns_false(self):
        assert is_private(None) is False

    def test_flag_absent_returns_false(self):
        info = TorrentInfo(private=None)
        assert is_private(info) is False

    def test_flag_false_returns_false(self):
        info = TorrentInfo(private=False)
        assert is_private(info) is False

    def test_flag_true_returns_true(self):
        info = TorrentInfo(private=True)
        assert is_private(info) is True

    def test_default_construction_not_private(self):
        info = TorrentInfo()
        assert is_private(info) is False


class TestValidatePrivateTorrentAnnounce:
    def test_public_torrent_no_violations(self):
        info = TorrentInfo(private=False)
        params = AnnounceParams(use_dht=True, use_lpd=True, use_pex=True)
        assert validate_private_torrent_announce(info, params) == []

    def test_none_info_no_violations(self):
        params = AnnounceParams(use_dht=True, use_lpd=True, use_pex=True)
        assert validate_private_torrent_announce(None, params) == []

    def test_private_with_dht_violation(self):
        info = TorrentInfo(private=True)
        params = AnnounceParams(use_dht=True)
        violations = validate_private_torrent_announce(info, params)
        assert len(violations) == 1
        assert "DHT" in violations[0]

    def test_private_with_lpd_violation(self):
        info = TorrentInfo(private=True)
        params = AnnounceParams(use_lpd=True)
        violations = validate_private_torrent_announce(info, params)
        assert len(violations) == 1
        assert "LPD" in violations[0]

    def test_private_with_pex_violation(self):
        info = TorrentInfo(private=True)
        params = AnnounceParams(use_pex=True)
        violations = validate_private_torrent_announce(info, params)
        assert len(violations) == 1
        assert "PEX" in violations[0]

    def test_private_with_all_discovery_methods(self):
        info = TorrentInfo(private=True)
        params = AnnounceParams(use_dht=True, use_lpd=True, use_pex=True)
        violations = validate_private_torrent_announce(info, params)
        assert len(violations) == 3

    def test_private_clean_announce(self):
        info = TorrentInfo(private=True)
        params = AnnounceParams()
        assert validate_private_torrent_announce(info, params) == []
