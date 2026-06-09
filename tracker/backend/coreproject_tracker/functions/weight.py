from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from coreproject_tracker.datastructures import RedisDatastructure

from coreproject_tracker.bep.bep40 import bep40_priority
from coreproject_tracker.proximity import geo_distance


@dataclass(slots=True)
class RankedPeer:
    peer_key: str
    peer_ip: str
    port: int
    peer_id: str = ""
    country: str | None = None
    base_score: float = 0.0
    combined_score: float = 0.0
    left: float | None = None
    downloaded: int = 0
    uploaded: int = 0


def calculate_weight(peer_data: "RedisDatastructure") -> float:
    """Calculate base priority score for a peer.

    Lower score = higher priority (for Redis ZSET ordering).
    Range: 0.0 (best) to 5.0 (worst).
    """
    score = 2.5
    if peer_data.left == 0:
        score -= 1.0
    if peer_data.downloaded:
        score -= 0.5
    if peer_data.uploaded:
        score -= 0.3
    return max(0.0, score)


def rank_peers(
    requester_ip: str,
    requester_country: str | None,
    peer_pool: list[tuple[str, float]],
    peer_data_map: dict[str, dict],
    numwant: int,
) -> list[RankedPeer]:
    """Rank peers by combined geo + BEP40 + activity score."""
    if not peer_pool:
        return []

    ranked: list[RankedPeer] = []

    for peer_key, base_score in peer_pool:
        pdata = peer_data_map.get(peer_key, {})
        peer_ip = pdata.get("peer_ip", "")
        port = pdata.get("port", 0)
        country = pdata.get("country")

        if not peer_ip:
            continue

        geo_pen = geo_distance(requester_country, country)
        net_pen = (bep40_priority(requester_ip, peer_ip, 0, port) & 0xFFFFFFFF) / 0xFFFFFFFF * 10.0
        combined = base_score + geo_pen + net_pen

        ranked.append(RankedPeer(
            peer_key=peer_key,
            peer_ip=peer_ip,
            port=port,
            peer_id=pdata.get("peer_id", ""),
            country=country,
            base_score=base_score,
            combined_score=combined,
            left=pdata.get("left"),
            downloaded=pdata.get("downloaded", 0),
            uploaded=pdata.get("uploaded", 0),
        ))

    ranked.sort(key=lambda p: p.combined_score)
    return ranked[:numwant]
