"""
Hypothesis Generator — produces falsifiable hypotheses from a research question.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class HypothesisStatus(str, Enum):
    PENDING = "pending"
    TESTING = "testing"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    INCONCLUSIVE = "inconclusive"


@dataclass
class Hypothesis:
    """A single falsifiable hypothesis."""

    hypothesis_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    question_id: str = ""
    statement: str = ""
    rationale: str = ""
    confidence: float = 0.5          # prior probability [0, 1]
    status: HypothesisStatus = HypothesisStatus.PENDING
    evidence_for: list[str] = field(default_factory=list)
    evidence_against: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def update_confidence(self, delta: float) -> None:
        self.confidence = max(0.0, min(1.0, self.confidence + delta))
        self.updated_at = datetime.now(timezone.utc)


class HypothesisGenerator:
    """
    Generates a ranked list of hypotheses for a research question.

    In a full implementation this would call an LLM or domain model.
    Here we demonstrate the interface with a template-based approach.
    """

    TEMPLATES = [
        "If {condition} then {outcome}.",
        "The relationship between {a} and {b} is mediated by {c}.",
        "Increasing {variable} by 10% will {effect} {target}.",
        "There exists a mechanism by which {cause} produces {effect}.",
    ]

    def generate(
        self,
        question: str,
        question_id: str,
        n: int = 3,
        context: dict[str, Any] | None = None,
    ) -> list[Hypothesis]:
        """
        Generate *n* hypotheses for *question*.

        In production, this would integrate with an LLM backbone.
        """
        _ = context  # reserved for future context injection
        hypotheses: list[Hypothesis] = []
        for i in range(n):
            h = Hypothesis(
                question_id=question_id,
                statement=f"Hypothesis {i + 1} for: '{question}'",
                rationale=(
                    f"Derived from question structure using template "
                    f"{self.TEMPLATES[i % len(self.TEMPLATES)]}"
                ),
                confidence=0.5 - (i * 0.05),
            )
            hypotheses.append(h)
        return hypotheses
