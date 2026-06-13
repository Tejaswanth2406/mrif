"""
Dimension T — Timeline Engine.

Models time as a branching tree of events rather than a linear sequence.
The MetaCore can instantiate multiple future branches and evaluate them.

        Future-A
       /
Root──Present──Future-B
       \\
        Future-C
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from mrif.exceptions import TimelineNodeNotFoundError


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class TimelineNode:
    """A single event node in the timeline tree."""

    node_id: str
    label: str
    parent_id: str | None
    timestamp: datetime = field(default_factory=_utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)
    children: list[str] = field(default_factory=list)  # child node_ids


class TimelineEngine:
    """
    Branching timeline backed by an in-memory dict of TimelineNodes.

    The root node is created automatically at construction.
    """

    def __init__(self) -> None:
        self._nodes: dict[str, TimelineNode] = {}
        self._root_id: str = self._create_root()

    # ── Internal ────────────────────────────────────────────────────────────

    def _create_root(self) -> str:
        root = TimelineNode(
            node_id="root",
            label="Genesis",
            parent_id=None,
        )
        self._nodes["root"] = root
        return "root"

    def _get(self, node_id: str) -> TimelineNode:
        try:
            return self._nodes[node_id]
        except KeyError:
            raise TimelineNodeNotFoundError(node_id)

    # ── Mutation ────────────────────────────────────────────────────────────

    def record_event(
        self,
        event_id: str | None = None,
        label: str = "",
        parent_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """
        Append an event to the timeline.

        If *parent_id* is None the event is attached to the current tip
        of the main branch (root if empty).
        """
        nid = event_id or str(uuid.uuid4())
        pid = parent_id or self._current_tip()

        if pid not in self._nodes:
            raise TimelineNodeNotFoundError(pid)

        node = TimelineNode(
            node_id=nid,
            label=label,
            parent_id=pid,
            metadata=metadata or {},
        )
        self._nodes[nid] = node
        self._nodes[pid].children.append(nid)
        return nid

    def branch(self, from_node_id: str, branch_label: str) -> str:
        """Create a new branch diverging from *from_node_id*."""
        return self.record_event(
            label=branch_label,
            parent_id=from_node_id,
        )

    # ── Query ───────────────────────────────────────────────────────────────

    def _current_tip(self) -> str:
        """Walk the main (first-child) branch to find the latest node."""
        current = self._root_id
        while self._nodes[current].children:
            current = self._nodes[current].children[0]
        return current

    def get_path(self, node_id: str) -> list[str]:
        """Return the ancestor chain from root → node_id."""
        path: list[str] = []
        node = self._get(node_id)
        while node is not None:
            path.append(node.node_id)
            node = self._nodes.get(node.parent_id) if node.parent_id else None  # type: ignore[assignment]
        return list(reversed(path))

    def get_branches(self, from_node_id: str) -> list[str]:
        """Return all direct children (branch points) of a node."""
        return list(self._get(from_node_id).children)

    def get_all_futures(self, from_node_id: str) -> list[list[str]]:
        """DFS all leaf paths reachable from *from_node_id*."""
        futures: list[list[str]] = []

        def dfs(nid: str, path: list[str]) -> None:
            node = self._nodes[nid]
            path = path + [nid]
            if not node.children:
                futures.append(path)
            else:
                for child in node.children:
                    dfs(child, path)

        dfs(from_node_id, [])
        return futures

    def node_count(self) -> int:
        return len(self._nodes)

    def export(self) -> dict[str, Any]:
        return {
            nid: {
                "label": n.label,
                "parent_id": n.parent_id,
                "children": n.children,
                "timestamp": n.timestamp.isoformat(),
                "metadata": n.metadata,
            }
            for nid, n in self._nodes.items()
        }
