import pytest
from logslice.stats import collect_values, compute_stats, field_stats


def _recs():
    return [
        {"latency": "10", "status": "200"},
        {"latency": "20", "status": "200"},
        {"latency": "30", "status": "500"},
        {"latency": "40"},
        {"latency": "bad"},
        {"other": "5"},
    ]


def test_collect_values_numeric_only():
    vals = collect_values(_recs(), "latency")
    assert vals == [10.0, 20.0, 30.0, 40.0]


def test_collect_values_missing_field_skipped():
    vals = collect_values(_recs(), "latency")
    assert len(vals) == 4


def test_collect_values_unknown_field_empty():
    vals = collect_values(_recs(), "nope")
    assert vals == []


def test_compute_stats_empty():
    result = compute_stats([])
    assert result == {"count": 0}


def test_compute_stats_single():
    result = compute_stats([5.0])
    assert result["count"] == 1
    assert result["min"] == 5.0
    assert result["max"] == 5.0
    assert result["mean"] == 5.0
    assert result["stddev"] == 0.0


def test_compute_stats_basic():
    result = compute_stats([10.0, 20.0, 30.0, 40.0])
    assert result["count"] == 4
    assert result["min"] == 10.0
    assert result["max"] == 40.0
    assert result["mean"] == 25.0


def test_compute_stats_p50():
    result = compute_stats([10.0, 20.0, 30.0, 40.0])
    assert result["p50"] == pytest.approx(25.0)


def test_compute_stats_p99_large():
    vals = list(range(1, 101))
    result = compute_stats([float(v) for v in vals])
    assert result["p99"] == pytest.approx(99.01, rel=1e-3)


def test_field_stats_integration():
    result = field_stats(_recs(), "latency")
    assert result["count"] == 4
    assert result["min"] == 10.0
    assert result["max"] == 40.0


def test_field_stats_no_data():
    result = field_stats(_recs(), "missing")
    assert result == {"count": 0}
