"""Tests for BranchEvaluator."""
from __future__ import annotations


def test_perfect_metrics(evaluator):
    score = evaluator.evaluate({
        "new_concepts": 100,
        "violations": 0,
        "novelty_score": 1.0,
    })
    assert score > 0.5


def test_zero_metrics(evaluator):
    score = evaluator.evaluate({
        "new_concepts": 0,
        "violations": 0,
        "novelty_score": 0.0,
    })
    assert score >= 0.0


def test_violation_penalises_score(evaluator):
    safe = evaluator.evaluate({"new_concepts": 50, "violations": 0, "novelty_score": 0.5})
    unsafe = evaluator.evaluate({"new_concepts": 50, "violations": 1, "novelty_score": 0.5})
    assert safe > unsafe


def test_score_bounded_zero_one(evaluator):
    for metrics in [
        {"new_concepts": 9999, "violations": 0, "novelty_score": 1.0},
        {"new_concepts": 0, "violations": 1, "novelty_score": 0.0},
    ]:
        score = evaluator.evaluate(metrics)
        assert 0.0 <= score <= 1.0


def test_list_criteria(evaluator):
    criteria = evaluator.list_criteria()
    assert "knowledge_growth" in criteria
    assert "safety_compliance" in criteria
    assert "novelty" in criteria


def test_add_custom_criterion(evaluator):
    from mrif.evolution.evaluator import EvaluationCriteria
    evaluator.add_criterion(EvaluationCriteria(
        name="custom",
        weight=0.0,
        scorer=lambda m: 1.0,
    ))
    assert "custom" in evaluator.list_criteria()


def test_missing_keys_default_gracefully(evaluator):
    score = evaluator.evaluate({})  # all keys missing → use defaults
    assert 0.0 <= score <= 1.0


def test_higher_knowledge_better_score(evaluator):
    low = evaluator.evaluate({"new_concepts": 5, "violations": 0, "novelty_score": 0.5})
    high = evaluator.evaluate({"new_concepts": 80, "violations": 0, "novelty_score": 0.5})
    assert high > low
