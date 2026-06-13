"""
Dimension R — Reality Engine.

Each "reality" is a parameterised world model with its own physical,
social, and epistemic assumptions.  The MetaCore can run many realities
in parallel and cross-breed them via mutation.

    C = Mutate(A, B)   # evolutionary crossover of two realities
"""
from __future__ import annotations

import random
import uuid
from dataclasses import dataclass, field
from typing import Any

from mrif.exceptions import RealityNotFoundError


@dataclass
class RealityModel:
    """
    A single parameterised universe.

    Attributes
    ----------
    reality_id    : Unique identifier.
    name          : Human-readable name.
    assumptions   : Physical / social / epistemic parameters.
    parent_ids    : IDs of realities this one was derived from.
    fitness       : Heuristic quality score (higher = better).
    """

    reality_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "unnamed"
    assumptions: dict[str, Any] = field(default_factory=dict)
    parent_ids: list[str] = field(default_factory=list)
    fitness: float = 0.0
    generation: int = 0

    @classmethod
    def default(cls) -> "RealityModel":
        """Baseline Newtonian-ish reality."""
        return cls(
            reality_id="reality-default",
            name="Baseline",
            assumptions={
                "space_dimensions": 3,
                "time_dimensions": 1,
                "gravity": "inverse_square",
                "energy_conservation": True,
                "causality": "forward",
                "information_speed": "finite",
            },
        )


class RealityEngine:
    """
    Container and factory for multiple RealityModel instances.
    """

    def __init__(self) -> None:
        self._realities: dict[str, RealityModel] = {}
        # Always start with a baseline
        base = RealityModel.default()
        self._realities[base.reality_id] = base

    # ── CRUD ────────────────────────────────────────────────────────────────

    def create(self, name: str, assumptions: dict[str, Any]) -> str:
        """Instantiate a new reality from scratch."""
        r = RealityModel(name=name, assumptions=assumptions)
        self._realities[r.reality_id] = r
        return r.reality_id

    def get(self, reality_id: str) -> RealityModel:
        try:
            return self._realities[reality_id]
        except KeyError:
            raise RealityNotFoundError(reality_id)

    def delete(self, reality_id: str) -> None:
        if reality_id not in self._realities:
            raise RealityNotFoundError(reality_id)
        del self._realities[reality_id]

    # ── Fork & Mutate ────────────────────────────────────────────────────────

    def fork(self, reality_id: str, name: str | None = None) -> str:
        """Create an exact copy of an existing reality."""
        src = self.get(reality_id)
        child = RealityModel(
            name=name or f"{src.name}-fork",
            assumptions=dict(src.assumptions),
            parent_ids=[reality_id],
            generation=src.generation + 1,
        )
        self._realities[child.reality_id] = child
        return child.reality_id

    def mutate(self, reality_id_a: str, reality_id_b: str) -> str:
        """
        Crossover two realities to create a child:  C = Mutate(A, B).

        For each assumption key, randomly select the value from A or B,
        then apply a small perturbation to numeric values.
        """
        a = self.get(reality_id_a)
        b = self.get(reality_id_b)

        merged_assumptions: dict[str, Any] = {}
        all_keys = set(a.assumptions) | set(b.assumptions)
        for key in all_keys:
            if key in a.assumptions and key in b.assumptions:
                val = random.choice([a.assumptions[key], b.assumptions[key]])
            elif key in a.assumptions:
                val = a.assumptions[key]
            else:
                val = b.assumptions[key]

            # Numeric perturbation ±10 %
            if isinstance(val, (int, float)):
                val = val * random.uniform(0.9, 1.1)
                val = type(a.assumptions.get(key, val))(val)  # preserve int/float

            merged_assumptions[key] = val

        child = RealityModel(
            name=f"mutant({a.name}×{b.name})",
            assumptions=merged_assumptions,
            parent_ids=[reality_id_a, reality_id_b],
            generation=max(a.generation, b.generation) + 1,
        )
        self._realities[child.reality_id] = child
        return child.reality_id

    # ── Query & Metrics ──────────────────────────────────────────────────────

    def compare(self, reality_id_a: str, reality_id_b: str) -> dict[str, Any]:
        """Return assumption differences between two realities."""
        a = self.get(reality_id_a)
        b = self.get(reality_id_b)
        diff: dict[str, Any] = {}
        all_keys = set(a.assumptions) | set(b.assumptions)
        for k in all_keys:
            va, vb = a.assumptions.get(k), b.assumptions.get(k)
            if va != vb:
                diff[k] = {"a": va, "b": vb}
        return diff

    def rank_by_fitness(self) -> list[RealityModel]:
        return sorted(self._realities.values(), key=lambda r: r.fitness, reverse=True)

    def update_fitness(self, reality_id: str, fitness: float) -> None:
        self.get(reality_id).fitness = fitness

    def count(self) -> int:
        return len(self._realities)

    def list_ids(self) -> list[str]:
        return list(self._realities.keys())
