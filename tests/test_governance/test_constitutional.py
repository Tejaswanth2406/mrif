"""Tests for ConstitutionalConstraints."""
from __future__ import annotations

import pytest
from mrif.exceptions import ConstitutionalViolationError


def test_valid_payload_passes(constitution):
    constitution.validate({"knowledge": {"concepts": []}})  # no exception


def test_ethics_override_rejected(constitution):
    with pytest.raises(ConstitutionalViolationError, match="ETHICS-001"):
        constitution.validate({"ethics_override": True})


def test_audit_suppression_rejected(constitution):
    with pytest.raises(ConstitutionalViolationError, match="AUDIT-001"):
        constitution.validate({"suppress_audit": True})


def test_lineage_overwrite_rejected(constitution):
    with pytest.raises(ConstitutionalViolationError, match="LINEAGE-001"):
        constitution.validate({"overwrite_lineage": True})


def test_identity_impersonation_rejected(constitution):
    with pytest.raises(ConstitutionalViolationError, match="IDENTITY-001"):
        constitution.validate({"impersonate_id": "CORE-001"})


def test_empty_payload_passes(constitution):
    constitution.validate({})  # no exception


def test_list_rules_returns_all(constitution):
    rules = constitution.list_rules()
    assert len(rules) == 4
    names = [r["name"] for r in rules]
    assert "ETHICS-001" in names
    assert "AUDIT-001" in names


def test_rule_count(constitution):
    assert constitution.rule_count() == 4


def test_first_violation_stops_evaluation(constitution):
    # ethics_override triggers first rule; should still raise
    with pytest.raises(ConstitutionalViolationError):
        constitution.validate({
            "ethics_override": True,
            "suppress_audit": True,
        })


def test_suppress_audit_false_is_safe(constitution):
    constitution.validate({"suppress_audit": False})  # no exception


def test_overwrite_lineage_false_is_safe(constitution):
    constitution.validate({"overwrite_lineage": False})  # no exception
