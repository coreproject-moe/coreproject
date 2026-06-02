import struct

__all__ = ["to_uint32", "from_uint16", "from_uint32", "from_uint64"]


def to_uint32(value: int) -> bytes:
    return struct.pack(">I", value)


def from_uint16(data: bytes) -> int:
    return struct.unpack(">H", data)[0]


def from_uint32(data: bytes) -> int:
    return struct.unpack(">I", data)[0]


def from_uint64(data: bytes) -> int:
    return struct.unpack(">Q", data)[0]
