"""
MRIF custom exception hierarchy.
All framework exceptions derive from MRIFError for easy catching.
"""


class MRIFError(Exception):
    """Base exception for all MRIF errors."""


# ── Constitutional / Governance ─────────────────────────────────────────────

class ConstitutionalViolationError(MRIFError):
    """Raised when an action violates an immutable constitutional constraint."""


class AuditWriteError(MRIFError):
    """Raised when the audit log cannot be written (e.g. tampering detected)."""


class LineageIntegrityError(MRIFError):
    """Raised when a lineage record is invalid or corrupted."""


# ── Evolution / Forking ─────────────────────────────────────────────────────

class MaxForksExceededError(MRIFError):
    """Raised when spawning a clone would exceed the configured fork limit."""


class MergeConflictError(MRIFError):
    """Raised when two knowledge graphs cannot be merged without conflicts."""


# ── Knowledge / Dimensions ──────────────────────────────────────────────────

class ConceptNotFoundError(MRIFError):
    """Raised when a queried concept does not exist in the knowledge graph."""


class RealityNotFoundError(MRIFError):
    """Raised when a referenced reality ID does not exist."""


class TimelineNodeNotFoundError(MRIFError):
    """Raised when a referenced timeline node does not exist."""


# ── Memory ──────────────────────────────────────────────────────────────────

class MemoryCapacityError(MRIFError):
    """Raised when working memory is full and cannot accept new items."""


class MemoryKeyError(MRIFError):
    """Raised when a key is not found in long-term memory."""


# ── Research ────────────────────────────────────────────────────────────────

class PipelineStageError(MRIFError):
    """Raised when a research pipeline stage fails."""


class HypothesisLimitError(MRIFError):
    """Raised when the maximum number of hypotheses is exceeded."""
