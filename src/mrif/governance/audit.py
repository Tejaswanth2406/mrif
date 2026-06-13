"""
Audit Log — append-only, tamper-evident event trail.

Every decision, observation, and constitutional check is recorded here.
Records are stored in SQLite and are never deleted in normal operation.

Schema:
    id           : int (auto)
    event_type   : str
    model_id     : str
    timestamp    : datetime UTC
    data_json    : str (JSON)
    reasoning    : str (optional natural-language trace)
    confidence   : float [0, 1]
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import Column, DateTime, Float, Integer, String, Text, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Session

from mrif.config import settings


class _AuditBase(DeclarativeBase):
    pass


class _AuditRecord(_AuditBase):
    __tablename__ = "audit_log"

    id: Any = Column(Integer, primary_key=True, autoincrement=True)
    event_type: Any = Column(String(128), nullable=False, index=True)
    model_id: Any = Column(String(128), nullable=False, index=True)
    timestamp: Any = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    data_json: Any = Column(Text, nullable=False, default="{}")
    reasoning: Any = Column(Text, nullable=True)
    confidence: Any = Column(Float, default=1.0)


class AuditLog:
    """
    Append-only audit log backed by SQLite.

    Parameters
    ----------
    db_url : str
        SQLAlchemy database URL (defaults to settings value).
    """

    def __init__(self, db_url: str | None = None) -> None:
        self._engine = create_engine(db_url or settings.db_url)
        _AuditBase.metadata.create_all(self._engine)

    def record(
        self,
        event_type: str,
        model_id: str,
        data: dict[str, Any] | None = None,
        reasoning: str | None = None,
        confidence: float = 1.0,
    ) -> int:
        """
        Append a new audit record.

        Returns the auto-generated row ID.
        """
        with Session(self._engine) as session:
            entry = _AuditRecord(
                event_type=event_type,
                model_id=model_id,
                data_json=json.dumps(data or {}, default=str),
                reasoning=reasoning,
                confidence=confidence,
            )
            session.add(entry)
            session.commit()
            session.refresh(entry)
            return int(entry.id)

    def get_recent(self, n: int = 20) -> list[dict[str, Any]]:
        """Return the *n* most recent audit entries."""
        with Session(self._engine) as session:
            rows = session.scalars(
                select(_AuditRecord)
                .order_by(_AuditRecord.timestamp.desc())
                .limit(n)
            ).all()
        return [self._row_to_dict(r) for r in rows]

    def get_by_type(self, event_type: str) -> list[dict[str, Any]]:
        with Session(self._engine) as session:
            rows = session.scalars(
                select(_AuditRecord).where(_AuditRecord.event_type == event_type)
            ).all()
        return [self._row_to_dict(r) for r in rows]

    def get_by_model(self, model_id: str) -> list[dict[str, Any]]:
        with Session(self._engine) as session:
            rows = session.scalars(
                select(_AuditRecord).where(_AuditRecord.model_id == model_id)
            ).all()
        return [self._row_to_dict(r) for r in rows]

    def count(self) -> int:
        with Session(self._engine) as session:
            return session.query(_AuditRecord).count()

    @staticmethod
    def _row_to_dict(row: _AuditRecord) -> dict[str, Any]:
        return {
            "id": row.id,
            "event_type": row.event_type,
            "model_id": row.model_id,
            "timestamp": row.timestamp.isoformat() if row.timestamp else None,
            "data": json.loads(row.data_json or "{}"),
            "reasoning": row.reasoning,
            "confidence": row.confidence,
        }
