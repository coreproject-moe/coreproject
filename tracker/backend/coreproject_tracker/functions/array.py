import random
from typing import Iterable

__all__ = ["get_n_random_items"]


async def get_n_random_items[T](array: Iterable[T], n: int) -> list[T]:
    """Given a set of array elements, returns n random elements from array"""
    # Convert to list if it's not already one
    if not isinstance(array, list):
        array = list(array)
    ret: list[T] = []

    try:
        ret = random.sample(array, n)
    except ValueError:
        ret = array
        
    return ret
