"""
Dimension C — Causal Graph.

Records action → consequence chains as a directed acyclic graph.
Enables tracing why any event occurred and predicting downstream effects.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import networkx as nx


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class CausalNode:
    """One node in the causal graph."""

    node_id: str
    action_type: str
    context: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=_utcnow)


class CausalGraph:
    """
    DAG of causal actions and their consequences.

    Nodes = actions / events
    Edges = "caused" relationships (A → B means A caused B)
    """

    def __init__(self) -> None:
        self._graph: nx.DiGraph = nx.DiGraph()
        self._nodes: dict[str, CausalNode] = {}

    # ── Mutation ────────────────────────────────────────────────────────────

    def record_action(
        self,
        action_id: str | None = None,
        action_type: str = "unknown",
        context: dict[str, Any] | None = None,
        caused_by: str | None = None,
    ) -> str:
        """
        Record an action node.

        Parameters
        ----------
        action_id  : Optional explicit ID (generated if omitted).
        action_type: Category label for the action.
        context    : Arbitrary metadata dict.
        caused_by  : ID of the action that triggered this one (adds an edge).
        """
        aid = action_id or str(uuid.uuid4())
        node = CausalNode(
            node_id=aid,
            action_type=action_type,
            context=context or {},
        )
        self._nodes[aid] = node
        self._graph.add_node(aid, action_type=action_type)

        if caused_by and caused_by in self._nodes:
            self._graph.add_edge(caused_by, aid, label="caused")

        return aid

    def add_consequence(self, cause_id: str, effect_id: str) -> None:
        """Explicitly link two existing nodes with a causal edge."""
        self._graph.add_edge(cause_id, effect_id, label="caused")

    # ── Query ────────────────────────────────────────────────────────────────

    def trace_causes(self, action_id: str) -> list[str]:
        """Return the causal chain leading up to *action_id* (oldest first)."""
        try:
            ancestors = nx.ancestors(self._graph, action_id)
        except nx.NodeNotFound:
            return []
        # Topological sort restricted to ancestors + target
        subgraph = self._graph.subgraph(ancestors | {action_id})
        return list(nx.topological_sort(subgraph))

    def trace_consequences(self, action_id: str) -> list[str]:
        """Return all downstream effects of *action_id*."""
        try:
            return list(nx.descendants(self._graph, action_id))
        except nx.NodeNotFound:
            return []

    def find_root_causes(self) -> list[str]:
        """Nodes with no incoming edges — the ultimate causes."""
        return [n for n in self._graph.nodes if self._graph.in_degree(n) == 0]

    def get_action(self, action_id: str) -> CausalNode | None:
        return self._nodes.get(action_id)

    # ── Metrics ─────────────────────────────────────────────────────────────

    def edge_count(self) -> int:
        return self._graph.number_of_edges()

    def node_count(self) -> int:
        return self._graph.number_of_nodes()

    def is_dag(self) -> bool:
        return nx.is_directed_acyclic_graph(self._graph)

    def export(self) -> dict[str, Any]:
        return {
            "nodes": [
                {
                    "id": n.node_id,
                    "type": n.action_type,
                    "context": n.context,
                    "timestamp": n.timestamp.isoformat(),
                }
                for n in self._nodes.values()
            ],
            "edges": [
                {"cause": u, "effect": v}
                for u, v in self._graph.edges()
            ],
        }
