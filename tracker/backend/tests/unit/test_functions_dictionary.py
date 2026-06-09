"""Tests for coreproject_tracker.functions.dictionary - decode_dictionary."""
import pytest
from coreproject_tracker.functions import decode_dictionary


@pytest.mark.asyncio
async def test_decode_dict_simple():
    data = {b"key": b"value"}
    result = await decode_dictionary(data)
    assert result == {"key": "value"}


@pytest.mark.asyncio
async def test_decode_dict_nested():
    data = {b"outer": {b"inner": b"value"}}
    result = await decode_dictionary(data)
    assert result == {"outer": {"inner": "value"}}


@pytest.mark.asyncio
async def test_decode_dict_list_bytes():
    data = [b"a", b"b", b"c"]
    result = await decode_dictionary(data)
    assert result == ["a", "b", "c"]


@pytest.mark.asyncio
async def test_decode_dict_bytes():
    result = await decode_dictionary(b"hello")
    assert result == "hello"


@pytest.mark.asyncio
async def test_decode_dict_string_passthrough():
    result = await decode_dictionary("already-string")
    assert result == "already-string"


@pytest.mark.asyncio
async def test_decode_dict_int_passthrough():
    result = await decode_dictionary(42)
    assert result == 42


@pytest.mark.asyncio
async def test_decode_dict_float_passthrough():
    result = await decode_dictionary(3.14)
    assert result == 3.14


@pytest.mark.asyncio
async def test_decode_dict_none_value():
    data = {b"key": None}
    result = await decode_dictionary(data)
    assert result == {"key": None}


@pytest.mark.asyncio
async def test_decode_dict_mixed_nested():
    data = {
        b"list": [b"item1", {b"nested": b"value"}],
        b"string": b"hello",
        b"number": 42,
    }
    result = await decode_dictionary(data)
    assert result["list"][0] == "item1"
    assert result["list"][1] == {"nested": "value"}
    assert result["string"] == "hello"
    assert result["number"] == 42
