"""
Update Engine — implements the formal MetaCore update rule.

    M_{t+1} = F(M_t, O_t)

This module isolates the state-transition logic so it can be
tested independently of the full MetaCore.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from loguru import logger

if TYPE_CHECKING:
    from mrif.core.meta_core import MetaCore


class UpdateEngine:
    """
    Applies a batch of observations to a MetaCore, producing the next state.

    Separating the update logic from MetaCore keeps the orchestrator lean
    and makes the transition function unit-testable in isolation.
    """

    def __init__(self, core: "MetaCore") -> None:
        self._core = core

    def apply(self, observations: list[dict[str, Any]]) -> int:
        """
        Apply all *observations* to the core and advance one generation.

        Returns the new generation number.
        """
        logger.debug(f"UpdateEngine: applying {len(observations)} observations")

        for obs in observations:
            self._apply_single(obs)

        self._sync_counters()
        self._core.state.increment_generation()

        logger.debug(f"UpdateEngine: generation → {self._core.state.generation}")
        return self._core.state.generation

    def _apply_single(self, obs: dict[str, Any]) -> None:
        """Route one observation to the appropriate dimension handlers."""
        core = self._core

        # Validate first
        core.constitution.validate(obs)

        # K — Knowledge
        if k := obs.get("knowledge"):
            for c in k.get("concepts", []):
                core.knowledge.add_concept(c["id"], c.get("attrs", {}))
            for r in k.get("relations", []):
                core.knowledge.add_relation(r["src"], r["dst"], r.get("kind", "related"))

        # T — Timeline
        if t := obs.get("timeline"):
            core.timeline.record_event(
                event_id=t.get("event_id"),
                label=t.get("label", ""),
                parent_id=t.get("parent_id"),
                metadata=t.get("metadata", {}),
            )

        # C — Causality
        if a := obs.get("action"):
            core.causality.record_action(
                action_id=a.get("id"),
                action_type=a.get("type", "unknown"),
                context=a.get("context", {}),
                caused_by=a.get("caused_by"),
            )

        # R — Reality snapshot
        if r := obs.get("reality"):
            rid = r.get("reality_id")
            fitness = r.get("fitness")
            if rid and fitness is not None:
                core.reality.update_fitness(rid, fitness)

        # Working memory cache
        core.working_memory.push(obs)

        # Audit
        core.audit.record("observation", core.state.core_id, obs)

    def _sync_counters(self) -> None:
        """Keep CoreState aggregate counters in sync with live dimensions."""
        core = self._core
        core.state.knowledge_nodes = core.knowledge.size()
        core.state.timeline_nodes = core.timeline.node_count()
        core.state.reality_count = core.reality.count()
        core.state.active_clones = core.identity.get_active_count()
        core.state.causal_edges = core.causality.edge_count()
        core.state.audit_entries = core.audit.count()

    def dry_run(self, observations: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Validate observations without mutating state.

        Returns a report of what would change.
        """
        from mrif.exceptions import ConstitutionalViolationError

        report: dict[str, Any] = {
            "total": len(observations),
            "valid": 0,
            "violations": [],
            "projected_knowledge_delta": 0,
        }
        for i, obs in enumerate(observations):
            try:
                self._core.constitution.validate(obs)
                report["valid"] += 1
                if k := obs.get("knowledge"):
                    report["projected_knowledge_delta"] += len(k.get("concepts", []))
            except ConstitutionalViolationError as exc:
                report["violations"].append({"index": i, "reason": str(exc)})
        return report
