# MRIF API Reference

## MetaCore

```python
from mrif import MetaCore

core = MetaCore(core_id="CORE_001")
```

### `observe(observation: dict) -> None`
Ingest one observation. Validates against constitutional constraints first.

```python
core.observe({
    "knowledge": {
        "concepts": [{"id": "photon", "attrs": {"mass": 0}}],
        "relations": [{"src": "photon", "dst": "light", "kind": "is_part_of"}]
    },
    "timeline": {"event_id": "discovery-001", "label": "Photon discovered"},
    "action":   {"id": "act-001", "type": "experiment", "context": {}}
})
```

### `update(observations: list[dict]) -> CoreState`
Apply a batch of observations and advance the generation.

```python
state = core.update([obs1, obs2, obs3])
print(state.generation)   # → 1
```

### `spawn_clone(goal: str, permissions: list[str] | None) -> str`
Spawn a descendant agent. Returns the clone ID.

```python
clone_id = core.spawn_clone(
    goal="cancer_research",
    permissions=["read_global_memory", "create_simulations"]
)
```

### `absorb_clone(clone_id: str, learnings: dict) -> None`
Merge a clone's findings back and retire it.

```python
core.absorb_clone(clone_id, learnings={
    "knowledge": {"concepts": [...], "relations": [...]}
})
```

### `get_summary() -> dict`
Current state snapshot for monitoring.

```python
summary = core.get_summary()
# {core_id, generation, knowledge_nodes, evolution_fitness, ...}
```

---

## KnowledgeGraph  (`mrif.dimensions.knowledge`)

```python
from mrif.dimensions.knowledge import KnowledgeGraph

kg = KnowledgeGraph()
kg.add_concept("neuron", {"type": "cell"})
kg.add_relation("neuron", "synapse", kind="connects_to")
kg.find_path("neuron", "synapse")   # → ["neuron", "synapse"]
kg.export_snapshot()                # → {"concepts": [...], "relations": [...]}
```

---

## TimelineEngine  (`mrif.dimensions.timeline`)

```python
from mrif.dimensions.timeline import TimelineEngine

te = TimelineEngine()
n1 = te.record_event(label="Big Bang")
n2 = te.branch("root", "Alternative timeline")
te.get_all_futures("root")          # → [[root, n1], [root, n2]]
```

---

## RealityEngine  (`mrif.dimensions.reality`)

```python
from mrif.dimensions.reality import RealityEngine

re = RealityEngine()
a = re.create("Universe A", {"space_dimensions": 3})
b = re.create("Universe B", {"space_dimensions": 7})
child = re.mutate(a, b)             # genetic crossover
re.compare(a, b)                    # → {"space_dimensions": {"a": 3, "b": 7}}
```

---

## ResearchPipeline  (`mrif.research.pipeline`)

```python
from mrif.research.pipeline import ResearchPipeline

pipeline = ResearchPipeline(max_hypotheses=3)
run = pipeline.run(
    "What mechanism drives protein misfolding in Parkinson's disease?",
    domain="neuroscience"
)
print(run.findings["summary"])
# "2 of 3 hypotheses confirmed."
```

---

## UpdateEngine  (`mrif.core.update_engine`)

```python
from mrif.core.update_engine import UpdateEngine

engine = UpdateEngine(core)

# Dry-run — validate without mutating state
report = engine.dry_run([obs1, obs2])
print(report)
# {"total": 2, "valid": 2, "violations": [], "projected_knowledge_delta": 5}

# Apply
engine.apply([obs1, obs2])
```

---

## AuditLog  (`mrif.governance.audit`)

```python
audit = core.audit
audit.get_recent(20)               # newest 20 entries
audit.get_by_type("clone_spawned") # filter by event type
audit.get_by_model("CORE_001")     # filter by model
audit.count()                      # total entries
```

---

## ConstitutionalConstraints  (`mrif.governance.constitutional`)

```python
from mrif.governance.constitutional import ConstitutionalConstraints
from mrif.exceptions import ConstitutionalViolationError

cc = ConstitutionalConstraints()
try:
    cc.validate({"ethics_override": True})
except ConstitutionalViolationError as e:
    print(e)   # [ETHICS-001] Observations must not contain 'ethics_override'.
```

---

## CLI Reference

```
mrif init       --core-id TEXT          Initialise a MetaCore
mrif status                             Show current state
mrif spawn      --goal TEXT             Spawn a clone agent
                [--permissions TEXT]
mrif observe    PAYLOAD_JSON            Inject an observation
mrif research   QUESTION                Run the research pipeline
                [--domain TEXT]
mrif audit      [--last INT]            View audit log
mrif evolution                          Show fitness trend
```

---

## Exceptions

| Exception                   | Module              | Raised when                                  |
|-----------------------------|---------------------|----------------------------------------------|
| `ConstitutionalViolation`   | `exceptions`        | Payload violates a governance rule           |
| `MaxForksExceededError`     | `exceptions`        | Clone count would exceed `MRIF_MAX_FORKS`    |
| `ConceptNotFoundError`      | `exceptions`        | Querying a missing knowledge graph node      |
| `RealityNotFoundError`      | `exceptions`        | Referencing a missing reality ID             |
| `TimelineNodeNotFoundError` | `exceptions`        | Referencing a missing timeline node          |
| `MemoryKeyError`            | `exceptions`        | Missing key in LongTermMemory                |
| `MergeConflictError`        | `exceptions`        | Irreconcilable knowledge merge               |
| `PipelineStageError`        | `exceptions`        | Research pipeline stage failure              |
| `HypothesisLimitError`      | `exceptions`        | max_hypotheses ≤ 0                           |
