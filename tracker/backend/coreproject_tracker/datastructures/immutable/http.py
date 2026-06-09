from attrs import define, field, validators

from coreproject_tracker.constants import DEFAULT_ANNOUNCE_PEERS, MAX_ANNOUNCE_PEERS
from coreproject_tracker.converters import (
    convert_ip,
    convert_to_url_bytes,
)
from coreproject_tracker.enums import EVENT_NAMES
from coreproject_tracker.validators import (
    validate_info_hash_length,
    validate_ip,
    validate_port,
)

__all__ = ["HttpDatastructure"]


@define
class HttpDatastructure:
    info_hash_raw: bytes = field(
        converter=convert_to_url_bytes,
        validator=[validate_info_hash_length],
    )
    port: int = field(converter=int, validator=[validate_port])
    left: int = field(converter=int)
    numwant: int = field(converter=int)
    peer_id: str = field(validator=validators.instance_of(str))
    peer_ip: str = field(converter=convert_ip, validator=[validate_ip])

    event_name: EVENT_NAMES = field(default=None)
    private: bool = field(default=False, converter=bool)

    # Derived
    info_hash: str = field(init=False)

    def __attrs_post_init__(self) -> None:
        self.numwant = min(self.numwant or DEFAULT_ANNOUNCE_PEERS, MAX_ANNOUNCE_PEERS)

        # Derived Data
        self.info_hash = self.info_hash_raw.hex()
