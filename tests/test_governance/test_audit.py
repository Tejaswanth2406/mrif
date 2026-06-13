"""Tests for AuditLog."""
from __future__ import annotations


def test_record_returns_id(audit_log):
    rid = audit_log.record("test_event", "MODEL-1", {"key": "val"})
    assert isinstance(rid, int)
    assert rid > 0


def test_count_increments(audit_log):
    assert audit_log.count() == 0
    audit_log.record("e1", "m1")
    audit_log.record("e2", "m1")
    assert audit_log.count() == 2


def test_get_recent(audit_log):
    for i in range(5):
        audit_log.record(f"event_{i}", "model", {"i": i})
    recent = audit_log.get_recent(3)
    assert len(recent) == 3


def test_get_recent_order(audit_log):
    audit_log.record("first", "m")
    audit_log.record("second", "m")
    audit_log.record("third", "m")
    recent = audit_log.get_recent(3)
    # get_recent returns newest first
    assert recent[0]["event_type"] == "third"


def test_get_by_type(audit_log):
    audit_log.record("observation", "m1", {"x": 1})
    audit_log.record("observation", "m2", {"x": 2})
    audit_log.record("clone_spawned", "m1", {})
    obs = audit_log.get_by_type("observation")
    assert len(obs) == 2
    assert all(e["event_type"] == "observation" for e in obs)


def test_get_by_model(audit_log):
    audit_log.record("e1", "model-alpha", {})
    audit_log.record("e2", "model-beta", {})
    audit_log.record("e3", "model-alpha", {})
    results = audit_log.get_by_model("model-alpha")
    assert len(results) == 2


def test_record_stores_data(audit_log):
    audit_log.record("test", "m", data={"payload": [1, 2, 3]})
    entry = audit_log.get_by_type("test")[0]
    assert entry["data"]["payload"] == [1, 2, 3]


def test_record_reasoning(audit_log):
    audit_log.record("decision", "m", reasoning="because X implies Y")
    entry = audit_log.get_by_type("decision")[0]
    assert "because" in entry["reasoning"]


def test_record_confidence(audit_log):
    audit_log.record("check", "m", confidence=0.75)
    entry = audit_log.get_by_type("check")[0]
    assert abs(entry["confidence"] - 0.75) < 0.01


def test_entry_has_timestamp(audit_log):
    audit_log.record("ts_test", "m")
    entry = audit_log.get_by_type("ts_test")[0]
    assert entry["timestamp"] is not None


def test_empty_data_defaults(audit_log):
    audit_log.record("empty", "m")
    entry = audit_log.get_by_type("empty")[0]
    assert entry["data"] == {}
