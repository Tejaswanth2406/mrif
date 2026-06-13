"""
CoreState — the persistent snapshot of a MetaCore at a given generation.

Formally:  M = (K, T, R, I, C, E, G)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class CoreState:
    """
    Immutable snapshot of the MetaCore.

    Attributes
    ----------
    core_id      : Unique identifier for this core instance.
    generation   : Monotonically increasing update counter.
    created_at   : UTC timestamp of creation.
    updated_at   : UTC timestamp of last update.
    metadata     : Arbitrary key-value annotations.
    """

    core_id: str
    generation: int = 0
    created_at: datetime = field(default_factory=_utcnow)
    updated_at: datetime = field(default_factory=_utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)

    # ── Aggregate counters (kept in sync by MetaCore) ─────────────────────
    knowledge_nodes: int = 0
    timeline_nodes: int = 0
    reality_count: int = 0
    active_clones: int = 0
    causal_edges: int = 0
    audit_entries: int = 0

    def increment_generation(self) -> None:
        """Advance to the next generation and stamp the update time."""
        self.generation += 1
        self.updated_at = _utcnow()

    def to_dict(self) -> dict[str, Any]:
        return {
            "core_id": self.core_id,
            "generation": self.generation,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "knowledge_nodes": self.knowledge_nodes,
            "timeline_nodes": self.timeline_nodes,
            "reality_count": self.reality_count,
            "active_clones": self.active_clones,
            "causal_edges": self.causal_edges,
            "audit_entries": self.audit_entries,
            "metadata": self.metadata,
        }
