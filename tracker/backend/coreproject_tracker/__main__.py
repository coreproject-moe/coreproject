import asyncio
import functools
import logging
import sys
from concurrent.futures import ProcessPoolExecutor
from typing import Any

import anyio
import click
from hypercorn import Config
from hypercorn.asyncio import serve  # type: ignore

from coreproject_tracker.app import make_app
from coreproject_tracker.enums import IP
from coreproject_tracker.envs import WORKERS_COUNT
from coreproject_tracker.functions import check_ip_type
from coreproject_tracker.servers import run_udp_server as _run_udp_server

logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s] [%(process)d] [%(levelname)s] %(message)s"
)


async def run_udp_server_async(host: str, port: int) -> None:
    # There has to be one Web Server on same port as udp server to avoid redis re-initialization
    async with anyio.create_task_group() as tg:
        tg.start_soon(functools.partial(_run_udp_server, host, port))


async def create_servable_app(host: str, port: int) -> Any:
    """Create a servable app for the HTTP server"""
    config = Config()
    config.bind = config.insecure_bind = [f"{host}:{port}"]
    return await serve(make_app(), config)


def run_udp_server(host: str, port: int) -> None:
    anyio.run(run_udp_server_async, host, port, backend="asyncio")


def run_http_websocket_server(host: str, port: int) -> None:
    config = Config()
    config.bind = [f"{host}:{port}"]
    anyio.run(create_servable_app, host, port, backend="asyncio")


async def _main_async_wrapper(host: str, port: int) -> None:
    """Async context for server management"""
    ip_type = check_ip_type(host)
    if ip_type == IP.IPV6:
        if sys.platform == "win32":
            raise ValueError(
                "IPv6 not supported on Windows under AnyIO. "
                + "See:https://github.com/agronholm/anyio/discussions/872"
            )

    loop = asyncio.get_event_loop()

    with ProcessPoolExecutor() as executor:
        # Run one instance of UDP server in the main process
        loop.run_in_executor(executor, run_udp_server, host, port)

        for _ in range(WORKERS_COUNT - 1):
            loop.run_in_executor(executor, run_http_websocket_server, host, port)


@click.command()
@click.option("--host", default="127.0.0.1", help="Host to bind")
@click.option("--port", default=5000, help="Port to bind")
def main(host: str, port: int):
    """Entry point for CoreProject Tracker"""

    try:
        asyncio.run(_main_async_wrapper(host, port))
    except KeyboardInterrupt:
        logging.info("Application shutdown complete")


if __name__ == "__main__":
    main()
