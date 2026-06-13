# MRIF Architecture

## Overview

The Meta-Recursive Intelligence Framework (MRIF) models intelligence as a
recursive, multi-dimensional system rather than a single monolithic model.

```
┌─────────────────────────────────────────────────────────────────┐
│                          MetaCore                               │
│                   M = (K, T, R, I, C, E, G)                    │
│                   M_{t+1} = F(M_t, O_t)                        │
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │    K     │  │    T     │  │    R     │  │    I     │       │
│  │Knowledge │  │Timeline  │  │ Reality  │  │Identity  │       │
│  │  Graph   │  │ Engine   │  │ Engine   │  │Registry  │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────────┐     │
│  │    C     │  │    E     │  │           G              │     │
│  │ Causality│  │Evolution │  │       Governance         │     │
│  │  Graph   │  │ Tracker  │  │  Constitution + Audit    │     │
│  └──────────┘  └──────────┘  └──────────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

---

## Dimension Details

### K — KnowledgeGraph
- **Backend**: NetworkX `DiGraph`
- **Nodes**: Concepts with attribute dicts
- **Edges**: Typed directed relations (`depends_on`, `causes`, `related`, …)
- **Key ops**: `add_concept`, `add_relation`, `find_path`, `merge`, `export_snapshot`

### T — TimelineEngine
- **Model**: Rooted tree of `TimelineNode` objects
- **Supports**: Branching futures, path tracing, DFS over all possible futures
- **Key ops**: `record_event`, `branch`, `get_path`, `get_all_futures`

### R — RealityEngine
- **Model**: Dict of `RealityModel` instances, each parameterised by assumptions
- **Evolutionary ops**: `fork` (copy), `mutate` (genetic crossover `C = Mutate(A, B)`)
- **Key ops**: `create`, `fork`, `mutate`, `compare`, `rank_by_fitness`

### I — IdentityRegistry
- **Model**: `AgentIdentity` Pydantic models keyed by agent ID
- **Lineage**: Append-only parent chains (like Git history)
- **Key ops**: `register_clone`, `retire_clone`, `has_permission`

### C — CausalGraph
- **Backend**: NetworkX `DiGraph` (DAG enforced)
- **Nodes**: Actions/events with timestamps and context
- **Edges**: `caused` relationships
- **Key ops**: `record_action`, `trace_causes`, `trace_consequences`, `find_root_causes`

### E — EvolutionTracker
- **Fitness**: `Φ = α·ΔK + β·ΔR + γ·safety_score`
- **History**: `GenerationSnapshot` list per generation
- **Key ops**: `evaluate`, `fitness_trend`, `is_improving`, `peak_fitness`

### G — Governance
- **ConstitutionalConstraints**: four immutable runtime rules checked on every payload
- **AuditLog**: append-only SQLite table, never deleted in normal operation

---

## Memory Stack

```
WorkingMemory        ← bounded deque, fastest, in-process
     ↓
LongTermMemory       ← SQLite via SQLAlchemy, persistent key-value
     ↓
EpisodicMemory       ← ordered event sequences per agent
     ↓
SemanticMemory       ← concept → attribute dict
     ↓
CollectiveMemory     ← shared namespace across all clones
```

---

## Update Cycle

```
Observations (O_t)
      │
      ▼
ConstitutionalConstraints.validate()
      │ (violation → raise, halt)
      ▼
UpdateEngine._apply_single() per observation
   ├─ K: add concepts / relations
   ├─ T: record timeline events
   ├─ C: record causal actions
   ├─ R: update reality fitness
   └─ WorkingMemory.push()
      │
      ▼
UpdateEngine._sync_counters()
      │
      ▼
CoreState.increment_generation()
      │
      ▼
EvolutionTracker.evaluate()
      │
      ▼
AuditLog.record("generation_advance")
```

---

## Clone Lifecycle

```
MetaCore.spawn_clone(goal, permissions)
      │
      ├─ IdentityRegistry.register_clone()  → clone_id
      ├─ KnowledgeGraph.export_snapshot()   → initial knowledge
      └─ CollectiveMemory.store(clone_id, "initial_knowledge", snapshot)

          [clone runs independently, discovers knowledge]

MetaCore.absorb_clone(clone_id, learnings)
      │
      ├─ MetaCore.observe(learnings)          → merge knowledge into K
      └─ IdentityRegistry.retire_clone()      → status = "retired"
```

---

## Research Pipeline

```
Question text
      │
HypothesisGenerator.generate(n)
      │
ExperimentPlanner.plan(hypothesis)
      │
_mock_simulate(experiment)        ← replace with domain model
      │
_stage_verify()
   ├─ p_value < 0.05 → CONFIRMED, confidence += 0.3
   └─ p_value ≥ 0.05 → REJECTED,  confidence -= 0.3
      │
PipelineRun.findings
```

---

## Dependency Map

```
mrif.core.meta_core
  ├── mrif.core.state
  ├── mrif.core.update_engine
  ├── mrif.dimensions.*
  ├── mrif.governance.*
  ├── mrif.memory.*
  └── mrif.config

mrif.dimensions.*           ← pure logic, no DB
mrif.governance.audit       ← SQLAlchemy + SQLite
mrif.memory.long_term       ← SQLAlchemy + SQLite
mrif.research.pipeline      ← depends on hypothesis + experiment
mrif.evolution.*            ← pure logic
mrif.cli                    ← depends on meta_core + pipeline
```
