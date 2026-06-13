"""Tests for EpisodicMemory."""
from __future__ import annotations


def test_record_returns_id(episodic_memory):
    eid = episodic_memory.record(event_type="discovery", data={"obj": "quasar"})
    assert eid.startswith("ep-")


def test_size_grows(episodic_memory):
    episodic_memory.record("observation", {"val": 1})
    episodic_memory.record("action", {"val": 2})
    assert episodic_memory.size() == 2


def test_get_recent(episodic_memory):
    for i in range(15):
        episodic_memory.record("event", {"i": i})
    recent = episodic_memory.get_recent(5)
    assert len(recent) == 5
    assert recent[-1].data["i"] == 14


def test_retrieve_all(episodic_memory):
    episodic_memory.record("t1", {"x": 1})
    episodic_memory.record("t2", {"x": 2})
    items = episodic_memory.retrieve()
    assert len(items) == 2


def test_retrieve_filter_by_type(episodic_memory):
    episodic_memory.record("collision", {"energy": 100})
    episodic_memory.record("observation", {"energy": 50})
    episodic_memory.record("collision", {"energy": 200})
    results = episodic_memory.retrieve("collision")
    assert len(results) == 2


def test_push_stores_item(episodic_memory):
    episodic_memory.push("raw string item")
    assert episodic_memory.size() == 1


def test_clear(episodic_memory):
    episodic_memory.record("e", {})
    episodic_memory.clear()
    assert episodic_memory.size() == 0


def test_episode_ids_sequential(episodic_memory):
    id1 = episodic_memory.record("a", {})
    id2 = episodic_memory.record("b", {})
    assert id1 < id2


def test_retrieve_returns_dicts(episodic_memory):
    episodic_memory.record("test", {"key": "val"})
    items = episodic_memory.retrieve()
    assert isinstance(items[0], dict)
    assert "episode_id" in items[0]
    assert "timestamp" in items[0]
