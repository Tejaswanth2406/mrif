"""
Dimension E — Evolution Tracker.

Measures the fitness of the MetaCore across generations.

Fitness function:
    Φ = α·ΔK + β·ΔR + γ·safety_score

Where:
    ΔK  = knowledge growth rate
    ΔR  = reality count growth rate
    α, β, γ = configurable weights
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class GenerationSnapshot:
    """Metrics captured at a single generation."""

    generation: int
    knowledge_size: int
    reality_count: int
    fitness: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class EvolutionTracker:
    """
    Tracks capability growth, novelty, and reliability across generations.

    The fitness function weights can be adjusted at runtime.
    """

    ALPHA: float = 0.5   # knowledge weight
    BETA: float = 0.3    # reality weight
    GAMMA: float = 0.2   # safety / stability bonus

    def __init__(self) -> None:
        self._history: list[GenerationSnapshot] = []
        self._fitness: float = 0.0

    # ── Evaluation ──────────────────────────────────────────────────────────

    def evaluate(
        self,
        knowledge_size: int,
        reality_count: int,
        generation: int,
        safety_score: float = 1.0,
    ) -> float:
        """
        Compute fitness for the current generation and append to history.

        Returns the new fitness score.
        """
        # Growth deltas vs previous generation
        prev = self._history[-1] if self._history else None
        dk = (knowledge_size - prev.knowledge_size) if prev else knowledge_size
        dr = (reality_count - prev.reality_count) if prev else reality_count

        # Normalise to [0, 1] using sigmoid-like damping
        norm_dk = dk / (dk + 10 + 1)
        norm_dr = dr / (dr + 5 + 1)

        fitness = (
            self.ALPHA * norm_dk
            + self.BETA * norm_dr
            + self.GAMMA * safety_score
        )
        self._fitness = max(0.0, min(1.0, fitness))

        snap = GenerationSnapshot(
            generation=generation,
            knowledge_size=knowledge_size,
            reality_count=reality_count,
            fitness=self._fitness,
        )
        self._history.append(snap)
        return self._fitness

    # ── Query ────────────────────────────────────────────────────────────────

    def current_fitness(self) -> float:
        return self._fitness

    def fitness_trend(self, last_n: int = 10) -> list[float]:
        """Return fitness scores for the last *n* generations."""
        return [s.fitness for s in self._history[-last_n:]]

    def is_improving(self) -> bool:
        """True if the last 3 generations show a positive trend."""
        if len(self._history) < 3:
            return False
        trend = self.fitness_trend(3)
        return trend[-1] > trend[0]

    def peak_fitness(self) -> float:
        if not self._history:
            return 0.0
        return max(s.fitness for s in self._history)

    def knowledge_growth_rate(self) -> float:
        """Average ΔK per generation."""
        if len(self._history) < 2:
            return 0.0
        sizes = [s.knowledge_size for s in self._history]
        deltas = [b - a for a, b in zip(sizes, sizes[1:])]
        return sum(deltas) / len(deltas)

    def export(self) -> list[dict[str, Any]]:
        return [
            {
                "generation": s.generation,
                "knowledge_size": s.knowledge_size,
                "reality_count": s.reality_count,
                "fitness": s.fitness,
                "timestamp": s.timestamp.isoformat(),
            }
            for s in self._history
        ]
