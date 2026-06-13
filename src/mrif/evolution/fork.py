"""
Fork Manager — creates divergent branches of the MetaCore for parallel evolution.

Pattern:
    Observe → Fork (A, B, C) → Each branch evolves independently
             → Evaluate fitness → Merge best branch back → Retire losers
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Fork:
    """Represents one evolutionary branch."""

    fork_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    parent_id: str = ""
    hypothesis: str = ""          # the evolutionary hypothesis being tested
    parameters: dict[str, Any] = field(default_factory=dict)
    fitness: float = 0.0
    is_active: bool = True
    generation_created: int = 0


class ForkManager:
    """
    Creates and tracks evolutionary branches.

    Forks are cheap snapshots of parameter sets, not full MetaCore instances.
    The MetaCore's RealityEngine is used to run separate simulations per fork.
    """

    def __init__(self) -> None:
        self._forks: dict[str, Fork] = {}

    def create_fork(
        self,
        parent_id: str,
        hypothesis: str,
        parameters: dict[str, Any],
        generation: int = 0,
    ) -> Fork:
        """Create a new evolutionary fork."""
        fork = Fork(
            parent_id=parent_id,
            hypothesis=hypothesis,
            parameters=parameters,
            generation_created=generation,
        )
        self._forks[fork.fork_id] = fork
        return fork

    def update_fitness(self, fork_id: str, fitness: float) -> None:
        if fork_id in self._forks:
            self._forks[fork_id].fitness = fitness

    def retire(self, fork_id: str) -> None:
        if fork_id in self._forks:
            self._forks[fork_id].is_active = False

    def best(self, n: int = 1) -> list[Fork]:
        """Return the *n* forks with highest fitness."""
        active = [f for f in self._forks.values() if f.is_active]
        return sorted(active, key=lambda f: f.fitness, reverse=True)[:n]

    def active_count(self) -> int:
        return sum(1 for f in self._forks.values() if f.is_active)

    def all_forks(self) -> list[Fork]:
        return list(self._forks.values())
