def bytes_to_bin_str(byte: bytes) -> str:
    return byte.decode("latin-1")


def hex_str_to_bin_str(hex_str: str) -> str:
    return bytes.fromhex(hex_str).decode("latin1")
