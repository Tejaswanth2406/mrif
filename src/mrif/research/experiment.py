"""
Experiment Planner — translates a hypothesis into a verifiable experiment plan.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class ExperimentStatus(str, Enum):
    PLANNED = "planned"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ExperimentPlan:
    """A single experiment designed to test a hypothesis."""

    plan_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    hypothesis_id: str = ""
    description: str = ""
    method: str = "simulation"           # simulation | survey | analysis
    variables: dict[str, Any] = field(default_factory=dict)
    expected_outcome: str = ""
    status: ExperimentStatus = ExperimentStatus.PLANNED
    result: dict[str, Any] | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def mark_running(self) -> None:
        self.status = ExperimentStatus.RUNNING

    def complete(self, result: dict[str, Any]) -> None:
        self.result = result
        self.status = ExperimentStatus.COMPLETED

    def fail(self, reason: str) -> None:
        self.result = {"error": reason}
        self.status = ExperimentStatus.FAILED


class ExperimentPlanner:
    """Maps a hypothesis to a concrete experiment plan."""

    def plan(
        self,
        hypothesis_id: str,
        statement: str,
        available_methods: list[str] | None = None,
    ) -> ExperimentPlan:
        """
        Create an experiment plan for *hypothesis_id*.

        Parameters
        ----------
        hypothesis_id : str
            ID of the hypothesis being tested.
        statement     : str
            The hypothesis statement text.
        available_methods : list[str]
            Methods the system can execute.
        """
        method = (available_methods or ["simulation"])[0]

        return ExperimentPlan(
            hypothesis_id=hypothesis_id,
            description=f"Experiment to test: '{statement}'",
            method=method,
            variables={"iterations": 1000, "seed": 42},
            expected_outcome="Hypothesis will be confirmed or rejected at p < 0.05",
        )
