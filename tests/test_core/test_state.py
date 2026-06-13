"""Tests for CoreState."""
from __future__ import annotations

from mrif.core.state import CoreState


def test_initial_state():
    state = CoreState(core_id="CORE-TEST")
    assert state.core_id == "CORE-TEST"
    assert state.generation == 0
    assert state.knowledge_nodes == 0


def test_increment_generation():
    state = CoreState(core_id="CORE-TEST")
    prev_time = state.updated_at
    state.increment_generation()
    assert state.generation == 1
    assert state.updated_at >= prev_time


def test_increment_multiple():
    state = CoreState(core_id="CORE-TEST")
    for i in range(5):
        state.increment_generation()
    assert state.generation == 5


def test_to_dict():
    state = CoreState(core_id="CORE-TEST")
    d = state.to_dict()
    assert d["core_id"] == "CORE-TEST"
    assert d["generation"] == 0
    assert "created_at" in d
    assert "updated_at" in d


def test_metadata_defaults_empty():
    state = CoreState(core_id="X")
    assert state.metadata == {}


def test_metadata_custom():
    state = CoreState(core_id="X", metadata={"env": "test"})
    assert state.metadata["env"] == "test"
