"""
MetaCore — central orchestrator of the MRIF system.

Implements the update rule:  M_{t+1} = F(M_t, O_t)

The MetaCore holds references to all seven dimensions:
    K  Knowledge, T  Timeline, R  Reality,
    I  Identity,  C  Causality, E  Evolution, G  Governance
"""
from __future__ import annotations

from typing import Any

from loguru import logger

from mrif.config import settings
from mrif.core.state import CoreState
from mrif.dimensions.causality import CausalGraph
from mrif.dimensions.evolution import EvolutionTracker
from mrif.dimensions.identity import IdentityRegistry
from mrif.dimensions.knowledge import KnowledgeGraph
from mrif.dimensions.reality import RealityEngine
from mrif.dimensions.timeline import TimelineEngine
from mrif.exceptions import ConstitutionalViolationError, MaxForksExceededError
from mrif.governance.audit import AuditLog
from mrif.governance.constitutional import ConstitutionalConstraints
from mrif.memory.collective import CollectiveMemory
from mrif.memory.working import WorkingMemory


class MetaCore:
    """
    The Meta-Recursive Intelligence Core.

    Parameters
    ----------
    core_id : str
        Unique identifier. Defaults to the value in settings.
    """

    def __init__(self, core_id: str | None = None) -> None:
        _id = core_id or settings.core_id
        self.state = CoreState(core_id=_id)

        # ── Dimension K — Knowledge ──────────────────────────────────────
        self.knowledge: KnowledgeGraph = KnowledgeGraph()

        # ── Dimension T — Timelines ──────────────────────────────────────
        self.timeline: TimelineEngine = TimelineEngine()

        # ── Dimension R — Realities ──────────────────────────────────────
        self.reality: RealityEngine = RealityEngine()

        # ── Dimension I — Identities ─────────────────────────────────────
        self.identity: IdentityRegistry = IdentityRegistry(_id)

        # ── Dimension C — Causality ──────────────────────────────────────
        self.causality: CausalGraph = CausalGraph()

        # ── Dimension E — Evolution ──────────────────────────────────────
        self.evolution: EvolutionTracker = EvolutionTracker()

        # ── Dimension G — Governance ─────────────────────────────────────
        self.constitution: ConstitutionalConstraints = ConstitutionalConstraints()
        self.audit: AuditLog = AuditLog()

        # ── Memory stack ─────────────────────────────────────────────────
        self.working_memory: WorkingMemory = WorkingMemory(
            limit=settings.working_memory_limit
        )
        self.collective_memory: CollectiveMemory = CollectiveMemory()

        logger.info(f"MetaCore '{_id}' initialised at generation {self.state.generation}")
        self.audit.record(
            event_type="core_init",
            model_id=_id,
            data={"generation": 0},
        )

    # ── Public API ──────────────────────────────────────────────────────────

    def observe(self, observation: dict[str, Any]) -> None:
        """
        Ingest a single observation from a descendant.

        Observation schema (all keys optional):
            knowledge   : { concepts: [...], relations: [...] }
            timeline    : { event_id, label, parent_id? }
            action      : { id, type, context }
            reality_id  : str   (pin to a specific reality)
        """
        try:
            self.constitution.validate(observation)
        except ConstitutionalViolationError:
            self.audit.record("constitution_violation", self.state.core_id, observation)
            raise

        # K — integrate new knowledge
        if k := observation.get("knowledge"):
            for c in k.get("concepts", []):
                self.knowledge.add_concept(c["id"], c.get("attrs", {}))
            for r in k.get("relations", []):
                self.knowledge.add_relation(r["src"], r["dst"], r.get("kind", "related"))

        # T — record timeline event
        if t := observation.get("timeline"):
            self.timeline.record_event(
                event_id=t["event_id"],
                label=t.get("label", ""),
                parent_id=t.get("parent_id"),
            )

        # C — causal action
        if a := observation.get("action"):
            self.causality.record_action(
                action_id=a["id"],
                action_type=a.get("type", "unknown"),
                context=a.get("context", {}),
            )

        # Working memory cache
        self.working_memory.push(observation)

        if settings.audit_enabled:
            self.audit.record("observation", self.state.core_id, observation)

        logger.debug(f"MetaCore observed: {list(observation.keys())}")

    def update(self, observations: list[dict[str, Any]]) -> CoreState:
        """
        Core update rule:  M_{t+1} = F(M_t, O_t)

        Processes all observations then advances the generation counter.
        """
        for obs in observations:
            self.observe(obs)

        # E — re-evaluate evolution fitness
        self.evolution.evaluate(
            knowledge_size=self.knowledge.size(),
            reality_count=self.reality.count(),
            generation=self.state.generation,
        )

        # Sync aggregate counters into state
        self.state.knowledge_nodes = self.knowledge.size()
        self.state.timeline_nodes = self.timeline.node_count()
        self.state.reality_count = self.reality.count()
        self.state.active_clones = self.identity.get_active_count()
        self.state.causal_edges = self.causality.edge_count()
        self.state.audit_entries = self.audit.count()

        self.state.increment_generation()

        self.audit.record(
            "generation_advance",
            self.state.core_id,
            {"new_generation": self.state.generation},
        )
        logger.info(f"MetaCore → generation {self.state.generation}")
        return self.state

    def spawn_clone(
        self,
        goal: str,
        permissions: list[str] | None = None,
    ) -> str:
        """
        Spawn a descendant agent authorised to pursue *goal*.

        Returns the clone's unique identifier.
        """
        if self.identity.get_active_count() >= settings.max_forks:
            raise MaxForksExceededError(
                f"Cannot spawn clone: max_forks ({settings.max_forks}) reached."
            )

        clone_id = self.identity.register_clone(
            parent_id=self.state.core_id,
            goal=goal,
            permissions=permissions or ["read_global_memory"],
        )

        # Share a knowledge snapshot with the new clone
        snapshot = self.knowledge.export_snapshot()
        self.collective_memory.store(clone_id, "initial_knowledge", snapshot)

        self.audit.record(
            "clone_spawned",
            self.state.core_id,
            {"clone_id": clone_id, "goal": goal, "permissions": permissions},
        )
        logger.info(f"Spawned clone '{clone_id}' for goal: {goal}")
        return clone_id

    def absorb_clone(self, clone_id: str, learnings: dict[str, Any]) -> None:
        """
        Merge a clone's findings back into the core.
        The clone is then retired.
        """
        self.observe({"knowledge": learnings.get("knowledge", {}),
                      "action": learnings.get("action", {})})
        self.identity.retire_clone(clone_id)
        self.audit.record("clone_absorbed", self.state.core_id,
                          {"clone_id": clone_id})
        logger.info(f"Absorbed clone '{clone_id}'")

    def get_summary(self) -> dict[str, Any]:
        """Return a human-readable summary of current MetaCore state."""
        return {
            **self.state.to_dict(),
            "evolution_fitness": self.evolution.current_fitness(),
        }
