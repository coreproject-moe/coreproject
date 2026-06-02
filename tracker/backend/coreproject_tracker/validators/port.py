from typing import Any, Optional

from attrs import Attribute

__all__ = ["validate_port"]


def validate_port(inst: Any, attr: Attribute, value: Optional[int]) -> None:
    if value and (value <= 0 or value >= 65535):
        raise ValueError(
            f"`{attr}` of `{inst}` is {value} which is not in range(0, 65535)"
        )
