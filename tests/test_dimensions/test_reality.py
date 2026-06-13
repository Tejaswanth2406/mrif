"""Tests for RealityEngine (Dimension R)."""
from __future__ import annotations

import pytest

from mrif.exceptions import RealityNotFoundError


def test_default_reality_exists(reality_engine):
    assert reality_engine.count() == 1


def test_create_reality(reality_engine):
    rid = reality_engine.create("Custom", {"space_dimensions": 4})
    r = reality_engine.get(rid)
    assert r.assumptions["space_dimensions"] == 4


def test_get_nonexistent_raises(reality_engine):
    with pytest.raises(RealityNotFoundError):
        reality_engine.get("does-not-exist")


def test_delete_reality(reality_engine):
    rid = reality_engine.create("Temp", {})
    reality_engine.delete(rid)
    with pytest.raises(RealityNotFoundError):
        reality_engine.get(rid)


def test_delete_nonexistent_raises(reality_engine):
    with pytest.raises(RealityNotFoundError):
        reality_engine.delete("ghost")


def test_fork_creates_copy(reality_engine):
    rid = reality_engine.create("Original", {"x": 1})
    fork_id = reality_engine.fork(rid)
    forked = reality_engine.get(fork_id)
    assert forked.assumptions["x"] == 1
    assert fork_id != rid


def test_fork_has_parent(reality_engine):
    rid = reality_engine.create("Base", {})
    fork_id = reality_engine.fork(rid)
    forked = reality_engine.get(fork_id)
    assert rid in forked.parent_ids


def test_mutate_creates_child(reality_engine):
    a = reality_engine.create("A", {"x": 10, "y": True})
    b = reality_engine.create("B", {"x": 20, "y": False})
    child_id = reality_engine.mutate(a, b)
    child = reality_engine.get(child_id)
    assert "x" in child.assumptions
    assert child_id not in (a, b)


def test_mutate_has_both_parents(reality_engine):
    a = reality_engine.create("A", {"x": 1})
    b = reality_engine.create("B", {"x": 2})
    child_id = reality_engine.mutate(a, b)
    child = reality_engine.get(child_id)
    assert a in child.parent_ids
    assert b in child.parent_ids


def test_compare_realities(reality_engine):
    a = reality_engine.create("A", {"x": 1, "y": 2})
    b = reality_engine.create("B", {"x": 9, "y": 2})
    diff = reality_engine.compare(a, b)
    assert "x" in diff
    assert "y" not in diff


def test_update_fitness(reality_engine):
    rid = list(reality_engine.list_ids())[0]
    reality_engine.update_fitness(rid, 0.95)
    r = reality_engine.get(rid)
    assert r.fitness == 0.95


def test_rank_by_fitness(reality_engine):
    a = reality_engine.create("A", {})
    b = reality_engine.create("B", {})
    reality_engine.update_fitness(a, 0.9)
    reality_engine.update_fitness(b, 0.1)
    ranked = reality_engine.rank_by_fitness()
    assert ranked[0].reality_id == a


def test_count(reality_engine):
    start = reality_engine.count()
    reality_engine.create("extra", {})
    assert reality_engine.count() == start + 1


def test_list_ids(reality_engine):
    ids = reality_engine.list_ids()
    assert len(ids) == reality_engine.count()
