from attrs import define, field, validators

from coreproject_tracker.constants import (
    ANNOUNCE_INTERVAL,
    DEFAULT_ANNOUNCE_PEERS,
    MAX_ANNOUNCE_PEERS,
)
from coreproject_tracker.enums import EVENT_NAMES
from coreproject_tracker.validators import (
    validate_info_hash_length,
    validate_connection_id,
    validate_ip,
    validate_port,
)

__all__ = ["UdpDatastructure"]


@define
class UdpDatastructure:
    # CONSTANT
    interval: int = field(
        init=False, default=ANNOUNCE_INTERVAL, validator=validators.instance_of(int)
    )

    connection_id: bytes = field(
        validator=[validators.instance_of(bytes), validate_connection_id]
    )
    action: int = field(validator=validators.instance_of(int))
    transaction_id: int = field(validator=validators.instance_of(int))

    # Only available on ANNOUNCE
    info_hash: bytes = field(default=None, validator=[validate_info_hash_length])
    peer_id: str = field(default=None)
    downloaded: int = field(default=None)
    left: int = field(default=None)
    uploaded: int = field(default=None)
    key: int = field(default=None)
    numwant: int = field(default=DEFAULT_ANNOUNCE_PEERS)

    # Set from function call
    peers: bytes = field(default=None)  # TODO: make a log_2 based validator here
    incomplete: int = field(default=0)
    complete: int = field(default=0)

    # Might not need these
    ip: str = field(default=None, validator=[validate_ip])
    port: int = field(default=None, validator=[validate_port])

    # Derived
    event_name: EVENT_NAMES = field(default=None)

    def __attrs_post_init__(self):
        self.numwant = min(self.numwant, MAX_ANNOUNCE_PEERS)
