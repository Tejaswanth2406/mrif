"""
Long-Term Memory — SQLite-backed persistent key-value + full-text store.

Uses SQLAlchemy 2.0 with the ORM-lite (Core) API for portability.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    Text,
    create_engine,
    select,
    delete,
)
from sqlalchemy.orm import DeclarativeBase, Session

from mrif.config import settings
from mrif.exceptions import MemoryKeyError
from mrif.memory.base import BaseMemory


class _Base(DeclarativeBase):
    pass


class _MemoryRecord(_Base):
    __tablename__ = "long_term_memory"

    id: Any = Column(Integer, primary_key=True, autoincrement=True)
    agent_id: Any = Column(String(128), nullable=False, index=True)
    key: Any = Column(String(256), nullable=False, index=True)
    value: Any = Column(Text, nullable=False)
    tags: Any = Column(String(512), default="")
    created_at: Any = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class LongTermMemory(BaseMemory):
    """
    Persistent memory backed by SQLite via SQLAlchemy.

    Parameters
    ----------
    agent_id : str
        Scopes all reads/writes to a single agent.
    db_url   : str
        SQLAlchemy-compatible database URL.
    """

    def __init__(
        self,
        agent_id: str,
        db_url: str | None = None,
    ) -> None:
        self._agent_id = agent_id
        self._engine = create_engine(db_url or settings.db_url)
        _Base.metadata.create_all(self._engine)

    # ── BaseMemory interface ─────────────────────────────────────────────────

    def push(self, item: Any) -> None:
        """Serialise *item* and store it under an auto-generated key."""
        key = f"auto:{datetime.now(timezone.utc).isoformat()}"
        self.set(key, item)

    def retrieve(self, query: Any = None) -> list[Any]:
        """
        Return all records for this agent.
        If *query* is a string, filter by key or value substring.
        """
        with Session(self._engine) as session:
            stmt = select(_MemoryRecord).where(
                _MemoryRecord.agent_id == self._agent_id
            )
            rows = session.scalars(stmt).all()
        if isinstance(query, str):
            q = query.lower()
            results = [json.loads(r.value) for r in rows
                       if q in r.key.lower() or q in r.value.lower()]
        else:
            results = [json.loads(r.value) for r in rows]
        return results

    def clear(self) -> None:
        with Session(self._engine) as session:
            session.execute(
                delete(_MemoryRecord).where(
                    _MemoryRecord.agent_id == self._agent_id
                )
            )
            session.commit()

    def size(self) -> int:
        with Session(self._engine) as session:
            return session.query(_MemoryRecord).filter(
                _MemoryRecord.agent_id == self._agent_id
            ).count()

    # ── Extended API ─────────────────────────────────────────────────────────

    def set(self, key: str, value: Any, tags: list[str] | None = None) -> None:
        """Store or overwrite *value* under *key*."""
        serialised = json.dumps(value, default=str)
        with Session(self._engine) as session:
            # Upsert pattern
            existing = session.scalars(
                select(_MemoryRecord).where(
                    _MemoryRecord.agent_id == self._agent_id,
                    _MemoryRecord.key == key,
                )
            ).first()
            if existing:
                existing.value = serialised
                existing.tags = ",".join(tags or [])
            else:
                session.add(
                    _MemoryRecord(
                        agent_id=self._agent_id,
                        key=key,
                        value=serialised,
                        tags=",".join(tags or []),
                    )
                )
            session.commit()

    def get(self, key: str) -> Any:
        """Retrieve a value by exact key."""
        with Session(self._engine) as session:
            row = session.scalars(
                select(_MemoryRecord).where(
                    _MemoryRecord.agent_id == self._agent_id,
                    _MemoryRecord.key == key,
                )
            ).first()
        if row is None:
            raise MemoryKeyError(key)
        return json.loads(row.value)

    def delete_key(self, key: str) -> None:
        with Session(self._engine) as session:
            session.execute(
                delete(_MemoryRecord).where(
                    _MemoryRecord.agent_id == self._agent_id,
                    _MemoryRecord.key == key,
                )
            )
            session.commit()

    def keys(self) -> list[str]:
        with Session(self._engine) as session:
            rows = session.scalars(
                select(_MemoryRecord.key).where(
                    _MemoryRecord.agent_id == self._agent_id
                )
            ).all()
        return list(rows)
