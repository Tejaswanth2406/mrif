"""
Lineage — helper utilities for reasoning about agent ancestry.
"""
from __future__ import annotations

from typing import Any


def build_lineage_tree(agents: list[dict[str, Any]]) -> dict[str, list[str]]:
    """
    Build a parent → [children] adjacency map from a flat agent list.

    Parameters
    ----------
    agents : list of dicts with keys 'agent_id' and 'parent_id'
    """
    tree: dict[str, list[str]] = {}
    for agent in agents:
        pid = agent.get("parent_id")
        aid = agent["agent_id"]
        if pid:
            tree.setdefault(pid, []).append(aid)
        else:
            tree.setdefault(aid, [])
    return tree


def depth(agent_id: str, agents_by_id: dict[str, dict[str, Any]]) -> int:
    """Return the depth of *agent_id* from the root (root = 0)."""
    d = 0
    current = agents_by_id.get(agent_id)
    while current and current.get("parent_id"):
        d += 1
        current = agents_by_id.get(current["parent_id"])
    return d


def common_ancestor(
    a: str,
    b: str,
    agents_by_id: dict[str, dict[str, Any]],
) -> str | None:
    """Find the nearest common ancestor of agents *a* and *b*."""

    def ancestors(agent_id: str) -> list[str]:
        chain: list[str] = []
        current = agents_by_id.get(agent_id)
        while current:
            chain.append(current["agent_id"])
            pid = current.get("parent_id")
            current = agents_by_id.get(pid) if pid else None
        return chain

    chain_a = ancestors(a)
    set_a = set(chain_a)

    for node in ancestors(b):
        if node in set_a:
            return node
    return None
