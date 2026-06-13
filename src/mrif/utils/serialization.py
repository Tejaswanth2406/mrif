"""
Serialisation helpers — fast JSON via orjson + YAML support.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

import orjson
import yaml


def to_json(obj: Any, pretty: bool = False) -> str:
    """Serialise *obj* to a JSON string using orjson."""
    opts = orjson.OPT_INDENT_2 if pretty else None
    return orjson.dumps(obj, option=opts, default=_json_default).decode("utf-8")


def from_json(data: str | bytes) -> Any:
    """Deserialise a JSON string/bytes."""
    return orjson.loads(data)


def to_yaml(obj: Any) -> str:
    """Serialise *obj* to a YAML string."""
    return yaml.dump(obj, default_flow_style=False, allow_unicode=True)


def from_yaml(data: str) -> Any:
    """Deserialise a YAML string."""
    return yaml.safe_load(data)


def _json_default(obj: Any) -> Any:
    """Custom encoder for types not handled by orjson."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    if hasattr(obj, "model_dump"):    # Pydantic v2
        return obj.model_dump()
    if hasattr(obj, "__dict__"):
        return obj.__dict__
    raise TypeError(f"Object of type {type(obj)} is not JSON serialisable")
