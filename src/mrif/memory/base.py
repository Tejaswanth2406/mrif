"""
Abstract base class for all memory layers.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseMemory(ABC):
    """Common interface every memory layer must implement."""

    @abstractmethod
    def push(self, item: Any) -> None:
        """Store one item."""

    @abstractmethod
    def retrieve(self, query: Any) -> list[Any]:
        """Retrieve items matching *query*."""

    @abstractmethod
    def clear(self) -> None:
        """Purge all stored items."""

    @abstractmethod
    def size(self) -> int:
        """Return the number of stored items."""
