from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from coreproject_tracker.datastructures import RedisDatastructure


def calculate_weight(peer_data: "RedisDatastructure") -> float:
    weight = 1.0
    if peer_data.left == 0:
        weight *= 2
    if peer_data.downloaded:
        weight *= 1.5
    if peer_data.uploaded:
        weight *= 1.2
    return weight