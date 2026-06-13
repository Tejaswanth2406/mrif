"""Tests for ResearchPipeline."""
from __future__ import annotations

import pytest
from mrif.research.pipeline import PipelineState, ResearchPipeline
from mrif.exceptions import HypothesisLimitError


def test_run_completes(pipeline):
    run = pipeline.run("Why does gravity exist?")
    assert run.state == PipelineState.COMPLETED


def test_run_produces_findings(pipeline):
    run = pipeline.run("What is dark matter?")
    assert run.findings != {}
    assert "question" in run.findings
    assert "confirmed" in run.findings


def test_run_links_question_text(pipeline):
    run = pipeline.run("How does memory form?")
    assert run.findings["question"] == "How does memory form?"


def test_run_generates_hypotheses(pipeline):
    run = pipeline.run("What causes inflation?")
    assert len(run.hypotheses) > 0


def test_run_generates_experiments(pipeline):
    run = pipeline.run("Why do stars collapse?")
    assert len(run.experiments) == len(run.hypotheses)


def test_run_has_timestamps(pipeline):
    run = pipeline.run("Test question")
    assert run.started_at is not None
    assert run.completed_at is not None


def test_run_completed_after_started(pipeline):
    run = pipeline.run("Timing test")
    assert run.completed_at >= run.started_at


def test_zero_max_hypotheses_fails():
    p = ResearchPipeline(max_hypotheses=0)
    run = p.run("Q?")
    assert run.state == PipelineState.FAILED
    assert run.error is not None


def test_get_run_by_id(pipeline):
    run = pipeline.run("Recall test")
    fetched = pipeline.get_run(run.run_id)
    assert fetched is not None
    assert fetched.run_id == run.run_id


def test_get_run_missing_returns_none(pipeline):
    assert pipeline.get_run("nonexistent") is None


def test_list_runs(pipeline):
    pipeline.run("Q1")
    pipeline.run("Q2")
    runs = pipeline.list_runs()
    assert len(runs) == 2


def test_list_runs_includes_state(pipeline):
    pipeline.run("Q")
    runs = pipeline.list_runs()
    assert "state" in runs[0]


def test_run_with_domain(pipeline):
    run = pipeline.run("Test?", domain="biology")
    assert run.state == PipelineState.COMPLETED


def test_hypotheses_have_final_status(pipeline):
    from mrif.research.hypothesis import HypothesisStatus
    run = pipeline.run("Final status check?")
    for h in run.hypotheses:
        assert h.status in (
            HypothesisStatus.CONFIRMED,
            HypothesisStatus.REJECTED,
            HypothesisStatus.PENDING,
        )
