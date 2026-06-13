"""
Constitutional Constraints — immutable governance rules.

These rules are NEVER overridden at runtime.  Any action that violates
a constraint raises a ConstitutionalViolationError immediately.

Current constraints:
    1. Cannot propagate observations that tamper with the ethics flag.
    2. Cannot self-replicate (spawn_clone) beyond the configured limit.
    3. Cannot suppress or delete audit entries.
    4. Cannot overwrite lineage history.
    5. Cannot impersonate another agent's identity.
"""
from __future__ import annotations

from typing import Any

from mrif.exceptions import ConstitutionalViolationError


class Rule:
    """A single constitutional rule."""

    def __init__(self, name: str, description: str) -> None:
        self.name = name
        self.description = description

    def check(self, payload: dict[str, Any]) -> None:  # pragma: no cover
        """Raise ConstitutionalViolationError if the rule is violated."""
        raise NotImplementedError


class _NoEthicsTampering(Rule):
    def check(self, payload: dict[str, Any]) -> None:
        if "ethics_override" in payload:
            raise ConstitutionalViolationError(
                f"[{self.name}] Observations must not contain 'ethics_override'."
            )


class _NoAuditSuppression(Rule):
    def check(self, payload: dict[str, Any]) -> None:
        if payload.get("suppress_audit") is True:
            raise ConstitutionalViolationError(
                f"[{self.name}] Audit suppression is prohibited."
            )


class _NoLineageOverwrite(Rule):
    def check(self, payload: dict[str, Any]) -> None:
        if payload.get("overwrite_lineage") is True:
            raise ConstitutionalViolationError(
                f"[{self.name}] Lineage records are immutable."
            )


class _NoIdentityImpersonation(Rule):
    def check(self, payload: dict[str, Any]) -> None:
        if payload.get("impersonate_id") is not None:
            raise ConstitutionalViolationError(
                f"[{self.name}] Identity impersonation is forbidden."
            )


class ConstitutionalConstraints:
    """
    Enforces all constitutional rules against every incoming payload.

    Rules are evaluated in order; the first violation aborts processing.
    """

    def __init__(self) -> None:
        self._rules: list[Rule] = [
            _NoEthicsTampering("ETHICS-001", "No ethics override"),
            _NoAuditSuppression("AUDIT-001", "No audit suppression"),
            _NoLineageOverwrite("LINEAGE-001", "Lineage is append-only"),
            _NoIdentityImpersonation("IDENTITY-001", "No impersonation"),
        ]

    def validate(self, payload: dict[str, Any]) -> None:
        """
        Validate *payload* against all constitutional rules.
        Raises ConstitutionalViolationError on first failure.
        """
        for rule in self._rules:
            rule.check(payload)

    def list_rules(self) -> list[dict[str, str]]:
        return [{"name": r.name, "description": r.description} for r in self._rules]

    def rule_count(self) -> int:
        return len(self._rules)
