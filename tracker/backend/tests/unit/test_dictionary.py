"""Tests for dictionary decoding."""
import pytest
from coreproject_tracker.functions import decode_dictionary


@pytest.mark.asyncio
async def test_decode_dict_simple():
    assert await decode_dictionary({b"k": b"v"}) == {"k": "v"}


@pytest.mark.asyncio
async def test_decode_dict_nested():
    assert await decode_dictionary({b"a": {b"b": b"c"}}) == {"a": {"b": "c"}}


@pytest.mark.asyncio
async def test_decode_dict_list():
    assert await decode_dictionary([b"a", b"b"]) == ["a", "b"]


@pytest.mark.asyncio
async def test_decode_dict_passthrough():
    assert await decode_dictionary("str") == "str"
    assert await decode_dictionary(42) == 42
    assert await decode_dictionary(3.14) == 3.14
    assert await decode_dictionary(None) is None
