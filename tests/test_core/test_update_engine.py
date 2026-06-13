"""Tests for UpdateEngine."""
from __future__ import annotations

from mrif.core.update_engine import UpdateEngine
from mrif.exceptions import ConstitutionalViolationError


def test_apply_advances_generation(core):
    engine = UpdateEngine(core)
    engine.apply([{"knowledge": {"concepts": [{"id": "x"}], "relations": []}}])
    assert core.state.generation == 1


def test_apply_updates_knowledge(core, sample_observation):
    engine = UpdateEngine(core)
    engine.apply([sample_observation])
    assert core.knowledge.size() >= 2


def test_apply_updates_counters(core, sample_observation):
    engine = UpdateEngine(core)
    engine.apply([sample_observation])
    assert core.state.knowledge_nodes == core.knowledge.size()
    assert core.state.causal_edges == core.causality.edge_count()


def test_apply_multiple_observations(core, sample_observation):
    engine = UpdateEngine(core)
    engine.apply([sample_observation, sample_observation])
    assert core.state.generation == 1


def test_apply_returns_generation(core, sample_observation):
    engine = UpdateEngine(core)
    gen = engine.apply([sample_observation])
    assert gen == 1


def test_dry_run_does_not_mutate(core, sample_observation):
    engine = UpdateEngine(core)
    before_gen = core.state.generation
    before_k = core.knowledge.size()
    engine.dry_run([sample_observation])
    assert core.state.generation == before_gen
    assert core.knowledge.size() == before_k


def test_dry_run_counts_valid(core, sample_observation):
    engine = UpdateEngine(core)
    report = engine.dry_run([sample_observation])
    assert report["valid"] == 1


def test_dry_run_detects_violations(core):
    engine = UpdateEngine(core)
    report = engine.dry_run([{"ethics_override": True}])
    assert report["violations"][0]["index"] == 0


def test_dry_run_projects_knowledge_delta(core):
    engine = UpdateEngine(core)
    obs = {"knowledge": {"concepts": [{"id": "a"}, {"id": "b"}], "relations": []}}
    report = engine.dry_run([obs])
    assert report["projected_knowledge_delta"] == 2


def test_apply_with_causality(core):
    engine = UpdateEngine(core)
    obs = {"action": {"id": "a1", "type": "test", "context": {}}}
    engine.apply([obs])
    assert core.causality.node_count() >= 1


def test_apply_with_reality_fitness(core):
    engine = UpdateEngine(core)
    rid = list(core.reality.list_ids())[0]
    obs = {"reality": {"reality_id": rid, "fitness": 0.77}}
    engine.apply([obs])
    r = core.reality.get(rid)
    assert abs(r.fitness - 0.77) < 0.001
