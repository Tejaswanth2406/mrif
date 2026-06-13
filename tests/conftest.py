"""
Shared pytest fixtures for the MRIF test suite.
"""
from __future__ import annotations

import pytest

from mrif.core.meta_core import MetaCore
from mrif.dimensions.causality import CausalGraph
from mrif.dimensions.evolution import EvolutionTracker
from mrif.dimensions.identity import IdentityRegistry
from mrif.dimensions.knowledge import KnowledgeGraph
from mrif.dimensions.reality import RealityEngine
from mrif.dimensions.timeline import TimelineEngine
from mrif.evolution.evaluator import BranchEvaluator
from mrif.evolution.fork import ForkManager
from mrif.evolution.merger import KnowledgeMerger
from mrif.governance.audit import AuditLog
from mrif.governance.constitutional import ConstitutionalConstraints
from mrif.memory.collective import CollectiveMemory
from mrif.memory.episodic import EpisodicMemory
from mrif.memory.long_term import LongTermMemory
from mrif.memory.semantic import SemanticMemory
from mrif.memory.working import WorkingMemory
from mrif.research.pipeline import ResearchPipeline


# ── MetaCore ────────────────────────────────────────────────────────────────

@pytest.fixture
def core() -> MetaCore:
    """Fresh MetaCore with in-memory SQLite."""
    return MetaCore(core_id="TEST-CORE")


# ── Dimensions ───────────────────────────────────────────────────────────────

@pytest.fixture
def knowledge_graph() -> KnowledgeGraph:
    return KnowledgeGraph()


@pytest.fixture
def timeline_engine() -> TimelineEngine:
    return TimelineEngine()


@pytest.fixture
def reality_engine() -> RealityEngine:
    return RealityEngine()


@pytest.fixture
def identity_registry() -> IdentityRegistry:
    return IdentityRegistry("TEST-CORE")


@pytest.fixture
def causal_graph() -> CausalGraph:
    return CausalGraph()


@pytest.fixture
def evolution_tracker() -> EvolutionTracker:
    return EvolutionTracker()


# ── Memory ───────────────────────────────────────────────────────────────────

@pytest.fixture
def working_memory() -> WorkingMemory:
    return WorkingMemory(limit=10)


@pytest.fixture
def long_term_memory(tmp_path) -> LongTermMemory:
    db_url = f"sqlite:///{tmp_path}/test.db"
    return LongTermMemory(agent_id="test-agent", db_url=db_url)


@pytest.fixture
def episodic_memory() -> EpisodicMemory:
    return EpisodicMemory(agent_id="test-agent")


@pytest.fixture
def semantic_memory() -> SemanticMemory:
    return SemanticMemory()


@pytest.fixture
def collective_memory() -> CollectiveMemory:
    return CollectiveMemory()


# ── Governance ───────────────────────────────────────────────────────────────

@pytest.fixture
def constitution() -> ConstitutionalConstraints:
    return ConstitutionalConstraints()


@pytest.fixture
def audit_log(tmp_path) -> AuditLog:
    return AuditLog(db_url=f"sqlite:///{tmp_path}/audit.db")


# ── Research ─────────────────────────────────────────────────────────────────

@pytest.fixture
def pipeline() -> ResearchPipeline:
    return ResearchPipeline(max_hypotheses=2)


# ── Evolution ────────────────────────────────────────────────────────────────

@pytest.fixture
def fork_manager() -> ForkManager:
    return ForkManager()


@pytest.fixture
def evaluator() -> BranchEvaluator:
    return BranchEvaluator()


@pytest.fixture
def merger() -> KnowledgeMerger:
    return KnowledgeMerger()


# ── Observation helpers ──────────────────────────────────────────────────────

@pytest.fixture
def sample_observation() -> dict:
    return {
        "knowledge": {
            "concepts": [
                {"id": "gravity", "attrs": {"type": "force"}},
                {"id": "mass",    "attrs": {"type": "property"}},
            ],
            "relations": [
                {"src": "gravity", "dst": "mass", "kind": "depends_on"}
            ],
        },
        "timeline": {
            "event_id": "evt-001",
            "label": "Gravity discovered",
        },
        "action": {
            "id": "act-001",
            "type": "experiment",
            "context": {"tool": "telescope"},
        },
    }
