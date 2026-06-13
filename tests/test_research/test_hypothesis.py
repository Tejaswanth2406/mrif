"""Tests for HypothesisGenerator."""
from __future__ import annotations

from mrif.research.hypothesis import HypothesisGenerator, HypothesisStatus


def test_generate_returns_correct_count():
    gen = HypothesisGenerator()
    hyps = gen.generate("What causes X?", question_id="q1", n=3)
    assert len(hyps) == 3


def test_generate_links_question_id():
    gen = HypothesisGenerator()
    hyps = gen.generate("Q?", question_id="q-99", n=2)
    assert all(h.question_id == "q-99" for h in hyps)


def test_generate_initial_status_pending():
    gen = HypothesisGenerator()
    hyps = gen.generate("Q?", question_id="q1", n=2)
    assert all(h.status == HypothesisStatus.PENDING for h in hyps)


def test_generate_has_statement():
    gen = HypothesisGenerator()
    hyps = gen.generate("Why?", question_id="q1", n=1)
    assert hyps[0].statement != ""


def test_generate_confidence_in_range():
    gen = HypothesisGenerator()
    hyps = gen.generate("H?", question_id="q1", n=3)
    for h in hyps:
        assert 0.0 <= h.confidence <= 1.0


def test_hypothesis_update_confidence():
    gen = HypothesisGenerator()
    h = gen.generate("Q?", question_id="q1", n=1)[0]
    original = h.confidence
    h.update_confidence(+0.2)
    assert abs(h.confidence - min(1.0, original + 0.2)) < 0.001


def test_hypothesis_confidence_clamps_at_one():
    gen = HypothesisGenerator()
    h = gen.generate("Q?", question_id="q1", n=1)[0]
    h.update_confidence(+999)
    assert h.confidence == 1.0


def test_hypothesis_confidence_clamps_at_zero():
    gen = HypothesisGenerator()
    h = gen.generate("Q?", question_id="q1", n=1)[0]
    h.update_confidence(-999)
    assert h.confidence == 0.0


def test_generate_with_context():
    gen = HypothesisGenerator()
    hyps = gen.generate("Q?", question_id="q1", n=2, context={"domain": "physics"})
    assert len(hyps) == 2


def test_hypothesis_has_unique_ids():
    gen = HypothesisGenerator()
    hyps = gen.generate("Q?", question_id="q1", n=5)
    ids = [h.hypothesis_id for h in hyps]
    assert len(set(ids)) == 5
