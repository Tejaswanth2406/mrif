"""Tests for EvolutionTracker (Dimension E)."""
from __future__ import annotations

from mrif.dimensions.evolution import EvolutionTracker


def test_initial_fitness_zero(evolution_tracker):
    assert evolution_tracker.current_fitness() == 0.0


def test_evaluate_returns_score(evolution_tracker):
    score = evolution_tracker.evaluate(knowledge_size=50, reality_count=5, generation=1)
    assert 0.0 <= score <= 1.0


def test_fitness_increases_with_knowledge(evolution_tracker):
    evolution_tracker.evaluate(knowledge_size=10, reality_count=1, generation=1)
    s1 = evolution_tracker.current_fitness()
    evolution_tracker.evaluate(knowledge_size=100, reality_count=1, generation=2)
    s2 = evolution_tracker.current_fitness()
    assert s2 >= s1


def test_history_grows(evolution_tracker):
    for i in range(5):
        evolution_tracker.evaluate(knowledge_size=i * 10, reality_count=i, generation=i)
    assert len(evolution_tracker.fitness_trend(10)) == 5


def test_fitness_trend_bounded(evolution_tracker):
    for i in range(20):
        evolution_tracker.evaluate(knowledge_size=i, reality_count=1, generation=i)
    trend = evolution_tracker.fitness_trend(5)
    assert len(trend) == 5


def test_is_improving(evolution_tracker):
    evolution_tracker.evaluate(knowledge_size=10, reality_count=1, generation=1)
    evolution_tracker.evaluate(knowledge_size=50, reality_count=3, generation=2)
    evolution_tracker.evaluate(knowledge_size=200, reality_count=10, generation=3)
    assert evolution_tracker.is_improving() is True


def test_peak_fitness(evolution_tracker):
    evolution_tracker.evaluate(knowledge_size=100, reality_count=5, generation=1)
    peak = evolution_tracker.peak_fitness()
    evolution_tracker.evaluate(knowledge_size=0, reality_count=0, generation=2)
    assert evolution_tracker.peak_fitness() == peak


def test_peak_fitness_no_history():
    tracker = EvolutionTracker()
    assert tracker.peak_fitness() == 0.0


def test_is_improving_insufficient_data(evolution_tracker):
    evolution_tracker.evaluate(knowledge_size=10, reality_count=1, generation=1)
    assert evolution_tracker.is_improving() is False


def test_knowledge_growth_rate(evolution_tracker):
    evolution_tracker.evaluate(knowledge_size=10, reality_count=1, generation=1)
    evolution_tracker.evaluate(knowledge_size=30, reality_count=1, generation=2)
    evolution_tracker.evaluate(knowledge_size=60, reality_count=1, generation=3)
    rate = evolution_tracker.knowledge_growth_rate()
    assert rate > 0


def test_export_format(evolution_tracker):
    evolution_tracker.evaluate(knowledge_size=20, reality_count=2, generation=1)
    rows = evolution_tracker.export()
    assert len(rows) == 1
    assert "generation" in rows[0]
    assert "fitness" in rows[0]
    assert "timestamp" in rows[0]


def test_safety_score_affects_fitness(evolution_tracker):
    s_safe = evolution_tracker.evaluate(
        knowledge_size=50, reality_count=5, generation=1, safety_score=1.0
    )
    evolution_tracker2 = EvolutionTracker()
    s_unsafe = evolution_tracker2.evaluate(
        knowledge_size=50, reality_count=5, generation=1, safety_score=0.0
    )
    assert s_safe > s_unsafe
