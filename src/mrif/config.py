"""
MRIF Configuration — environment-driven settings via Pydantic.
"""
from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class MRIFSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="MRIF_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── Core ────────────────────────────────────────────────────────────────
    core_id: str = Field(default="CORE_001", description="Unique identifier for this MetaCore")
    log_level: str = Field(default="INFO", description="Logging level")

    # ── Persistence ─────────────────────────────────────────────────────────
    db_url: str = Field(default="sqlite:///mrif.db", description="SQLAlchemy database URL")

    # ── Memory ──────────────────────────────────────────────────────────────
    working_memory_limit: int = Field(default=1000, description="Max items in working memory")

    # ── Evolution ───────────────────────────────────────────────────────────
    max_forks: int = Field(default=10, description="Maximum concurrent descendant agents")
    evolution_threshold: float = Field(default=0.8, description="Fitness threshold for promotion")

    # ── Research ────────────────────────────────────────────────────────────
    max_hypotheses: int = Field(default=100, description="Max hypotheses per research cycle")
    simulation_timeout: int = Field(default=300, description="Simulation timeout in seconds")

    # ── Safety ──────────────────────────────────────────────────────────────
    audit_enabled: bool = Field(default=True, description="Enable append-only audit trail")
    reproducibility_mode: bool = Field(default=False, description="Deterministic mode")

    # ── Reality Engine ──────────────────────────────────────────────────────
    max_realities: int = Field(default=50, description="Max concurrent reality models")

    # ── Timeline Engine ─────────────────────────────────────────────────────
    max_timeline_depth: int = Field(default=20, description="Max branching depth")


settings = MRIFSettings()
