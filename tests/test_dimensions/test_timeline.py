"""Tests for TimelineEngine (Dimension T)."""
from __future__ import annotations

import pytest

from mrif.exceptions import TimelineNodeNotFoundError


def test_initial_root_node(timeline_engine):
    assert timeline_engine.node_count() == 1


def test_record_event(timeline_engine):
    nid = timeline_engine.record_event(event_id="e1", label="First event")
    assert nid == "e1"
    assert timeline_engine.node_count() == 2


def test_record_event_auto_id(timeline_engine):
    nid = timeline_engine.record_event(label="Auto")
    assert nid is not None
    assert len(nid) > 0


def test_record_event_with_parent(timeline_engine):
    n1 = timeline_engine.record_event(event_id="n1", label="A")
    n2 = timeline_engine.record_event(event_id="n2", label="B", parent_id="n1")
    path = timeline_engine.get_path("n2")
    assert "n1" in path
    assert "n2" in path


def test_invalid_parent_raises(timeline_engine):
    with pytest.raises(TimelineNodeNotFoundError):
        timeline_engine.record_event(label="orphan", parent_id="no-such-node")


def test_branch(timeline_engine):
    branch_id = timeline_engine.branch("root", "Alternative future")
    assert branch_id is not None
    branches = timeline_engine.get_branches("root")
    assert branch_id in branches


def test_get_path_from_root(timeline_engine):
    n1 = timeline_engine.record_event(label="step1")
    n2 = timeline_engine.record_event(label="step2", parent_id=n1)
    path = timeline_engine.get_path(n2)
    assert path[0] == "root"
    assert path[-1] == n2


def test_get_all_futures(timeline_engine):
    a = timeline_engine.branch("root", "Future A")
    b = timeline_engine.branch("root", "Future B")
    futures = timeline_engine.get_all_futures("root")
    leaf_ids = [f[-1] for f in futures]
    assert a in leaf_ids
    assert b in leaf_ids


def test_node_count_grows(timeline_engine):
    for i in range(5):
        timeline_engine.record_event(label=f"event-{i}")
    assert timeline_engine.node_count() == 6  # root + 5


def test_export_contains_root(timeline_engine):
    export = timeline_engine.export()
    assert "root" in export


def test_metadata_stored(timeline_engine):
    nid = timeline_engine.record_event(
        label="rich", metadata={"author": "newton"}
    )
    export = timeline_engine.export()
    assert export[nid]["metadata"]["author"] == "newton"
