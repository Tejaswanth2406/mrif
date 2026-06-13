"""Tests for LongTermMemory (SQLite-backed)."""
from __future__ import annotations

import pytest
from mrif.exceptions import MemoryKeyError


def test_set_and_get(long_term_memory):
    long_term_memory.set("key1", {"value": 42})
    result = long_term_memory.get("key1")
    assert result["value"] == 42


def test_get_missing_raises(long_term_memory):
    with pytest.raises(MemoryKeyError):
        long_term_memory.get("nonexistent")


def test_overwrite_key(long_term_memory):
    long_term_memory.set("k", "original")
    long_term_memory.set("k", "updated")
    assert long_term_memory.get("k") == "updated"


def test_push_increments_size(long_term_memory):
    long_term_memory.push({"data": "item"})
    assert long_term_memory.size() == 1


def test_size_grows(long_term_memory):
    long_term_memory.set("a", 1)
    long_term_memory.set("b", 2)
    assert long_term_memory.size() == 2


def test_delete_key(long_term_memory):
    long_term_memory.set("to_delete", "bye")
    long_term_memory.delete_key("to_delete")
    with pytest.raises(MemoryKeyError):
        long_term_memory.get("to_delete")


def test_keys_list(long_term_memory):
    long_term_memory.set("x", 1)
    long_term_memory.set("y", 2)
    keys = long_term_memory.keys()
    assert "x" in keys
    assert "y" in keys


def test_retrieve_all(long_term_memory):
    long_term_memory.set("p", {"n": 1})
    long_term_memory.set("q", {"n": 2})
    items = long_term_memory.retrieve()
    assert len(items) == 2


def test_retrieve_filter(long_term_memory):
    long_term_memory.set("fruit_apple", "sweet")
    long_term_memory.set("fruit_lemon", "sour")
    long_term_memory.set("veggie_carrot", "crunchy")
    results = long_term_memory.retrieve("fruit")
    assert len(results) == 2


def test_clear(long_term_memory):
    long_term_memory.set("a", 1)
    long_term_memory.set("b", 2)
    long_term_memory.clear()
    assert long_term_memory.size() == 0


def test_set_with_tags(long_term_memory):
    long_term_memory.set("tagged", "data", tags=["science", "physics"])
    result = long_term_memory.get("tagged")
    assert result == "data"


def test_store_complex_object(long_term_memory):
    obj = {"nested": {"list": [1, 2, 3], "flag": True}}
    long_term_memory.set("complex", obj)
    result = long_term_memory.get("complex")
    assert result["nested"]["list"] == [1, 2, 3]
