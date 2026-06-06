"""Tests for coreproject_tracker.functions.events - event conversions."""
import pytest
from coreproject_tracker.enums import EVENT_NAMES
from coreproject_tracker.functions import (
    convert_event_id_to_event_enum,
    convert_event_name_to_event_enum,
)


class TestConvertEventIdToEventEnum:
    def test_update(self):
        assert convert_event_id_to_event_enum(0) == EVENT_NAMES.UPDATE

    def test_complete(self):
        assert convert_event_id_to_event_enum(1) == EVENT_NAMES.COMPLETE

    def test_start(self):
        assert convert_event_id_to_event_enum(2) == EVENT_NAMES.START

    def test_stop(self):
        assert convert_event_id_to_event_enum(3) == EVENT_NAMES.STOP

    def test_pause(self):
        assert convert_event_id_to_event_enum(4) == EVENT_NAMES.PAUSE

    def test_invalid_id(self):
        with pytest.raises(ValueError, match="not supported"):
            convert_event_id_to_event_enum(99)

    def test_negative_id(self):
        with pytest.raises(ValueError, match="not supported"):
            convert_event_id_to_event_enum(-1)


class TestConvertEventNameToEventEnum:
    def test_update(self):
        assert convert_event_name_to_event_enum("update") == EVENT_NAMES.UPDATE

    def test_completed(self):
        assert convert_event_name_to_event_enum("completed") == EVENT_NAMES.COMPLETE

    def test_started(self):
        assert convert_event_name_to_event_enum("started") == EVENT_NAMES.START

    def test_stopped(self):
        assert convert_event_name_to_event_enum("stopped") == EVENT_NAMES.STOP

    def test_paused(self):
        assert convert_event_name_to_event_enum("paused") == EVENT_NAMES.PAUSE

    def test_case_insensitive(self):
        assert convert_event_name_to_event_enum("STOPPED") == EVENT_NAMES.STOP
        assert convert_event_name_to_event_enum("Stopped") == EVENT_NAMES.STOP

    def test_invalid_name(self):
        with pytest.raises(ValueError, match="not supported"):
            convert_event_name_to_event_enum("invalid_event")

    def test_none_raises(self):
        with pytest.raises(ValueError, match="is None"):
            convert_event_name_to_event_enum(None)
