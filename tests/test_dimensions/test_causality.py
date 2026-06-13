"""Tests for CausalGraph (Dimension C)."""
from __future__ import annotations

import pytest
from mrif.dimensions.causality import CausalGraph


def test_record_action_returns_id(causal_graph):
    aid = causal_graph.record_action(action_type="experiment")
    assert aid is not None


def test_record_action_explicit_id(causal_graph):
    aid = causal_graph.record_action(action_id="act-001", action_type="observe")
    assert aid == "act-001"


def test_node_count_grows(causal_graph):
    causal_graph.record_action(action_type="a")
    causal_graph.record_action(action_type="b")
    assert causal_graph.node_count() == 2


def test_causal_chain(causal_graph):
    a = causal_graph.record_action(action_type="cause")
    b = causal_graph.record_action(action_type="effect", caused_by=a)
    causes = causal_graph.trace_causes(b)
    assert a in causes


def test_trace_consequences(causal_graph):
    a = causal_graph.record_action(action_type="root")
    b = causal_graph.record_action(action_type="child", caused_by=a)
    c = causal_graph.record_action(action_type="grandchild", caused_by=b)
    consequences = causal_graph.trace_consequences(a)
    assert b in consequences
    assert c in consequences


def test_find_root_causes(causal_graph):
    a = causal_graph.record_action(action_type="root")
    causal_graph.record_action(action_type="derived", caused_by=a)
    roots = causal_graph.find_root_causes()
    assert a in roots


def test_add_consequence(causal_graph):
    a = causal_graph.record_action(action_type="A")
    b = causal_graph.record_action(action_type="B")
    causal_graph.add_consequence(a, b)
    assert causal_graph.edge_count() == 1


def test_edge_count(causal_graph):
    a = causal_graph.record_action(action_type="A")
    b = causal_graph.record_action(action_type="B", caused_by=a)
    c = causal_graph.record_action(action_type="C", caused_by=b)
    assert causal_graph.edge_count() == 2


def test_is_dag(causal_graph):
    a = causal_graph.record_action(action_type="A")
    causal_graph.record_action(action_type="B", caused_by=a)
    assert causal_graph.is_dag() is True


def test_get_action(causal_graph):
    aid = causal_graph.record_action(action_id="x1", action_type="test",
                                     context={"key": "val"})
    node = causal_graph.get_action(aid)
    assert node is not None
    assert node.action_type == "test"
    assert node.context["key"] == "val"


def test_get_action_missing(causal_graph):
    assert causal_graph.get_action("ghost") is None


def test_export_structure(causal_graph):
    a = causal_graph.record_action(action_type="A")
    b = causal_graph.record_action(action_type="B", caused_by=a)
    export = causal_graph.export()
    assert "nodes" in export
    assert "edges" in export
    assert len(export["nodes"]) == 2
    assert len(export["edges"]) == 1


def test_trace_causes_no_parent(causal_graph):
    a = causal_graph.record_action(action_type="lone")
    causes = causal_graph.trace_causes(a)
    assert a in causes


def test_trace_consequences_leaf(causal_graph):
    a = causal_graph.record_action(action_type="leaf")
    assert causal_graph.trace_consequences(a) == []
