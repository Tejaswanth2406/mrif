"""
Semantic Memory — concept-to-concept relational knowledge store.

Distinct from the Knowledge Graph (which is the MetaCore's world model),
Semantic Memory stores the *meaning* of concepts relative to an agent.
"""
from __future__ import annotations

from typing import Any

from mrif.memory.base import BaseMemory


class SemanticMemory(BaseMemory):
    """
    Dict-of-dicts semantic store.

    concept_id → { attribute_key: value, ... }
    """

    def __init__(self) -> None:
        self._store: dict[str, dict[str, Any]] = {}

    def push(self, item: Any) -> None:
        if isinstance(item, dict) and "concept_id" in item:
            self.learn(item["concept_id"], item.get("attrs", {}))

    def learn(self, concept_id: str, attrs: dict[str, Any]) -> None:
        """Store or merge attributes for a concept."""
        self._store.setdefault(concept_id, {}).update(attrs)

    def recall(self, concept_id: str) -> dict[str, Any]:
        return dict(self._store.get(concept_id, {}))

    def retrieve(self, query: Any = None) -> list[Any]:
        if isinstance(query, str):
            return [
                {"concept_id": cid, "attrs": attrs}
                for cid, attrs in self._store.items()
                if query.lower() in cid.lower()
                or query.lower() in str(attrs).lower()
            ]
        return [
            {"concept_id": cid, "attrs": attrs}
            for cid, attrs in self._store.items()
        ]

    def forget(self, concept_id: str) -> None:
        self._store.pop(concept_id, None)

    def clear(self) -> None:
        self._store.clear()

    def size(self) -> int:
        return len(self._store)
