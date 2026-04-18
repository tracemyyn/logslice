import pytest
from logslice.pivot import pivot_records, column_names, fill_missing


@pytest.fixture()
def records():
    return [
        {"host": "a", "metric": "cpu", "value": 10},
        {"host": "a", "metric": "mem", "value": 80},
        {"host": "b", "metric": "cpu", "value": 20},
        {"host": "b", "metric": "mem", "value": 60},
    ]


def test_pivot_produces_one_row_per_index(records):
    result = pivot_records(records, "host", "metric", "value")
    assert len(result) == 2


def test_pivot_columns_are_metric_values(records):
    result = pivot_records(records, "host", "metric", "value")
    row_a = next(r for r in result if r["host"] == "a")
    assert row_a["cpu"] == 10
    assert row_a["mem"] == 80


def test_pivot_missing_index_skipped():
    recs = [{"metric": "cpu", "value": 5}]
    result = pivot_records(recs, "host", "metric", "value")
    assert result == []


def test_pivot_missing_column_skipped():
    recs = [{"host": "a", "value": 5}]
    result = pivot_records(recs, "host", "metric", "value")
    assert result == []


def test_column_names_excludes_index(records):
    pivoted = pivot_records(records, "host", "metric", "value")
    cols = column_names(pivoted, "host")
    assert "host" not in cols
    assert "cpu" in cols
    assert "mem" in cols


def test_column_names_sorted(records):
    pivoted = pivot_records(records, "host", "metric", "value")
    cols = column_names(pivoted, "host")
    assert cols == sorted(cols)


def test_fill_missing_adds_none_for_absent_columns():
    pivoted = [{"host": "a", "cpu": 10}]
    filled = fill_missing(pivoted, ["cpu", "mem"])
    assert filled[0]["mem"] is None


def test_fill_missing_custom_fill_value():
    pivoted = [{"host": "a", "cpu": 10}]
    filled = fill_missing(pivoted, ["cpu", "mem"], fill_value=0)
    assert filled[0]["mem"] == 0


def test_fill_missing_does_not_mutate_original():
    pivoted = [{"host": "a", "cpu": 10}]
    fill_missing(pivoted, ["cpu", "mem"])
    assert "mem" not in pivoted[0]
