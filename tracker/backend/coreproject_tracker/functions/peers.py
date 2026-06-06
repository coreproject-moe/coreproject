"""Geo-aware peer selection with oversampling + ranking."""

import json

from coreproject_tracker.constants import DEFAULT_ANNOUNCE_PEERS, MAX_ANNOUNCE_PEERS
from coreproject_tracker.enums import REDIS_NAMESPACE_ENUM
from coreproject_tracker.functions import hmget, zcard, zrandmember_with_scores
from coreproject_tracker.functions.weight import RankedPeer, rank_peers
from coreproject_tracker.geo import resolve_country

# Oversampling multiplier: fetch N*numwant peers, rank them, return top numwant.
PEER_POOL_MULTIPLIER = 3


async def select_peers(
    requester_ip: str,
    info_hash: str,
    numwant: int,
    namespace: REDIS_NAMESPACE_ENUM,
) -> list[RankedPeer]:
    """Geo-aware peer selection with oversampling + ranking.

    Pipeline: resolve requester country -> fetch peer pool with scores ->
    fetch peer data -> rank by geo+BEP40+activity -> return top N.
    """
    numwant = min(max(numwant, DEFAULT_ANNOUNCE_PEERS), MAX_ANNOUNCE_PEERS)

    # Resolve requester country (non-blocking, cached)
    requester_country = await resolve_country(requester_ip)

    # Determine pool size: oversample but cap at actual swarm size
    swarm_size = await zcard(info_hash, namespace)
    pool_size = min(numwant * PEER_POOL_MULTIPLIER, swarm_size)

    # Fetch peer pool with base scores
    peer_pool = await zrandmember_with_scores(info_hash, pool_size, namespace)
    if not peer_pool:
        return []

    # Fetch peer data via hmget
    peer_keys = [key for key, _ in peer_pool]
    peer_json_list = await hmget(info_hash, peer_keys, namespace)

    # Build data map
    peer_data_map: dict[str, dict] = {}
    for key, raw_json in zip(peer_keys, peer_json_list):
        if not raw_json:
            continue
        try:
            peer_data_map[key] = json.loads(raw_json)
        except (json.JSONDecodeError, TypeError):
            continue

    # Rank and return top N
    ranked = rank_peers(
        requester_ip, requester_country, peer_pool, peer_data_map, numwant
    )
    return ranked
