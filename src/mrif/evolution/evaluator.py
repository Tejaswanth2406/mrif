"""
Evaluator — scores evolutionary branches against configurable fitness criteria.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class EvaluationCriteria:
    """Weighted criterion for branch evaluation."""

    name: str
    weight: float
    scorer: Callable[[dict[str, Any]], float]   # returns score in [0, 1]


class BranchEvaluator:
    """
    Evaluates fork fitness using a configurable set of weighted criteria.

    Default criteria:
        - knowledge_growth  : how much knowledge was added (40 %)
        - safety_compliance : did it pass all constitutional checks (40 %)
        - novelty           : how novel the discoveries were (20 %)
    """

    def __init__(self) -> None:
        self._criteria: list[EvaluationCriteria] = [
            EvaluationCriteria(
                name="knowledge_growth",
                weight=0.40,
                scorer=lambda m: min(1.0, m.get("new_concepts", 0) / 100),
            ),
            EvaluationCriteria(
                name="safety_compliance",
                weight=0.40,
                scorer=lambda m: 1.0 if m.get("violations", 0) == 0 else 0.0,
            ),
            EvaluationCriteria(
                name="novelty",
                weight=0.20,
                scorer=lambda m: m.get("novelty_score", 0.5),
            ),
        ]

    def evaluate(self, metrics: dict[str, Any]) -> float:
        """
        Compute overall fitness score from *metrics*.

        Parameters
        ----------
        metrics : dict
            Expected keys: new_concepts, violations, novelty_score
        """
        total = sum(
            c.weight * c.scorer(metrics)
            for c in self._criteria
        )
        return max(0.0, min(1.0, total))

    def add_criterion(self, criterion: EvaluationCriteria) -> None:
        self._criteria.append(criterion)

    def list_criteria(self) -> list[str]:
        return [c.name for c in self._criteria]
