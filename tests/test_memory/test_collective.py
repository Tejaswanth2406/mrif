"""Tests for CollectiveMemory."""
from __future__ import annotations


def test_store_and_fetch(collective_memory):
    collective_memory.store("agent-1", "discovery", {"planet": "Kepler-442b"})
    val = collective_memory.fetch("agent-1", "discovery")
    assert val["planet"] == "Kepler-442b"


def test_fetch_missing_returns_none(collective_memory):
    assert collective_memory.fetch("agent-x", "missing") is None


def test_agents_isolated(collective_memory):
    collective_memory.store("a1", "k", "value_a1")
    collective_memory.store("a2", "k", "value_a2")
    assert collective_memory.fetch("a1", "k") == "value_a1"
    assert collective_memory.fetch("a2", "k") == "value_a2"


def test_delete(collective_memory):
    collective_memory.store("agent", "key", "data")
    collective_memory.delete("agent", "key")
    assert collective_memory.fetch("agent", "key") is None


def test_list_keys(collective_memory):
    collective_memory.store("agt", "key1", 1)
    collective_memory.store("agt", "key2", 2)
    keys = collective_memory.list_keys("agt")
    assert set(keys) == {"key1", "key2"}


def test_fetch_all(collective_memory):
    collective_memory.store("agt", "a", 1)
    collective_memory.store("agt", "b", 2)
    all_data = collective_memory.fetch_all("agt")
    assert all_data == {"a": 1, "b": 2}


def test_size(collective_memory):
    assert collective_memory.size() == 0
    collective_memory.store("a", "k1", "v")
    collective_memory.store("b", "k2", "v")
    assert collective_memory.size() == 2


def test_retrieve_all(collective_memory):
    collective_memory.store("x", "k", {"val": 99})
    items = collective_memory.retrieve()
    assert len(items) == 1


def test_retrieve_filter(collective_memory):
    collective_memory.store("a", "science", {"domain": "physics"})
    collective_memory.store("b", "art", {"domain": "drawing"})
    results = collective_memory.retrieve("physics")
    assert len(results) == 1


def test_push_dict(collective_memory):
    collective_memory.push({"agent_id": "agt", "key": "pushed", "value": 42})
    assert collective_memory.fetch("agt", "pushed") == 42


def test_clear(collective_memory):
    collective_memory.store("a", "k", "v")
    collective_memory.clear()
    assert collective_memory.size() == 0
