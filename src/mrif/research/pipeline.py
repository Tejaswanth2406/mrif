"""
Research Pipeline — autonomous end-to-end research orchestration.

Stages:
    Question → Hypothesis → Experiment → Simulation → Verification → Publication

Each stage is independently retryable and auditable.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from loguru import logger

from mrif.exceptions import HypothesisLimitError, PipelineStageError
from mrif.research.experiment import ExperimentPlan, ExperimentPlanner, ExperimentStatus
from mrif.research.hypothesis import Hypothesis, HypothesisGenerator, HypothesisStatus


class PipelineState(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ResearchQuestion:
    question_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    text: str = ""
    domain: str = "general"
    priority: int = 5          # 1 (highest) – 10 (lowest)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class PipelineRun:
    """Full lifecycle of one research question through the pipeline."""

    run_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    question: ResearchQuestion | None = None
    hypotheses: list[Hypothesis] = field(default_factory=list)
    experiments: list[ExperimentPlan] = field(default_factory=list)
    findings: dict[str, Any] = field(default_factory=dict)
    state: PipelineState = PipelineState.IDLE
    error: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None


class ResearchPipeline:
    """
    Orchestrates the full research lifecycle.

    Usage
    -----
    pipeline = ResearchPipeline()
    run = pipeline.run("What drives protein misfolding in Alzheimer's disease?")
    print(run.findings)
    """

    def __init__(self, max_hypotheses: int = 3) -> None:
        self._max_hypotheses = max_hypotheses
        self._hyp_gen = HypothesisGenerator()
        self._exp_planner = ExperimentPlanner()
        self._runs: dict[str, PipelineRun] = {}

    def run(
        self,
        question_text: str,
        domain: str = "general",
        priority: int = 5,
        context: dict[str, Any] | None = None,
    ) -> PipelineRun:
        """
        Execute the full pipeline for *question_text*.

        Returns a completed (or failed) PipelineRun.
        """
        question = ResearchQuestion(text=question_text, domain=domain, priority=priority)
        pipeline_run = PipelineRun(question=question, state=PipelineState.RUNNING,
                                   started_at=datetime.now(timezone.utc))
        self._runs[pipeline_run.run_id] = pipeline_run

        try:
            pipeline_run = self._stage_hypothesize(pipeline_run, context)
            pipeline_run = self._stage_experiment(pipeline_run)
            pipeline_run = self._stage_simulate(pipeline_run)
            pipeline_run = self._stage_verify(pipeline_run)
            pipeline_run.state = PipelineState.COMPLETED
            pipeline_run.completed_at = datetime.now(timezone.utc)
            logger.info(f"Pipeline completed: run_id={pipeline_run.run_id}")
        except Exception as exc:
            pipeline_run.state = PipelineState.FAILED
            pipeline_run.error = str(exc)
            pipeline_run.completed_at = datetime.now(timezone.utc)
            logger.error(f"Pipeline failed: {exc}")

        return pipeline_run

    # ── Stages ────────────────────────────────────────────────────────────────

    def _stage_hypothesize(
        self, run: PipelineRun, context: dict[str, Any] | None
    ) -> PipelineRun:
        assert run.question is not None
        if self._max_hypotheses <= 0:
            raise HypothesisLimitError("max_hypotheses must be > 0")

        run.hypotheses = self._hyp_gen.generate(
            question=run.question.text,
            question_id=run.question.question_id,
            n=min(self._max_hypotheses, 3),
            context=context,
        )
        logger.debug(f"Generated {len(run.hypotheses)} hypotheses")
        return run

    def _stage_experiment(self, run: PipelineRun) -> PipelineRun:
        for h in run.hypotheses:
            plan = self._exp_planner.plan(
                hypothesis_id=h.hypothesis_id,
                statement=h.statement,
            )
            run.experiments.append(plan)
        return run

    def _stage_simulate(self, run: PipelineRun) -> PipelineRun:
        """Run each experiment (mock simulation in this scaffold)."""
        for exp in run.experiments:
            try:
                exp.mark_running()
                result = self._mock_simulate(exp)
                exp.complete(result)
            except Exception as exc:
                exp.fail(str(exc))
                raise PipelineStageError(f"Simulation failed: {exc}") from exc
        return run

    def _stage_verify(self, run: PipelineRun) -> PipelineRun:
        """Cross-check experiment results against hypotheses."""
        confirmed, rejected = 0, 0
        for h, exp in zip(run.hypotheses, run.experiments):
            if exp.status == ExperimentStatus.COMPLETED:
                p_value = (exp.result or {}).get("p_value", 0.5)
                if p_value < 0.05:
                    h.status = HypothesisStatus.CONFIRMED
                    h.update_confidence(+0.3)
                    confirmed += 1
                else:
                    h.status = HypothesisStatus.REJECTED
                    h.update_confidence(-0.3)
                    rejected += 1

        run.findings = {
            "question": run.question.text if run.question else "",
            "hypotheses_tested": len(run.hypotheses),
            "confirmed": confirmed,
            "rejected": rejected,
            "summary": (
                f"{confirmed} of {len(run.hypotheses)} hypotheses confirmed."
            ),
        }
        return run

    @staticmethod
    def _mock_simulate(exp: ExperimentPlan) -> dict[str, Any]:
        """Placeholder simulation — replace with real domain models."""
        import random
        random.seed(exp.variables.get("seed", 42))
        return {
            "p_value": random.uniform(0.01, 0.10),
            "effect_size": random.uniform(0.1, 0.9),
            "iterations": exp.variables.get("iterations", 1000),
        }

    # ── Query ─────────────────────────────────────────────────────────────────

    def get_run(self, run_id: str) -> PipelineRun | None:
        return self._runs.get(run_id)

    def list_runs(self) -> list[dict[str, Any]]:
        return [
            {
                "run_id": r.run_id,
                "question": r.question.text if r.question else "",
                "state": r.state,
                "completed_at": r.completed_at.isoformat() if r.completed_at else None,
            }
            for r in self._runs.values()
        ]
