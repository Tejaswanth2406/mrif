"""Tests for WorkingMemory."""
from __future__ import annotations

from mrif.memory.working import WorkingMemory


def test_push_and_size(working_memory):
    working_memory.push({"x": 1})
    assert working_memory.size() == 1


def test_eviction_at_limit():
    wm = WorkingMemory(limit=3)
    for i in range(5):
        wm.push(i)
    assert wm.size() == 3


def test_peek_returns_last(working_memory):
    working_memory.push("first")
    working_memory.push("second")
    assert working_memory.peek() == "second"


def test_peek_empty_returns_none():
    wm = WorkingMemory(limit=10)
    assert wm.peek() is None


def test_pop_removes_last(working_memory):
    working_memory.push("a")
    working_memory.push("b")
    val = working_memory.pop()
    assert val == "b"
    assert working_memory.size() == 1


def test_pop_empty_returns_none():
    wm = WorkingMemory(limit=5)
    assert wm.pop() is None


def test_retrieve_all(working_memory):
    working_memory.push("alpha")
    working_memory.push("beta")
    items = working_memory.retrieve()
    assert len(items) == 2


def test_retrieve_newest_first(working_memory):
    working_memory.push("old")
    working_memory.push("new")
    items = working_memory.retrieve()
    assert items[0] == "new"


def test_retrieve_filter_string(working_memory):
    working_memory.push("apple")
    working_memory.push("banana")
    working_memory.push("apricot")
    results = working_memory.retrieve("ap")
    assert len(results) == 2


def test_clear(working_memory):
    working_memory.push(1)
    working_memory.push(2)
    working_memory.clear()
    assert working_memory.size() == 0


def test_is_full():
    wm = WorkingMemory(limit=2)
    wm.push(1)
    assert not wm.is_full()
    wm.push(2)
    assert wm.is_full()


def test_limit_property(working_memory):
    assert working_memory.limit == 10
