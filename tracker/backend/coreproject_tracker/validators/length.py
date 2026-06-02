from typing import Any, Optional

from attrs import Attribute

__all__ = ["validate_20_length", "validate_info_hash_length"]


def validate_20_length(inst: Any, attr: Attribute, value: Optional[bytes]) -> None:
    if (length := value) and len(length) != 20:
        raise ValueError(f"`{attr}` of `{inst}` is {value} which not 20 bytes")


def validate_info_hash_length(
    inst: Any, attr: Attribute, value: Optional[bytes]
) -> None:
    """Validate info hash is SHA-1 (20 bytes) or SHA-256 (32 bytes) per BEP-52."""
    if (length := value) and len(length) not in (20, 32):
        raise ValueError(
            f"`{attr}` of `{inst}` is {value} which is not 20 or 32 bytes"
        )
