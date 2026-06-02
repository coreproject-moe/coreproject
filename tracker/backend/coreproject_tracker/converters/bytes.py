__all__ = ["convert_binary_string_to_bytes"]


def convert_binary_string_to_bytes(value: str | None) -> bytes | None:
    return value.encode("latin1") if value else None
