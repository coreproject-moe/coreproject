"""BEP14 LPD validation for private torrent compliance.

Validates that LPD (Local Peer Discovery) is not used with private torrents
per BEP27 requirements.
"""

from coreproject_tracker.bep.bep27 import (
    AnnounceParams,
    TorrentInfo,
    validate_private_torrent_announce,
)


def validate_lpd_for_torrent(torrent_info: TorrentInfo | None) -> list[str]:
    """Check if LPD is allowed for a given torrent.

    Returns a list of violation strings. Empty list means LPD is allowed.
    LPD is prohibited for private torrents per BEP27.
    """
    params = AnnounceParams(use_lpd=True)
    return validate_private_torrent_announce(torrent_info, params)
