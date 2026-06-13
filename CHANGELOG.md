# Changelog

All notable changes to MRIF are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### Planned
- LLM-backed HypothesisGenerator (replace template stubs)
- REST API layer via FastAPI
- Distributed CollectiveMemory via Redis
- Vector-store SemanticMemory via ChromaDB
- Formal verification proofs for constitutional constraints
- Async update engine with asyncio

---

## [0.1.0] — 2025-06-13

### Added
- **MetaCore** — central orchestrator implementing `M = (K, T, R, I, C, E, G)`
- **Dimension K** — `KnowledgeGraph` backed by NetworkX DiGraph
- **Dimension T** — `TimelineEngine` with branching future trees
- **Dimension R** — `RealityEngine` with fork/mutate (evolutionary crossover)
- **Dimension I** — `IdentityRegistry` — Git-like lineage tracking for clones
- **Dimension C** — `CausalGraph` — DAG of action → consequence chains
- **Dimension E** — `EvolutionTracker` — fitness function `Φ = α·ΔK + β·ΔR + γ·safety`
- **Memory stack** — Working → LongTerm (SQLite) → Episodic → Semantic → Collective
- **Constitutional constraints** — immutable runtime governance rules
- **AuditLog** — append-only, SQLite-backed event trail
- **Lineage helpers** — tree building, depth, common ancestor
- **ResearchPipeline** — Question → Hypothesis → Experiment → Simulate → Verify
- **UpdateEngine** — isolated `F(M, O)` transition function with dry-run support
- **ForkManager** — evolutionary branch lifecycle management
- **BranchEvaluator** — weighted fitness scoring for forks
- **KnowledgeMerger** — union-based conflict-resolved knowledge merging
- **CLI** — Typer-based: `init`, `status`, `spawn`, `observe`, `research`, `audit`, `evolution`
- **Dockerfile** — two-stage build (builder + slim runtime)
- **docker-compose.yml** — core + dev service definitions
- Full pytest suite — 100 + test cases across all modules

### Architecture
- `src/` layout with PEP 517 build via setuptools
- Pydantic v2 for all validated models
- SQLAlchemy 2.0 (ORM Core) for persistent storage
- Loguru for structured JSON logging
- Orjson for fast serialisation
- Ruff + Black + Mypy for code quality
