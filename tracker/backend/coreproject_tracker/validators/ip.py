from typing import Any, Optional

from attrs import Attribute

from coreproject_tracker.functions import convert_str_to_ip_object


def validate_ip(inst: Any, attr: Attribute, value: Optional[str]) -> None:
    if value and convert_str_to_ip_object(value):
        raise ValueError(f"`{value}` is not a valid ip.")
