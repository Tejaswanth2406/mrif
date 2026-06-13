"""Tests for KnowledgeGraph (Dimension K)."""
from __future__ import annotations

import pytest

from mrif.dimensions.knowledge import KnowledgeGraph
from mrif.exceptions import ConceptNotFoundError


def test_add_and_get_concept(knowledge_graph):
    knowledge_graph.add_concept("gravity", {"type": "force"})
    attrs = knowledge_graph.get_concept("gravity")
    assert attrs["type"] == "force"


def test_concept_not_found_raises(knowledge_graph):
    with pytest.raises(ConceptNotFoundError):
        knowledge_graph.get_concept("nonexistent")


def test_add_relation(knowledge_graph):
    knowledge_graph.add_concept("A")
    knowledge_graph.add_concept("B")
    knowledge_graph.add_relation("A", "B", kind="causes")
    relations = knowledge_graph.get_relations("A")
    assert len(relations) == 1
    assert relations[0]["dst"] == "B"
    assert relations[0]["kind"] == "causes"


def test_add_relation_auto_creates_nodes(knowledge_graph):
    knowledge_graph.add_relation("X", "Y", kind="linked")
    assert knowledge_graph.size() == 2


def test_remove_concept(knowledge_graph):
    knowledge_graph.add_concept("temp")
    knowledge_graph.remove_concept("temp")
    with pytest.raises(ConceptNotFoundError):
        knowledge_graph.get_concept("temp")


def test_remove_nonexistent_raises(knowledge_graph):
    with pytest.raises(ConceptNotFoundError):
        knowledge_graph.remove_concept("ghost")


def test_find_path(knowledge_graph):
    knowledge_graph.add_relation("A", "B")
    knowledge_graph.add_relation("B", "C")
    path = knowledge_graph.find_path("A", "C")
    assert path == ["A", "B", "C"]


def test_find_path_no_route(knowledge_graph):
    knowledge_graph.add_concept("island")
    path = knowledge_graph.find_path("A", "island")
    assert path == []


def test_search(knowledge_graph):
    knowledge_graph.add_concept("neural_network")
    knowledge_graph.add_concept("neural_pathway")
    knowledge_graph.add_concept("gravity")
    results = knowledge_graph.search("neural")
    assert len(results) == 2


def test_neighbours(knowledge_graph):
    knowledge_graph.add_relation("A", "B")
    knowledge_graph.add_relation("A", "C")
    nb = knowledge_graph.neighbours("A")
    assert set(nb) == {"B", "C"}


def test_size(knowledge_graph):
    assert knowledge_graph.size() == 0
    knowledge_graph.add_concept("x")
    knowledge_graph.add_concept("y")
    assert knowledge_graph.size() == 2


def test_export_snapshot(knowledge_graph):
    knowledge_graph.add_concept("p", {"val": 1})
    knowledge_graph.add_relation("p", "q")
    snap = knowledge_graph.export_snapshot()
    assert len(snap["concepts"]) >= 1
    assert len(snap["relations"]) >= 1


def test_import_snapshot(knowledge_graph):
    snap = {
        "concepts": [{"id": "alpha", "attrs": {}}],
        "relations": [{"src": "alpha", "dst": "beta", "kind": "linked"}],
    }
    knowledge_graph.import_snapshot(snap)
    assert knowledge_graph.size() >= 2


def test_merge(knowledge_graph):
    other = KnowledgeGraph()
    other.add_concept("unique_concept")
    knowledge_graph.merge(other)
    assert knowledge_graph.get_concept("unique_concept") is not None


def test_relation_count(knowledge_graph):
    knowledge_graph.add_relation("a", "b")
    knowledge_graph.add_relation("b", "c")
    assert knowledge_graph.relation_count() == 2
