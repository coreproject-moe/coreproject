import asyncio
import logging
import multiprocessing
import multiprocessing as mp
import signal
import sys

import anyio
import click

from coreproject_tracker.app import make_app
from coreproject_tracker.enums import IP
from coreproject_tracker.envs import WORKERS_COUNT
from coreproject_tracker.functions import check_ip_type
from coreproject_tracker.servers import run_udp_server as _run_udp_server

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(process)d] [%(levelname)s] %(message)s",
)


def _worker_tcp(host: str, port: int, worker_id: int) -> None:
    """TCP worker: runs Quart (HTTP + WebSocket) on its own event loop."""

    async def _serve() -> None:
        from hypercorn import Config
        from hypercorn.asyncio import serve

        config = Config()
        config.bind = [f"{host}:{port}"]
        if sys.platform != "win32":
            config.sock_options = [(2, 26, 1)]  # SO_REUSEPORT
        await serve(make_app(), config)

    logging.info("TCP worker %d started", worker_id)
    anyio.run(_serve, backend="asyncio")


def _worker_udp(host: str, port: int, worker_id: int) -> None:
    """UDP worker: runs UDP tracker server on its own event loop."""

    async def _serve() -> None:
        await _run_udp_server(host, port)

    logging.info("UDP worker %d started", worker_id)
    anyio.run(_serve, backend="asyncio")


def _spawn_workers(
    host: str,
    port: int,
    tcp_count: int,
    udp_count: int,
) -> list[multiprocessing.Process]:
    """Spawn TCP and UDP worker processes across CPU cores."""
    workers: list[multiprocessing.Process] = []

    # Spawn UDP workers
    for i in range(udp_count):
        p = multiprocessing.Process(
            target=_worker_udp,
            args=(host, port, i),
            name=f"udp-worker-{i}",
            daemon=True,
        )
        workers.append(p)

    # Spawn TCP workers
    for i in range(tcp_count):
        p = multiprocessing.Process(
            target=_worker_tcp,
            args=(host, port, i),
            name=f"tcp-worker-{i}",
            daemon=True,
        )
        workers.append(p)

    return workers


def _start_workers(workers: list[multiprocessing.Process]) -> None:
    """Start all worker processes and log."""
    for w in workers:
        w.start()
        logging.info(
            "Started %s (pid=%d)", w.name, w.pid or 0
        )


def _wait_and_cleanup(
    workers: list[multiprocessing.Process],
) -> None:
    """Wait for interrupt, then terminate all workers gracefully."""
    try:
        # Wait on any worker exiting (means crash) or Ctrl+C
        for w in workers:
            w.join()
    except KeyboardInterrupt:
        logging.info("Shutdown signal received, stopping workers...")
        for w in workers:
            if w.is_alive():
                w.terminate()
        for w in workers:
            w.join(timeout=5)
        for w in workers:
            if w.is_alive():
                w.kill()
        logging.info("All workers stopped")


@click.command()
@click.option("--host", default="127.0.0.1", help="Host to bind")
@click.option("--port", default=5000, help="Port to bind")
def main(host: str, port: int):
    """Entry point for CoreProject Tracker

    Spawns WORKERS_COUNT TCP workers + WORKERS_COUNT UDP workers,
    each running on its own CPU core with its own asyncio event loop.
    """
    ip_type = check_ip_type(host)
    if ip_type == IP.IPV6 and sys.platform == "win32":
        raise ValueError(
            "IPv6 not supported on Windows under AnyIO. "
            "See: https://github.com/agronholm/anyio/discussions/872"
        )

    tcp_count = WORKERS_COUNT
    udp_count = WORKERS_COUNT

    logging.info(
        "Starting tracker: %d TCP + %d UDP workers on %s:%d",
        tcp_count, udp_count, host, port,
    )

    workers = _spawn_workers(host, port, tcp_count, udp_count)
    _start_workers(workers)
    _wait_and_cleanup(workers)


if __name__ == "__main__":
    main()
