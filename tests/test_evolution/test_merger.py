"""Tests for KnowledgeMerger."""
from __future__ import annotations


BASE = {
    "concepts": [
        {"id": "gravity", "attrs": {"strength": "strong"}},
        {"id": "mass", "attrs": {}},
    ],
    "relations": [
        {"src": "gravity", "dst": "mass", "kind": "depends_on"}
    ],
}

INCOMING = {
    "concepts": [
        {"id": "gravity", "attrs": {"strength": "weak", "new_key": "new_val"}},
        {"id": "energy", "attrs": {"unit": "joule"}},
    ],
    "relations": [
        {"src": "gravity", "dst": "mass", "kind": "depends_on"},  # duplicate
        {"src": "energy", "dst": "mass", "kind": "related"},
    ],
}


def test_merge_union_of_concepts(merger):
    result = merger.merge(BASE, INCOMING)
    ids = [c["id"] for c in result["concepts"]]
    assert "gravity" in ids
    assert "mass" in ids
    assert "energy" in ids


def test_merge_prefer_incoming_updates_attrs(merger):
    result = merger.merge(BASE, INCOMING, conflict_strategy="prefer_incoming")
    g = next(c for c in result["concepts"] if c["id"] == "gravity")
    assert g["attrs"].get("new_key") == "new_val"


def test_merge_prefer_base_keeps_original(merger):
    result = merger.merge(BASE, INCOMING, conflict_strategy="prefer_base")
    g = next(c for c in result["concepts"] if c["id"] == "gravity")
    assert g["attrs"]["strength"] == "strong"


def test_merge_deduplicates_relations(merger):
    result = merger.merge(BASE, INCOMING)
    # gravity→mass appears in both but should appear once
    gravity_mass = [
        r for r in result["relations"]
        if r["src"] == "gravity" and r["dst"] == "mass"
    ]
    assert len(gravity_mass) == 1


def test_merge_adds_new_relations(merger):
    result = merger.merge(BASE, INCOMING)
    energy_mass = [
        r for r in result["relations"]
        if r["src"] == "energy" and r["dst"] == "mass"
    ]
    assert len(energy_mass) == 1


def test_merge_empty_base(merger):
    result = merger.merge({"concepts": [], "relations": []}, INCOMING)
    ids = [c["id"] for c in result["concepts"]]
    assert "gravity" in ids
    assert "energy" in ids


def test_merge_empty_incoming(merger):
    result = merger.merge(BASE, {"concepts": [], "relations": []})
    assert len(result["concepts"]) == len(BASE["concepts"])


def test_can_merge_always_true(merger):
    assert merger.can_merge(BASE, INCOMING) is True


def test_merge_no_relations_lost(merger):
    result = merger.merge(BASE, INCOMING)
    assert len(result["relations"]) >= len(BASE["relations"])
