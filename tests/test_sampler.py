"""Tests for logslice.sampler."""
from __future__ import annotations

import pytest

from logslice.sampler import reservoir_sample, sample_records


def _records(n: int = 100):
    return [{"idx": i, "svc": "a" if i % 2 == 0 else "b"} for i in range(n)]


# ---------------------------------------------------------------------------
# sample_records – counter mode
# ---------------------------------------------------------------------------

def test_sample_rate_1_returns_all():
    recs = _records(10)
    result = list(sample_records(iter(recs), rate=1.0))
    assert result == recs


def test_sample_rate_half_roughly_halves():
    recs = _records(100)
    result = list(sample_records(iter(recs), rate=0.5))
    assert 40 <= len(result) <= 60


def test_sample_rate_invalid_raises():
    with pytest.raises(ValueError):
        list(sample_records(iter([]), rate=0.0))
    with pytest.raises(ValueError):
        list(sample_records(iter([]), rate=1.5))


def test_sample_first_record_always_included():
    recs = _records(50)
    result = list(sample_records(iter(recs), rate=0.1))
    assert result[0]["idx"] == 0


def test_sample_preserves_record_contents():
    """Sampled records should be the original dicts, not copies."""
    recs = _records(20)
    result = list(sample_records(iter(recs), rate=1.0))
    for original, sampled in zip(recs, result):
        assert sampled is original


# ---------------------------------------------------------------------------
# sample_records – field mode
# ---------------------------------------------------------------------------

def test_field_sample_deterministic():
    recs = _records(200)
    r1 = list(sample_records(iter(recs), rate=0.5, field="svc"))
    r2 = list(sample_records(iter(recs), rate=0.5, field="svc"))
    assert r1 == r2


def test_field_sample_consistent_per_value():
    """All records with the same field value should be kept or all dropped."""
    recs = _records(100)
    result = list(sample_records(iter(recs), rate=0.5, field="svc"))
    kept_svcs = {r["svc"] for r in result}
    # Every record whose svc is in kept_svcs must appear in result
    expected = [r for r in recs if r["svc"] in kept_svcs]
    assert result == expected


def test_field_sample_missing_field_uses_empty_string():
    recs = [{"x": i} for i in range(50)]
    # Should not raise
    result = list(sample_records(iter(recs), rate=0.5, field="svc"))
    # All records share the same missing-field value so all kept or all dropped
    assert len(result) in (0, 50)


# ---------------------------------------------------------------------------
# reservoir_sample
# ---------------------------------------------------------------------------

def test_reservoir_returns_k_records():
    recs = _records(100)
    result = reservoir_sample(iter(recs), k=10)
    assert len(result) == 10


def test_reservoir_fewer_than_k():
    recs = _records(5)
    result = reservoir_sample(iter(recs), k=20)
    assert len(result) == 5


def test_reservoir_records_are_original():
    recs = _records(50)
    result = reservoir_sample(iter(recs), k=10)
    for r in result:
        assert r in recs


def test_reservoir_no_duplicates():
    """reservoir_sample should never return the same record twice."""
    recs = _records(50)
    result = reservoir_sample(iter(recs), k=20)
    indices = [r["idx"] for r in result]
    assert len(indices) == len(set(indices))
