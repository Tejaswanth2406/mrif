<img width="1983" height="793" alt="image" src="https://github.com/user-attachments/assets/4828fac1-13e0-4df8-a62e-48832932d6d1" />
# Meta-Recursive Intelligence Framework (MRIF)

> *A production-grade implementation of recursive meta-intelligence architecture.*

MRIF is a modular, extensible Python framework that models a **Meta-Core** — an orchestrating intelligence that manages knowledge, timelines, realities, identities, causality, evolution, and governance across a hierarchy of descendant agents.

---

## Architecture

The MetaCore state is formally defined as:

```
M = (K, T, R, I, C, E, G)
```

| Symbol | Dimension     | Module                        |
|--------|---------------|-------------------------------|
| K      | Knowledge     | `mrif.dimensions.knowledge`   |
| T      | Timelines     | `mrif.dimensions.timeline`    |
| R      | Realities     | `mrif.dimensions.reality`     |
| I      | Identities    | `mrif.dimensions.identity`    |
| C      | Causality     | `mrif.dimensions.causality`   |
| E      | Evolution     | `mrif.dimensions.evolution`   |
| G      | Governance    | `mrif.governance`             |

**Update rule:** `M_{t+1} = F(M_t, O_t)`  
where `O_t` is the set of observations from all descendants at time `t`.

---

## Project Structure

```
mrif/
├── src/
│   └── mrif/
│       ├── core/           # MetaCore orchestrator & state
│       ├── dimensions/     # K, T, R, I, C, E layers
│       ├── memory/         # Working → Civilizational memory stack
│       ├── governance/     # Constitutional constraints & audit log
│       ├── research/       # Autonomous research pipeline
│       ├── evolution/      # Fork / Evaluate / Merge engine
│       └── utils/          # Logging, serialization
├── tests/                  # Full pytest suite
├── pyproject.toml
├── Makefile
└── .env.example
```

---

## Quick Start

```bash
# Install
pip install -e ".[dev]"

# Copy and edit environment config
cp .env.example .env

# Initialize a MetaCore and show its status
mrif init --core-id CORE_001
mrif status

# Spawn a descendant agent
mrif spawn --goal "cancer_research" --permissions read_global_memory

# Run the research pipeline
mrif research --question "What is the optimal protein folding pathway?"

# View audit log
mrif audit --last 20
```

---

## Memory Architecture

```
WorkingMemory      (fast, bounded, in-process deque)
    ↓
LongTermMemory     (SQLite via SQLAlchemy — persistent)
    ↓
EpisodicMemory     (ordered event sequences per agent)
    ↓
SemanticMemory     (concept → concept relationship graph)
    ↓
CollectiveMemory   (shared across all clones / descendants)
```

---

## Governance

Every action is validated against **Constitutional Constraints** — an immutable rule set enforced at runtime:

- Cannot modify core ethics layer
- Cannot self-replicate without explicit authorization
- Cannot overwrite lineage history
- Cannot suppress audit trail

Every decision is recorded to an append-only **AuditLog** with full reasoning traces.

---

## Development

```bash
make install        # install with dev extras
make test           # run full test suite
make lint           # ruff + mypy
make format         # black
make clean          # remove build artifacts
```

---

## Mathematical Abstraction

```
MetaCore update:    M_{t+1} = F(M_t, O_t)
Evolution fitness:  Φ = α·ΔK + β·ΔR + γ·safety_score
Reality mutation:   C = Mutate(A, B)   (genetic crossover of realities)
```

---

## License

MIT
