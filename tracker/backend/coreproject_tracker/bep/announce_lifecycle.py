"""Tracker announce lifecycle — clean room port from anacrolix/torrent.

Implements announce event scheduling, priority ordering, and queue management
as observed in the Go client-tracker-announcer implementation.
"""

import enum
from attrs import define
from datetime import datetime, timezone


class AnnounceEvent(enum.IntEnum):
    NONE = -1
    COMPLETED = -2
    STOPPED = -3
    STARTED = -4


_MIN_ERROR_BACKOFF_SECONDS = 60
_MAX_CONCURRENT_ANNOUNCES_PER_TRACKER = 2


@define
class AnnounceState:
    last_event: AnnounceEvent = AnnounceEvent.NONE
    interval: int = 1800
    last_ok_time: datetime | None = None
    num_peers: int = 0
    error: str | None = None
    announced: bool = False


@define
class NextAnnounceResult:
    event: AnnounceEvent
    immediate: bool = False
    reason: str = ""


def next_announce_event(
    state: AnnounceState,
    torrent_active: bool,
    have_all_pieces: bool = False,
    now: datetime | None = None,
) -> NextAnnounceResult:
    """Determine the next announce event based on state and torrent status.

    Priority rules (most urgent first):
    1. Torrent dropped + last announce errored -> skip
    2. Torrent dropped + never announced -> skip
    3. Torrent dropped + already sent STOPPED -> skip
    4. Torrent dropped + still active -> STOPPED immediately
    5. Last errored + within backoff window -> skip
    6. Saw incomplete + now complete -> COMPLETED
    7. Never announced -> STARTED
    8. Default -> NONE at interval
    """
    if now is None:
        now = datetime.now(timezone.utc)

    if not torrent_active:
        if state.error is not None:
            return NextAnnounceResult(
                AnnounceEvent.NONE, reason="torrent dropped with error"
            )
        if not state.announced:
            return NextAnnounceResult(
                AnnounceEvent.NONE, reason="torrent dropped never announced"
            )
        if state.last_event == AnnounceEvent.STOPPED:
            return NextAnnounceResult(
                AnnounceEvent.NONE, reason="stopped already sent"
            )
        return NextAnnounceResult(
            AnnounceEvent.STOPPED,
            immediate=True,
            reason="torrent dropped, need to stop",
        )

    if state.error is not None and state.last_ok_time is not None:
        elapsed = (now - state.last_ok_time).total_seconds()
        if elapsed < _MIN_ERROR_BACKOFF_SECONDS:
            return NextAnnounceResult(
                AnnounceEvent.NONE,
                reason=f"error backoff, {elapsed:.0f}s < {_MIN_ERROR_BACKOFF_SECONDS}s",
            )

    if have_all_pieces and state.announced:
        return NextAnnounceResult(
            AnnounceEvent.COMPLETED,
            immediate=True,
            reason="data completed",
        )

    if not state.announced:
        return NextAnnounceResult(
            AnnounceEvent.STARTED,
            immediate=True,
            reason="first announce",
        )

    return NextAnnounceResult(
        AnnounceEvent.NONE,
        immediate=False,
        reason="regular interval",
    )


class AnnounceQueue:
    """Priority-sorted announce queue with per-tracker concurrency limits."""

    def __init__(self) -> None:
        self._entries: list[dict[str, object]] = []
        self._tracker_counts: dict[str, int] = {}

    def add(self, tracker_url: str, info_hash: str, event: AnnounceEvent, overdue: bool = False) -> None:
        entry = {
            "tracker": tracker_url,
            "info_hash": info_hash,
            "event": event,
            "overdue": overdue,
            "priority": self._entry_priority(event, overdue),
        }
        self._entries.append(entry)
        self._entries.sort(key=lambda e: e["priority"])
        self._tracker_counts[tracker_url] = self._tracker_counts.get(tracker_url, 0)

    def _entry_priority(self, event: AnnounceEvent, overdue: bool) -> float:
        base = float(event)
        if overdue:
            base -= 100
        return base

    def pop_next(self) -> dict[str, object] | None:
        """Pop the highest priority announce that is within tracker limits."""
        for i, entry in enumerate(self._entries):
            tracker = entry["tracker"]
            current = self._tracker_counts.get(tracker, 0)
            if current < _MAX_CONCURRENT_ANNOUNCES_PER_TRACKER:
                self._tracker_counts[tracker] = current + 1
                return self._entries.pop(i)
        return None

    def finish(self, tracker_url: str) -> None:
        """Mark a tracker announce as completed (decrement counter)."""
        self._tracker_counts[tracker_url] = max(
            0, self._tracker_counts.get(tracker_url, 0) - 1
        )

    @property
    def size(self) -> int:
        return len(self._entries)

    def is_empty(self) -> bool:
        return len(self._entries) == 0
