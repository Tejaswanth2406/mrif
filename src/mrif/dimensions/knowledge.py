"""
Dimension K — Knowledge Graph.

Backed by a directed NetworkX graph where:
  nodes  = concepts  (id + attribute dict)
  edges  = relations (src → dst + kind label)
"""
from __future__ import annotations

from typing import Any

import networkx as nx

from mrif.exceptions import ConceptNotFoundError


class KnowledgeGraph:
    """
    Directed knowledge graph with typed relations.

    Concepts are nodes; relations are labelled directed edges.
    """

    def __init__(self) -> None:
        self._graph: nx.DiGraph = nx.DiGraph()

    # ── Mutation ────────────────────────────────────────────────────────────

    def add_concept(self, concept_id: str, attrs: dict[str, Any] | None = None) -> None:
        """Insert or update a concept node."""
        self._graph.add_node(concept_id, **(attrs or {}))

    def add_relation(self, src: str, dst: str, kind: str = "related") -> None:
        """Add a directed relation between two concepts."""
        for cid in (src, dst):
            if not self._graph.has_node(cid):
                self._graph.add_node(cid)
        self._graph.add_edge(src, dst, kind=kind)

    def remove_concept(self, concept_id: str) -> None:
        """Remove a concept and all its relations."""
        if not self._graph.has_node(concept_id):
            raise ConceptNotFoundError(concept_id)
        self._graph.remove_node(concept_id)

    # ── Query ───────────────────────────────────────────────────────────────

    def get_concept(self, concept_id: str) -> dict[str, Any]:
        if not self._graph.has_node(concept_id):
            raise ConceptNotFoundError(concept_id)
        return dict(self._graph.nodes[concept_id])

    def get_relations(self, concept_id: str) -> list[dict[str, Any]]:
        """Return all outgoing relations from a concept."""
        if not self._graph.has_node(concept_id):
            raise ConceptNotFoundError(concept_id)
        return [
            {"src": concept_id, "dst": dst, "kind": data.get("kind", "related")}
            for dst, data in self._graph[concept_id].items()
        ]

    def find_path(self, src: str, dst: str) -> list[str]:
        """Shortest concept path between two nodes."""
        try:
            return nx.shortest_path(self._graph, src, dst)
        except (nx.NodeNotFound, nx.NetworkXNoPath):
            return []

    def search(self, query: str) -> list[str]:
        """Return concept IDs containing *query* as a substring."""
        q = query.lower()
        return [n for n in self._graph.nodes if q in n.lower()]

    def neighbours(self, concept_id: str) -> list[str]:
        if not self._graph.has_node(concept_id):
            raise ConceptNotFoundError(concept_id)
        return list(self._graph.successors(concept_id))

    # ── Metrics ─────────────────────────────────────────────────────────────

    def size(self) -> int:
        """Number of concepts."""
        return self._graph.number_of_nodes()

    def relation_count(self) -> int:
        return self._graph.number_of_edges()

    # ── Serialisation ───────────────────────────────────────────────────────

    def export_snapshot(self) -> dict[str, Any]:
        """Export the full graph as a serialisable dict."""
        return {
            "concepts": [
                {"id": n, "attrs": dict(d)}
                for n, d in self._graph.nodes(data=True)
            ],
            "relations": [
                {"src": u, "dst": v, "kind": d.get("kind", "related")}
                for u, v, d in self._graph.edges(data=True)
            ],
        }

    def import_snapshot(self, snapshot: dict[str, Any]) -> None:
        """Merge a snapshot into this graph."""
        for c in snapshot.get("concepts", []):
            self.add_concept(c["id"], c.get("attrs", {}))
        for r in snapshot.get("relations", []):
            self.add_relation(r["src"], r["dst"], r.get("kind", "related"))

    def merge(self, other: "KnowledgeGraph") -> None:
        """Non-destructively merge another graph into this one."""
        self.import_snapshot(other.export_snapshot())
