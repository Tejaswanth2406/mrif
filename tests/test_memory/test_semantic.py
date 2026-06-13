"""Tests for SemanticMemory."""
from __future__ import annotations


def test_learn_and_recall(semantic_memory):
    semantic_memory.learn("photon", {"mass": 0, "speed": "c"})
    attrs = semantic_memory.recall("photon")
    assert attrs["mass"] == 0


def test_recall_unknown_returns_empty(semantic_memory):
    assert semantic_memory.recall("unknown") == {}


def test_learn_merges_attrs(semantic_memory):
    semantic_memory.learn("electron", {"charge": -1})
    semantic_memory.learn("electron", {"spin": 0.5})
    attrs = semantic_memory.recall("electron")
    assert attrs["charge"] == -1
    assert attrs["spin"] == 0.5


def test_learn_overwrites_existing_key(semantic_memory):
    semantic_memory.learn("quark", {"color": "red"})
    semantic_memory.learn("quark", {"color": "blue"})
    assert semantic_memory.recall("quark")["color"] == "blue"


def test_forget(semantic_memory):
    semantic_memory.learn("temporary", {"x": 1})
    semantic_memory.forget("temporary")
    assert semantic_memory.recall("temporary") == {}


def test_forget_nonexistent_no_error(semantic_memory):
    semantic_memory.forget("ghost")  # should not raise


def test_size(semantic_memory):
    assert semantic_memory.size() == 0
    semantic_memory.learn("a", {})
    semantic_memory.learn("b", {})
    assert semantic_memory.size() == 2


def test_retrieve_all(semantic_memory):
    semantic_memory.learn("x", {"v": 1})
    semantic_memory.learn("y", {"v": 2})
    items = semantic_memory.retrieve()
    assert len(items) == 2


def test_retrieve_filter(semantic_memory):
    semantic_memory.learn("neural_net", {"type": "ml"})
    semantic_memory.learn("neural_pathway", {"type": "bio"})
    semantic_memory.learn("gravity", {"type": "physics"})
    results = semantic_memory.retrieve("neural")
    assert len(results) == 2


def test_push_dict(semantic_memory):
    semantic_memory.push({"concept_id": "boson", "attrs": {"spin": 1}})
    assert semantic_memory.recall("boson")["spin"] == 1


def test_clear(semantic_memory):
    semantic_memory.learn("a", {})
    semantic_memory.clear()
    assert semantic_memory.size() == 0
