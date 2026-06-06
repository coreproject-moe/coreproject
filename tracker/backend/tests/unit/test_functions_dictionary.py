"""Tests for coreproject_tracker.functions.dictionary - decode_dictionary."""
import pytest
from coreproject_tracker.functions import decode_dictionary


class TestDecodeDictionary:
    @pytest.mark.asyncio
    async def test_simple_dict(self):
        data = {b"key": b"value"}
        result = await decode_dictionary(data)
        assert result == {"key": "value"}

    @pytest.mark.asyncio
    async def test_nested_dict(self):
        data = {b"outer": {b"inner": b"value"}}
        result = await decode_dictionary(data)
        assert result == {"outer": {"inner": "value"}}

    @pytest.mark.asyncio
    async def test_list_of_bytes(self):
        data = [b"a", b"b", b"c"]
        result = await decode_dictionary(data)
        assert result == ["a", "b", "c"]

    @pytest.mark.asyncio
    async def test_bytes(self):
        result = await decode_dictionary(b"hello")
        assert result == "hello"

    @pytest.mark.asyncio
    async def test_string_passthrough(self):
        result = await decode_dictionary("already-string")
        assert result == "already-string"

    @pytest.mark.asyncio
    async def test_int_passthrough(self):
        result = await decode_dictionary(42)
        assert result == 42

    @pytest.mark.asyncio
    async def test_float_passthrough(self):
        result = await decode_dictionary(3.14)
        assert result == 3.14

    @pytest.mark.asyncio
    async def test_none_in_dict_value(self):
        data = {b"key": None}
        result = await decode_dictionary(data)
        assert result == {"key": None}

    @pytest.mark.asyncio
    async def test_mixed_nested(self):
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
