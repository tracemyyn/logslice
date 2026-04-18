"""Tests for logslice.context."""
import pytest
from logslice.context import with_context


def _recs(n: int):
    return [{"i": i, "msg": f"line {i}"} for i in range(n)]


def test_no_context_yields_all_unchanged():
    recs = _recs(5)
    result = list(with_context(recs, before=0, after=0))
    assert [r["i"] for r in result] == list(range(5))
    assert all("_context" not in r for r in result)


def test_after_context_includes_following_records():
    recs = _recs(4)  # 0,1,2,3 — pretend all match
    result = list(with_context(recs, after=1))
    indices = [r["i"] for r in result]
    # Every record should appear at least once
    for i in range(4):
        assert i in indices


def test_before_context_tag():
    recs = _recs(3)
    result = list(with_context(recs, before=1))
    # First record has no predecessor, so no before-context entry for it
    context_roles = {r["i"]: r.get("_context") for r in result}
    # Record 0 itself has no _context tag
    assert context_roles.get(0) is None


def test_after_context_tag():
    recs = _recs(3)
    result = list(with_context(recs, after=1))
    roles = [r.get("_context") for r in result]
    assert "after" in roles


def test_no_duplicate_primary_records():
    recs = _recs(5)
    result = list(with_context(recs, before=2, after=2))
    primary = [r for r in result if r.get("_context") is None]
    primary_ids = [r["i"] for r in primary]
    assert len(primary_ids) == len(set(primary_ids))


def test_before_zero_after_zero_no_context_key():
    recs = _recs(3)
    for r in with_context(recs):
        assert "_context" not in r


def test_large_before_clipped_to_available():
    recs = _recs(3)
    result = list(with_context(recs, before=10))
    indices = [r["i"] for r in result]
    for i in range(3):
        assert i in indices
