"""Tests for IdentityRegistry (Dimension I)."""
from __future__ import annotations

import pytest
from mrif.dimensions.identity import IdentityRegistry


def test_core_registered_on_init(identity_registry):
    agent = identity_registry.get("TEST-CORE")
    assert agent is not None
    assert agent.status == "active"


def test_core_has_all_permissions(identity_registry):
    assert identity_registry.has_permission("TEST-CORE", "any_permission") is True


def test_register_clone(identity_registry):
    clone_id = identity_registry.register_clone(
        parent_id="TEST-CORE", goal="research"
    )
    clone = identity_registry.get(clone_id)
    assert clone is not None
    assert clone.goal == "research"
    assert clone.parent_id == "TEST-CORE"


def test_clone_inherits_lineage(identity_registry):
    clone_id = identity_registry.register_clone(
        parent_id="TEST-CORE", goal="task"
    )
    lineage = identity_registry.get_lineage(clone_id)
    assert "TEST-CORE" in lineage


def test_clone_permissions_default(identity_registry):
    clone_id = identity_registry.register_clone(
        parent_id="TEST-CORE", goal="default-perms"
    )
    assert identity_registry.has_permission(clone_id, "read_global_memory")


def test_clone_custom_permissions(identity_registry):
    clone_id = identity_registry.register_clone(
        parent_id="TEST-CORE",
        goal="limited",
        permissions=["read_global_memory", "create_simulations"],
    )
    assert identity_registry.has_permission(clone_id, "create_simulations")
    assert not identity_registry.has_permission(clone_id, "write_global_memory")


def test_active_count(identity_registry):
    initial = identity_registry.get_active_count()
    identity_registry.register_clone(parent_id="TEST-CORE", goal="a")
    identity_registry.register_clone(parent_id="TEST-CORE", goal="b")
    assert identity_registry.get_active_count() == initial + 2


def test_retire_clone(identity_registry):
    clone_id = identity_registry.register_clone(
        parent_id="TEST-CORE", goal="retire-me"
    )
    identity_registry.retire_clone(clone_id)
    agent = identity_registry.get(clone_id)
    assert agent.status == "retired"


def test_archive_clone(identity_registry):
    clone_id = identity_registry.register_clone(
        parent_id="TEST-CORE", goal="archive-me"
    )
    identity_registry.archive_clone(clone_id)
    assert identity_registry.get(clone_id).status == "archived"


def test_list_active_excludes_retired(identity_registry):
    clone_id = identity_registry.register_clone(
        parent_id="TEST-CORE", goal="will-retire"
    )
    identity_registry.retire_clone(clone_id)
    active_ids = [a.agent_id for a in identity_registry.list_active()]
    assert clone_id not in active_ids


def test_get_unknown_returns_none(identity_registry):
    assert identity_registry.get("nonexistent") is None


def test_has_permission_unknown_agent(identity_registry):
    assert identity_registry.has_permission("ghost", "anything") is False


def test_export_returns_all(identity_registry):
    identity_registry.register_clone(parent_id="TEST-CORE", goal="x")
    exported = identity_registry.export()
    assert len(exported) >= 2
    assert all("agent_id" in e for e in exported)
