from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from coreproject_tracker.datastructures import RedisDatastructure


def calculate_weight(peer_data: RedisDatastructure) -> float:
    """
    Calculate the weight of a peer for weighted selection.

    Args:
        peer_data: RedisDatastructure

    Returns:
        float: computed weight
    """
    weight = 1.0

    if peer_data.left == 0:
        weight *= 2

    return weight
