"""Tests for MetaCore — the central MRIF orchestrator."""
from __future__ import annotations

import pytest

from mrif.core.meta_core import MetaCore
from mrif.exceptions import ConstitutionalViolationError, MaxForksExceededError


def test_init(core):
    assert core.state.core_id == "TEST-CORE"
    assert core.state.generation == 0


def test_observe_knowledge(core, sample_observation):
    core.observe(sample_observation)
    assert core.knowledge.size() >= 2


def test_observe_adds_timeline_event(core, sample_observation):
    before = core.timeline.node_count()
    core.observe(sample_observation)
    assert core.timeline.node_count() > before


def test_observe_adds_causal_action(core, sample_observation):
    core.observe(sample_observation)
    assert core.causality.node_count() >= 1


def test_update_advances_generation(core, sample_observation):
    state = core.update([sample_observation, sample_observation])
    assert state.generation == 1


def test_update_syncs_counters(core, sample_observation):
    state = core.update([sample_observation])
    assert state.knowledge_nodes == core.knowledge.size()
    assert state.timeline_nodes == core.timeline.node_count()


def test_spawn_clone(core):
    clone_id = core.spawn_clone(goal="test_goal")
    assert clone_id is not None
    assert core.identity.get_active_count() == 2  # core + clone


def test_spawn_clone_stores_knowledge_snapshot(core, sample_observation):
    core.observe(sample_observation)
    clone_id = core.spawn_clone(goal="research")
    snapshot = core.collective_memory.fetch(clone_id, "initial_knowledge")
    assert snapshot is not None
    assert "concepts" in snapshot


def test_spawn_clone_permissions(core):
    clone_id = core.spawn_clone(goal="limited", permissions=["read_global_memory"])
    agent = core.identity.get(clone_id)
    assert agent is not None
    assert "read_global_memory" in agent.permissions


def test_absorb_clone(core):
    clone_id = core.spawn_clone(goal="research")
    core.absorb_clone(clone_id, learnings={
        "knowledge": {"concepts": [{"id": "absorbed-concept"}], "relations": []}
    })
    agent = core.identity.get(clone_id)
    assert agent.status == "retired"


def test_max_forks_exceeded(tmp_path):
    from mrif.config import MRIFSettings
    import os
    os.environ["MRIF_MAX_FORKS"] = "2"
    os.environ["MRIF_DB_URL"] = f"sqlite:///{tmp_path}/test.db"
    from importlib import reload
    import mrif.config as cfg_mod
    import mrif.core.meta_core as mc_mod
    reload(cfg_mod)
    reload(mc_mod)

    c = mc_mod.MetaCore(core_id="FORK-TEST")
    c.spawn_clone("goal1")
    with pytest.raises(MaxForksExceededError):
        c.spawn_clone("goal2")

    # cleanup
    del os.environ["MRIF_MAX_FORKS"]


def test_constitutional_violation_rejected(core):
    with pytest.raises(ConstitutionalViolationError):
        core.observe({"ethics_override": True})


def test_get_summary(core):
    summary = core.get_summary()
    assert "core_id" in summary
    assert "generation" in summary
    assert "evolution_fitness" in summary


def test_audit_records_observation(core, sample_observation):
    before = core.audit.count()
    core.observe(sample_observation)
    assert core.audit.count() > before


def test_update_returns_state(core, sample_observation):
    from mrif.core.state import CoreState
    result = core.update([sample_observation])
    assert isinstance(result, CoreState)
