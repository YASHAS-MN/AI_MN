# Architecture — Artificial Mind Foundation (V0)

## Overview

V0 establishes the smallest possible persistent artificial entity: an identity, internal state, memory, and a minimal cognitive interface. It uses no external dependencies — only the Python standard library.

## Design Principles

1. **Independence from specific technologies.** The entity's conceptual model (identity, state, memory, cognition) is defined by data structures and interfaces, not by any particular database, AI model, or framework.
2. **Human inspectability.** All persistent data is stored as formatted JSON files that can be read and edited with any text editor.
3. **Portability.** The entire entity is self-contained in a code directory and a data directory. Copy both to any machine with Python 3.10+ and the entity is fully operational.
4. **Minimal surface area.** No feature is included unless it is required by the V0 completion criteria.

## Module Responsibilities

| Module | Responsibility | Depends on |
|---|---|---|
| `mind/storage.py` | Read/write JSON files atomically | Python stdlib only |
| `mind/identity.py` | Persistent identity (create once, load forever) | `storage` |
| `mind/state.py` | Mutable internal state (current state, uncertainties, questions) | `storage` |
| `mind/memory.py` | Append-only experience store | `storage` |
| `mind/cognition.py` | Input→output processing (stub in V0) | `identity`, `state`, `memory` |
| `main.py` | CLI entry point | All of the above |

## Data Directory Layout

```
mind_data/
├── identity.json     # Created once; never overwritten unless version bumps
├── state.json        # Overwritten on every state mutation
└── memories.json     # Overwritten on every new experience (append to list)
```

All files are human-readable JSON with 2-space indentation.

## Data Schemas

### identity.json

```json
{
  "id": "uuid4-string",
  "name": "Mind",
  "created_at": "ISO-8601-timestamp",
  "version": "0.1.0"
}
```

### state.json

```json
{
  "current_state": "initialized",
  "uncertainties": [],
  "open_questions": [],
  "last_updated": "ISO-8601-timestamp"
}
```

### memories.json

```json
{
  "experiences": [
    {
      "id": "uuid4-string",
      "content": "text",
      "timestamp": "ISO-8601-timestamp",
      "importance": 0.5,
      "source": "input"
    }
  ]
}
```

## How to Replace Components

### Replacing Storage

1. Create a new module (e.g., `mind/storage_sqlite.py`) that exports the same interface: `ensure_dir()`, `load()`, `save()`.
2. Update imports in `identity.py`, `state.py`, and `memory.py` to point to the new module.
3. Write a one-time migration script to move data from JSON to the new backend.

### Replacing Cognition

1. Replace the body of `cognition.process()`.
2. The function signature remains: `process(input_text, identity, state, memory) → str`.
3. Future cognition engines (LLM, rule engine, etc.) receive the same four arguments and return a string.

### Adding New State Fields

1. Add the field to the `InternalState` dataclass with a default value.
2. Handle missing keys in `from_dict()` with `.get()` (already done for all existing fields).
3. Existing `state.json` files remain backward-compatible.

### Adding New Memory Fields

1. Add the field to the `Experience` dataclass.
2. Handle missing keys in `from_dict()`.
3. Existing experiences in `memories.json` remain loadable.

## Dependencies

**None.** V0 uses only:

- `json` — serialization
- `uuid` — unique identifiers
- `datetime` — timestamps
- `dataclasses` — data structures
- `pathlib` — file paths
- `os`, `tempfile` — atomic file writes
- `sys` — CLI argument handling

All are part of the Python standard library (3.10+).

## Migration Path

When V0 needs to evolve:

1. **V1 — Richer cognition**: Replace `cognition.py` with an LLM-backed or rule-based reasoner. The interface does not change.
2. **V1 — Better storage**: Replace `storage.py` with SQLite or another backend. Migrate JSON → new format with a script.
3. **V1 — Memory indexing**: Add search capabilities to `MemoryStore` (semantic search, filtering by importance/source). The `Experience` schema does not change.
4. **V1 — Network interface**: Replace `main.py` with an HTTP server, WebSocket endpoint, or message queue consumer. The `cognition.process()` function is called the same way.

The conceptual model — identity, state, memory, cognition — remains stable across all of these changes.
