"""Tracker announce lifecycle — clean room port from anacrolix/torrent.

Tests announce event scheduling, priority ordering, error backoff,
and queue concurrency limits against Go reference behavior.
"""

import pytest
from datetime import datetime, timezone, timedelta

from coreproject_tracker.bep.announce_lifecycle import (
    AnnounceEvent,
    AnnounceQueue,
    AnnounceState,
    NextAnnounceResult,
    next_announce_event,
)

pytestmark = pytest.mark.integration


_NOW = datetime(2025, 6, 1, 12, 0, 0, tzinfo=timezone.utc)


class TestNextAnnounceEvent:
    def test_event_priority_ordering(self):
        assert AnnounceEvent.STARTED < AnnounceEvent.STOPPED
        assert AnnounceEvent.STOPPED < AnnounceEvent.COMPLETED
        assert AnnounceEvent.COMPLETED < AnnounceEvent.NONE

    def test_never_announced_returns_started(self):
        state = AnnounceState(announced=False)
        result = next_announce_event(state, torrent_active=True, now=_NOW)
        assert result.event == AnnounceEvent.STARTED
        assert result.immediate is True

    def test_torrent_dropped_returns_stopped(self):
        state = AnnounceState(announced=True, last_event=AnnounceEvent.NONE)
        result = next_announce_event(state, torrent_active=False, now=_NOW)
        assert result.event == AnnounceEvent.STOPPED
        assert result.immediate is True

    def test_torrent_dropped_with_error_skips(self):
        state = AnnounceState(
            announced=True, error="tracker unreachable"
        )
        result = next_announce_event(state, torrent_active=False, now=_NOW)
        assert result.event == AnnounceEvent.NONE

    def test_torrent_dropped_never_announced_skips(self):
        state = AnnounceState(announced=False)
        result = next_announce_event(state, torrent_active=False, now=_NOW)
        assert result.event == AnnounceEvent.NONE

    def test_torrent_dropped_stopped_already_sent_skips(self):
        state = AnnounceState(
            announced=True, last_event=AnnounceEvent.STOPPED
        )
        result = next_announce_event(state, torrent_active=False, now=_NOW)
        assert result.event == AnnounceEvent.NONE

    def test_completed_detection(self):
        state = AnnounceState(
            announced=True,
            last_ok_time=_NOW - timedelta(minutes=5),
        )
        result = next_announce_event(
            state, torrent_active=True, have_all_pieces=True, now=_NOW
        )
        assert result.event == AnnounceEvent.COMPLETED
        assert result.immediate is True

    def test_error_backoff_enforced(self):
        state = AnnounceState(
            announced=True,
            error="tracker timeout",
            last_ok_time=_NOW - timedelta(seconds=30),
        )
        result = next_announce_event(state, torrent_active=True, now=_NOW)
        assert result.event == AnnounceEvent.NONE
        assert "backoff" in result.reason

    def test_error_backoff_expired(self):
        state = AnnounceState(
            announced=True,
            error="tracker timeout",
            last_ok_time=_NOW - timedelta(minutes=2),
        )
        result = next_announce_event(state, torrent_active=True, now=_NOW)
        assert result.event == AnnounceEvent.NONE
        assert result.immediate is False

    def test_regular_interval(self):
        state = AnnounceState(
            announced=True,
            last_ok_time=_NOW - timedelta(minutes=10),
            last_event=AnnounceEvent.NONE,
        )
        result = next_announce_event(state, torrent_active=True, now=_NOW)
        assert result.event == AnnounceEvent.NONE
        assert result.immediate is False

    def test_default_now_parameter(self):
        state = AnnounceState(announced=False)
        result = next_announce_event(state, torrent_active=True)
        assert result.event == AnnounceEvent.STARTED
        assert result.immediate is True


class TestAnnounceQueue:
    def test_priority_ordering(self):
        queue = AnnounceQueue()
        queue.add("http://tracker1", "ih1", AnnounceEvent.NONE)
        queue.add("http://tracker1", "ih2", AnnounceEvent.STARTED)
        queue.add("http://tracker1", "ih3", AnnounceEvent.STOPPED)

        first = queue.pop_next()
        assert first["info_hash"] == "ih2"

    def test_overdue_jumps_queue(self):
        queue = AnnounceQueue()
        queue.add("http://tracker1", "ih1", AnnounceEvent.NONE, overdue=False)
        queue.add("http://tracker1", "ih2", AnnounceEvent.NONE, overdue=True)

        first = queue.pop_next()
        assert first["info_hash"] == "ih2"

    def test_max_concurrent_per_tracker(self):
        queue = AnnounceQueue()
        queue.add("http://tracker1", "ih1", AnnounceEvent.STARTED)
        queue.add("http://tracker1", "ih2", AnnounceEvent.STOPPED)
        queue.add("http://tracker1", "ih3", AnnounceEvent.COMPLETED)

        first = queue.pop_next()
        assert first is not None
        second = queue.pop_next()
        assert second is not None
        third = queue.pop_next()
        assert third is None

    def test_different_trackers_independent(self):
        queue = AnnounceQueue()
        queue.add("http://tracker1", "ih1", AnnounceEvent.STARTED)
        queue.add("http://tracker2", "ih2", AnnounceEvent.STOPPED)

        first = queue.pop_next()
        assert first is not None
        second = queue.pop_next()
        assert second is not None

    def test_finish_frees_slot(self):
        queue = AnnounceQueue()
        queue.add("http://tracker1", "ih1", AnnounceEvent.STARTED)
        queue.add("http://tracker1", "ih2", AnnounceEvent.STOPPED)
        queue.add("http://tracker1", "ih3", AnnounceEvent.COMPLETED)

        queue.pop_next()
        queue.pop_next()
        assert queue.pop_next() is None

        queue.finish("http://tracker1")
        next_entry = queue.pop_next()
        assert next_entry is not None
        assert next_entry["info_hash"] == "ih3"

    def test_empty_queue(self):
        queue = AnnounceQueue()
        assert queue.is_empty() is True
        assert queue.size == 0
        assert queue.pop_next() is None

    def test_size_tracking(self):
        queue = AnnounceQueue()
        queue.add("http://t1", "ih1", AnnounceEvent.NONE)
        queue.add("http://t1", "ih2", AnnounceEvent.NONE)
        assert queue.size == 2
        queue.pop_next()
        assert queue.size == 1
