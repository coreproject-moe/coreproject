"""BEP27 private torrent semantics — clean room port from anacrolix/torrent.

Detects private torrents and validates that announce requests for private
torrents do not use DHT, LPD, or PEX peer discovery methods.
"""

from attrs import define


@define
class TorrentInfo:
    private: bool | None = None


def is_private(torrent_info: TorrentInfo | None) -> bool:
    """Check if a torrent is marked as private per BEP27.

    Returns True only when info is non-None AND private flag is explicitly True.
    All other cases (None info, missing flag, flag=False) return False.
    """
    if torrent_info is None:
        return False
    if torrent_info.private is None:
        return False
    return torrent_info.private


@define
class AnnounceParams:
    use_dht: bool = False
    use_lpd: bool = False
    use_pex: bool = False


def validate_private_torrent_announce(
    torrent_info: TorrentInfo | None,
    params: AnnounceParams,
) -> list[str]:
    """Validate announce parameters for private torrent compliance.

    Returns a list of violation warning strings. Empty list means no violations.
    Private torrents must not use DHT, LPD, or PEX for peer discovery.
    """
    if not is_private(torrent_info):
        return []

    violations: list[str] = []
    if params.use_dht:
        violations.append("private torrent must not use DHT")
    if params.use_lpd:
        violations.append("private torrent must not use LPD")
    if params.use_pex:
        violations.append("private torrent must not use PEX")
    return violations
