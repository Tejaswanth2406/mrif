"""Tests for ExperimentPlanner."""
from __future__ import annotations

from mrif.research.experiment import ExperimentPlanner, ExperimentStatus


def test_plan_creates_experiment():
    planner = ExperimentPlanner()
    plan = planner.plan("hyp-1", "If X then Y.")
    assert plan is not None
    assert plan.hypothesis_id == "hyp-1"


def test_plan_initial_status_is_planned():
    planner = ExperimentPlanner()
    plan = planner.plan("hyp-1", "stmt")
    assert plan.status == ExperimentStatus.PLANNED


def test_plan_has_description():
    planner = ExperimentPlanner()
    plan = planner.plan("hyp-1", "Test statement")
    assert "Test statement" in plan.description


def test_plan_uses_first_available_method():
    planner = ExperimentPlanner()
    plan = planner.plan("h1", "stmt", available_methods=["survey", "simulation"])
    assert plan.method == "survey"


def test_plan_default_method_simulation():
    planner = ExperimentPlanner()
    plan = planner.plan("h1", "stmt")
    assert plan.method == "simulation"


def test_mark_running(experiment_plan):
    experiment_plan.mark_running()
    assert experiment_plan.status == ExperimentStatus.RUNNING


def test_complete(experiment_plan):
    experiment_plan.complete({"p_value": 0.03})
    assert experiment_plan.status == ExperimentStatus.COMPLETED
    assert experiment_plan.result["p_value"] == 0.03


def test_fail(experiment_plan):
    experiment_plan.fail("timeout")
    assert experiment_plan.status == ExperimentStatus.FAILED
    assert "timeout" in experiment_plan.result["error"]


def test_plan_has_variables():
    planner = ExperimentPlanner()
    plan = planner.plan("h1", "stmt")
    assert isinstance(plan.variables, dict)
    assert "iterations" in plan.variables


import pytest

@pytest.fixture
def experiment_plan():
    planner = ExperimentPlanner()
    return planner.plan("h-test", "Test hypothesis statement.")
