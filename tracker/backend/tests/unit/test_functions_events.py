"""Tests for coreproject_tracker.functions.events - event conversions."""
import pytest
from coreproject_tracker.enums import EVENT_NAMES
from coreproject_tracker.functions import (
    convert_event_id_to_event_enum,
    convert_event_name_to_event_enum,
)


def test_convert_event_id_update():
    assert convert_event_id_to_event_enum(0) == EVENT_NAMES.UPDATE


def test_convert_event_id_complete():
    assert convert_event_id_to_event_enum(1) == EVENT_NAMES.COMPLETE


def test_convert_event_id_start():
    assert convert_event_id_to_event_enum(2) == EVENT_NAMES.START


def test_convert_event_id_stop():
    assert convert_event_id_to_event_enum(3) == EVENT_NAMES.STOP


def test_convert_event_id_pause():
    assert convert_event_id_to_event_enum(4) == EVENT_NAMES.PAUSE


def test_convert_event_id_invalid():
    with pytest.raises(ValueError, match="not supported"):
        convert_event_id_to_event_enum(99)


def test_convert_event_id_negative():
    with pytest.raises(ValueError, match="not supported"):
        convert_event_id_to_event_enum(-1)


def test_convert_event_name_update():
    assert convert_event_name_to_event_enum("update") == EVENT_NAMES.UPDATE


def test_convert_event_name_completed():
    assert convert_event_name_to_event_enum("completed") == EVENT_NAMES.COMPLETE


def test_convert_event_name_started():
    assert convert_event_name_to_event_enum("started") == EVENT_NAMES.START


def test_convert_event_name_stopped():
    assert convert_event_name_to_event_enum("stopped") == EVENT_NAMES.STOP


def test_convert_event_name_paused():
    assert convert_event_name_to_event_enum("paused") == EVENT_NAMES.PAUSE


def test_convert_event_name_case_insensitive():
    assert convert_event_name_to_event_enum("STOPPED") == EVENT_NAMES.STOP
    assert convert_event_name_to_event_enum("Stopped") == EVENT_NAMES.STOP


def test_convert_event_name_invalid():
    with pytest.raises(ValueError, match="not supported"):
        convert_event_name_to_event_enum("invalid_event")


def test_convert_event_name_none_raises():
    with pytest.raises(ValueError, match="is None"):
        convert_event_name_to_event_enum(None)
