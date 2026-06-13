"""Tests for lineage helper utilities."""
from __future__ import annotations

from mrif.governance.lineage import build_lineage_tree, common_ancestor, depth


AGENTS = [
    {"agent_id": "root", "parent_id": None},
    {"agent_id": "child-a", "parent_id": "root"},
    {"agent_id": "child-b", "parent_id": "root"},
    {"agent_id": "grandchild-a1", "parent_id": "child-a"},
    {"agent_id": "grandchild-a2", "parent_id": "child-a"},
]
BY_ID = {a["agent_id"]: a for a in AGENTS}


def test_build_lineage_tree():
    tree = build_lineage_tree(AGENTS)
    assert set(tree["root"]) == {"child-a", "child-b"}
    assert set(tree["child-a"]) == {"grandchild-a1", "grandchild-a2"}


def test_build_lineage_tree_leaf_has_empty_list():
    tree = build_lineage_tree(AGENTS)
    assert tree.get("grandchild-a1") is None or tree["grandchild-a1"] == []


def test_depth_root():
    assert depth("root", BY_ID) == 0


def test_depth_child():
    assert depth("child-a", BY_ID) == 1


def test_depth_grandchild():
    assert depth("grandchild-a1", BY_ID) == 2


def test_common_ancestor_direct_siblings():
    anc = common_ancestor("child-a", "child-b", BY_ID)
    assert anc == "root"


def test_common_ancestor_different_depths():
    anc = common_ancestor("grandchild-a1", "child-b", BY_ID)
    assert anc == "root"


def test_common_ancestor_same_node():
    anc = common_ancestor("child-a", "child-a", BY_ID)
    assert anc == "child-a"


def test_common_ancestor_no_relation():
    agents = [
        {"agent_id": "x", "parent_id": None},
        {"agent_id": "y", "parent_id": None},
    ]
    by_id = {a["agent_id"]: a for a in agents}
    anc = common_ancestor("x", "y", by_id)
    assert anc is None


def test_lineage_tree_no_parents():
    agents = [{"agent_id": "solo", "parent_id": None}]
    tree = build_lineage_tree(agents)
    assert "solo" in tree
    assert tree["solo"] == []
