"""
Dimension I — Identity Registry.

Tracks every agent (core + clones) with full lineage metadata —
like Git, but for intelligence instances.

YAML schema per agent:
    parent_id     : str
    lineage       : list[str]
    permissions   : list[str]
    knowledge_scope: str
    ethics_profile : str
    goal           : str
    status         : active | retired | archived
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class AgentIdentity(BaseModel):
    """Validated identity record for one agent."""

    agent_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    parent_id: str | None = None
    lineage: list[str] = Field(default_factory=list)
    permissions: list[str] = Field(default_factory=list)
    knowledge_scope: str = "local"
    ethics_profile: str = "default"
    goal: str = ""
    status: str = "active"  # active | retired | archived
    created_at: datetime = Field(default_factory=_utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)


class IdentityRegistry:
    """
    Maintains the full lineage graph of all agents spawned from this core.
    """

    def __init__(self, core_id: str) -> None:
        self._core_id = core_id
        self._agents: dict[str, AgentIdentity] = {}

        # Register the core itself
        root = AgentIdentity(
            agent_id=core_id,
            parent_id=None,
            lineage=[core_id],
            permissions=["all"],
            knowledge_scope="global",
            goal="meta-recursive-intelligence",
        )
        self._agents[core_id] = root

    # ── Registration ─────────────────────────────────────────────────────────

    def register_clone(
        self,
        parent_id: str,
        goal: str,
        permissions: list[str] | None = None,
        knowledge_scope: str = "local",
        ethics_profile: str = "default",
    ) -> str:
        """Create and register a new descendant agent."""
        parent = self._agents.get(parent_id)
        parent_lineage = parent.lineage if parent else []

        agent = AgentIdentity(
            parent_id=parent_id,
            lineage=[*parent_lineage, str(uuid.uuid4())],
            permissions=permissions or ["read_global_memory"],
            knowledge_scope=knowledge_scope,
            ethics_profile=ethics_profile,
            goal=goal,
        )
        self._agents[agent.agent_id] = agent
        return agent.agent_id

    # ── Status mutations ────────────────────────────────────────────────────

    def retire_clone(self, agent_id: str) -> None:
        """Mark a clone as retired (completed its mission)."""
        if agent_id in self._agents:
            self._agents[agent_id].status = "retired"

    def archive_clone(self, agent_id: str) -> None:
        """Archive a clone — softer than deletion."""
        if agent_id in self._agents:
            self._agents[agent_id].status = "archived"

    # ── Query ────────────────────────────────────────────────────────────────

    def get(self, agent_id: str) -> AgentIdentity | None:
        return self._agents.get(agent_id)

    def get_active_count(self) -> int:
        return sum(1 for a in self._agents.values() if a.status == "active")

    def get_lineage(self, agent_id: str) -> list[str]:
        a = self._agents.get(agent_id)
        return a.lineage if a else []

    def has_permission(self, agent_id: str, permission: str) -> bool:
        a = self._agents.get(agent_id)
        if not a:
            return False
        return "all" in a.permissions or permission in a.permissions

    def list_active(self) -> list[AgentIdentity]:
        return [a for a in self._agents.values() if a.status == "active"]

    def export(self) -> list[dict[str, Any]]:
        return [a.model_dump() for a in self._agents.values()]
