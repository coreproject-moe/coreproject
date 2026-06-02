from coreproject_tracker.functions import convert_ipv4_coded_ipv6_to_ipv4

__all__ = ["convert_ip"]


def convert_ip(value: str) -> str:
    if (ipv4 := convert_ipv4_coded_ipv6_to_ipv4(value)) is False:
        raise ValueError(f"Invalid IPv4 address: {value}")
    return ipv4 if isinstance(ipv4, str) else value
