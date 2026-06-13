"""
Collective Memory — shared knowledge accessible by all authorised agents.

Every clone can read from and write to this store.
The MetaCore absorbs clone learnings here before they are retired.
"""
from __future__ import annotations

import json
from typing import Any

from mrif.memory.base import BaseMemory


class CollectiveMemory(BaseMemory):
    """
    Simple namespace-keyed in-process store.

    Keys are namespaced as:  "{agent_id}:{key}"
    This allows per-agent isolation while sharing a single backing store.
    """

    def __init__(self) -> None:
        self._store: dict[str, Any] = {}

    # ── BaseMemory ──────────────────────────────────────────────────────────

    def push(self, item: Any) -> None:
        if isinstance(item, dict):
            agent_id = item.get("agent_id", "global")
            key = item.get("key", "auto")
            self.store(agent_id, key, item.get("value", item))

    def retrieve(self, query: Any = None) -> list[Any]:
        values = list(self._store.values())
        if isinstance(query, str):
            q = query.lower()
            values = [v for v in values if q in json.dumps(v, default=str).lower()]
        return values

    def clear(self) -> None:
        self._store.clear()

    def size(self) -> int:
        return len(self._store)

    # ── Extended API ─────────────────────────────────────────────────────────

    def store(self, agent_id: str, key: str, value: Any) -> None:
        self._store[f"{agent_id}:{key}"] = value

    def fetch(self, agent_id: str, key: str) -> Any | None:
        return self._store.get(f"{agent_id}:{key}")

    def fetch_all(self, agent_id: str) -> dict[str, Any]:
        prefix = f"{agent_id}:"
        return {
            k[len(prefix):]: v
            for k, v in self._store.items()
            if k.startswith(prefix)
        }

    def delete(self, agent_id: str, key: str) -> None:
        self._store.pop(f"{agent_id}:{key}", None)

    def list_keys(self, agent_id: str) -> list[str]:
        prefix = f"{agent_id}:"
        return [k[len(prefix):] for k in self._store if k.startswith(prefix)]
