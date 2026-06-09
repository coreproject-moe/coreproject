"""Tests for rollback transaction context manager."""
import pytest
from coreproject_tracker.datastructures import MutableBox
from coreproject_tracker.transaction import rollback_on_exception


def test_rollback_restores_values():
    box1 = MutableBox[int](0)
    box2 = MutableBox[list]([])
    try:
        with rollback_on_exception(box1, box2):
            box1.value = 42
            box2.value = ["a"]
            raise ValueError("oops")
    except ValueError:
        pass
    assert box1.value == 0
    assert box2.value == []


def test_no_rollback_on_success():
    box = MutableBox[int](0)
    with rollback_on_exception(box):
        box.value = 99
    assert box.value == 99


def test_rollback_deep_copy():
    box = MutableBox[list]([])
    try:
        with rollback_on_exception(box):
            box.value.append("item")
            raise RuntimeError()
    except RuntimeError:
        pass
    assert box.value == []
