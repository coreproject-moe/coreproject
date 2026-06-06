"""Tests for event conversion functions."""
import pytest
from coreproject_tracker.enums import EVENT_NAMES
from coreproject_tracker.functions import (
    convert_event_id_to_event_enum,
    convert_event_name_to_event_enum,
)


def test_event_id_map():
    assert convert_event_id_to_event_enum(0) == EVENT_NAMES.UPDATE
    assert convert_event_id_to_event_enum(1) == EVENT_NAMES.COMPLETE
    assert convert_event_id_to_event_enum(2) == EVENT_NAMES.START
    assert convert_event_id_to_event_enum(3) == EVENT_NAMES.STOP
    assert convert_event_id_to_event_enum(4) == EVENT_NAMES.PAUSE


def test_event_id_invalid():
    with pytest.raises(ValueError):
        convert_event_id_to_event_enum(99)
    with pytest.raises(ValueError):
        convert_event_id_to_event_enum(-1)


def test_event_name_map():
    assert convert_event_name_to_event_enum("update") == EVENT_NAMES.UPDATE
    assert convert_event_name_to_event_enum("completed") == EVENT_NAMES.COMPLETE
    assert convert_event_name_to_event_enum("started") == EVENT_NAMES.START
    assert convert_event_name_to_event_enum("stopped") == EVENT_NAMES.STOP
    assert convert_event_name_to_event_enum("paused") == EVENT_NAMES.PAUSE


def test_event_name_case_insensitive():
    assert convert_event_name_to_event_enum("STOPPED") == EVENT_NAMES.STOP
    assert convert_event_name_to_event_enum("Stopped") == EVENT_NAMES.STOP


def test_event_name_invalid():
    with pytest.raises(ValueError):
        convert_event_name_to_event_enum("invalid")
    with pytest.raises(ValueError):
        convert_event_name_to_event_enum(None)
