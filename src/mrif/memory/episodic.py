"""
Episodic Memory — ordered sequences of events (episodes) per agent.

Analogous to autobiographical memory: "I did X, then Y happened."
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from mrif.memory.base import BaseMemory


@dataclass
class Episode:
    episode_id: str
    agent_id: str
    event_type: str
    data: dict[str, Any]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class EpisodicMemory(BaseMemory):
    """Ordered log of episodes for an agent."""

    def __init__(self, agent_id: str) -> None:
        self._agent_id = agent_id
        self._episodes: list[Episode] = []
        self._counter = 0

    def push(self, item: Any) -> None:
        """Store a raw item as an episode."""
        self.record(event_type="raw", data={"value": item})

    def record(self, event_type: str, data: dict[str, Any]) -> str:
        self._counter += 1
        ep = Episode(
            episode_id=f"ep-{self._counter:06d}",
            agent_id=self._agent_id,
            event_type=event_type,
            data=data,
        )
        self._episodes.append(ep)
        return ep.episode_id

    def retrieve(self, query: Any = None) -> list[Any]:
        eps = self._episodes
        if isinstance(query, str):
            eps = [e for e in eps if query in e.event_type or query in str(e.data)]
        return [{"episode_id": e.episode_id, "type": e.event_type,
                 "data": e.data, "timestamp": e.timestamp.isoformat()} for e in eps]

    def get_recent(self, n: int = 10) -> list[Episode]:
        return self._episodes[-n:]

    def clear(self) -> None:
        self._episodes.clear()

    def size(self) -> int:
        return len(self._episodes)
