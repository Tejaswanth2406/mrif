"""
Working Memory — fast, bounded, in-process deque.

Analogous to CPU L1/L2 cache: highest speed, smallest capacity.
Oldest items are evicted when the limit is reached (LRU).
"""
from __future__ import annotations

from collections import deque
from typing import Any

from mrif.memory.base import BaseMemory


class WorkingMemory(BaseMemory):
    """
    Bounded FIFO / LRU working memory backed by a collections.deque.

    Parameters
    ----------
    limit : int
        Maximum number of items stored simultaneously.
    """

    def __init__(self, limit: int = 1000) -> None:
        self._limit = limit
        self._store: deque[Any] = deque(maxlen=limit)

    def push(self, item: Any) -> None:
        """Append an item; oldest is auto-evicted if at capacity."""
        self._store.append(item)

    def peek(self) -> Any | None:
        """Return the most recently pushed item without removing it."""
        return self._store[-1] if self._store else None

    def pop(self) -> Any | None:
        """Remove and return the most recently pushed item."""
        return self._store.pop() if self._store else None

    def retrieve(self, query: Any = None) -> list[Any]:
        """
        Return all items (newest-first).
        If *query* is a string, filter items that contain it as a substring
        when converted to str.
        """
        items = list(reversed(self._store))
        if isinstance(query, str):
            q = query.lower()
            items = [i for i in items if q in str(i).lower()]
        return items

    def clear(self) -> None:
        self._store.clear()

    def size(self) -> int:
        return len(self._store)

    def is_full(self) -> bool:
        return len(self._store) >= self._limit

    @property
    def limit(self) -> int:
        return self._limit
