import ipaddress
import struct

from coreproject_tracker.enums import IP


def convert_str_to_ip_object(
    ip: str,
) -> bool | (ipaddress.IPv4Address | ipaddress.IPv6Address):
    try:
        ip = ip.strip("[]")
        return ipaddress.ip_address(ip)
    except ValueError:
        return False


def addr_to_ip_port(addr: str) -> tuple[str, int]:
    """Convert address in the format [IP]:[PORT] to a tuple (IP, PORT)."""
    if not isinstance(addr, str):
        raise ValueError("Address must be a string in the format [IP]:[PORT]")
    parts = addr.rsplit(":", 1)
    if len(parts) != 2:
        raise ValueError("Invalid address format, expecting: [IP]:[PORT]")
    return (parts[0], int(parts[1]))


def addrs_to_compact(addrs: str | list[str]) -> bytes:
    """Convert a list of addresses to compact format."""
    if isinstance(addrs, str):
        addrs = [addrs]

    compact = bytearray()
    for addr in addrs:
        ip, port = addr_to_ip_port(addr)
        ip_obj = ipaddress.ip_address(ip)
        compact.extend(ip_obj.packed + struct.pack("!H", port))

    return bytes(compact)


def convert_ipv4_coded_ipv6_to_ipv4(ip: str) -> bool | str | None:
    if not (ip_obj := convert_str_to_ip_object(ip)):
        return False

    if isinstance(ip_obj, ipaddress.IPv6Address) and ip_obj.ipv4_mapped:
        return str(ip_obj.ipv4_mapped)


def check_ip_type(ip: str) -> bool | IP:
    if not (ip_obj := convert_str_to_ip_object(ip)):
        return False

    if isinstance(ip_obj, ipaddress.IPv4Address):
        return IP.IPV4
    elif isinstance(ip_obj, ipaddress.IPv6Address):
        return IP.IPV6
    raise ValueError("`check_ip_type`: Invalid IP address type")
