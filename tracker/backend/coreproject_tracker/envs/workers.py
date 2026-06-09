import multiprocessing
import os

__all__ = ["WORKERS_COUNT"]

WORKERS_COUNT = int(
    os.environ.get(
        "WORKERS_COUNT",
        max(
            2,
            multiprocessing.cpu_count() - 2,
        ),
    ),
)
