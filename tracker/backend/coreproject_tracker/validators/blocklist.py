import ipaddress
import logging
from pathlib import Path

_networks: list[ipaddress.IPv4Network | ipaddress.IPv6Network] = []


def _load_blocklist(path: str) -> None:
    global _networks
    file = Path(path)
    if not file.exists():
        logging.warning(f"Blocklist file not found: {path}")
        return

    networks = []
    with file.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                if "/" in line:
                    networks.append(ipaddress.ip_network(line, strict=False))
                else:
                    addr = ipaddress.ip_address(line)
                    prefix = 32 if addr.version == 4 else 128
                    networks.append(
                        ipaddress.ip_network(f"{addr}/{prefix}", strict=False)
                    )
            except ValueError:
                logging.warning(f"Invalid blocklist entry: {line}")
    _networks = networks
    logging.info(f"Loaded {len(networks)} blocklist entries from {path}")


def is_blocked(ip: str) -> bool:
    if not _networks:
        return False
    try:
        addr = ipaddress.ip_address(ip.strip("[]"))
        for net in _networks:
            if addr.version == net.version and addr in net:
                return True
    except ValueError:
        pass
    return False
