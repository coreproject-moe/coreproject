"""Tests for enum definitions."""
from coreproject_tracker.enums import ACTIONS, EVENT_NAMES, IP, REDIS_NAMESPACE_ENUM


def test_actions():
    assert ACTIONS.CONNECT == 0
    assert ACTIONS.ANNOUNCE == 1
    assert ACTIONS.SCRAPE == 2
    assert ACTIONS.ERROR == 3


def test_event_names():
    assert EVENT_NAMES.UPDATE is not None
    assert EVENT_NAMES.COMPLETE is not None
    assert EVENT_NAMES.START is not None
    assert EVENT_NAMES.STOP is not None
    assert EVENT_NAMES.PAUSE is not None


def test_ip_enum():
    assert IP.IPV4 is not None
    assert IP.IPV6 is not None


def test_redis_namespace():
    assert REDIS_NAMESPACE_ENUM.HTTP_UDP is not None
    assert REDIS_NAMESPACE_ENUM.WEBSOCKET is not None
    assert REDIS_NAMESPACE_ENUM.HTTP_UDP.value != REDIS_NAMESPACE_ENUM.WEBSOCKET.value
