"""
Merger — merges knowledge from winning forks back into the MetaCore.
"""
from __future__ import annotations

from typing import Any

from mrif.exceptions import MergeConflictError


class KnowledgeMerger:
    """
    Merges two knowledge snapshots (dicts) into one.

    Conflict strategy:
        - Concepts: union (no concept is lost)
        - Relations: union (directed; duplicates collapsed)
        - Attribute conflicts: prefer *winner* values
    """

    def merge(
        self,
        base: dict[str, Any],
        incoming: dict[str, Any],
        conflict_strategy: str = "prefer_incoming",
    ) -> dict[str, Any]:
        """
        Merge *incoming* snapshot into *base*.

        Parameters
        ----------
        base             : The current MetaCore knowledge snapshot.
        incoming         : The fork's knowledge snapshot.
        conflict_strategy: 'prefer_incoming' | 'prefer_base'

        Returns the merged snapshot.
        """
        merged_concepts = self._merge_concepts(
            base.get("concepts", []),
            incoming.get("concepts", []),
            conflict_strategy,
        )
        merged_relations = self._merge_relations(
            base.get("relations", []),
            incoming.get("relations", []),
        )
        return {"concepts": merged_concepts, "relations": merged_relations}

    def _merge_concepts(
        self,
        base: list[dict[str, Any]],
        incoming: list[dict[str, Any]],
        strategy: str,
    ) -> list[dict[str, Any]]:
        by_id: dict[str, dict[str, Any]] = {}
        for c in base:
            by_id[c["id"]] = dict(c)
        for c in incoming:
            cid = c["id"]
            if cid in by_id:
                if strategy == "prefer_incoming":
                    by_id[cid]["attrs"] = {**by_id[cid].get("attrs", {}),
                                           **c.get("attrs", {})}
                # else: keep base — do nothing
            else:
                by_id[cid] = dict(c)
        return list(by_id.values())

    @staticmethod
    def _merge_relations(
        base: list[dict[str, Any]],
        incoming: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        seen: set[tuple[str, str, str]] = set()
        result: list[dict[str, Any]] = []
        for r in (*base, *incoming):
            key = (r["src"], r["dst"], r.get("kind", "related"))
            if key not in seen:
                seen.add(key)
                result.append(r)
        return result

    def can_merge(self, base: dict[str, Any], incoming: dict[str, Any]) -> bool:
        """Returns True if a merge is possible without irreconcilable conflicts."""
        _ = base, incoming
        # Placeholder: always mergeable in this implementation
        return True
