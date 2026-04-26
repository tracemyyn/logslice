"""Tests for logslice.batch and logslice.cli_batch."""
from __future__ import annotations

import argparse
from typing import List

import pytest

from logslice.batch import (
    apply_batch,
    batch_by_field,
    batch_by_size,
    default_reducer,
)
from logslice.cli_batch import add_batch_args, apply_batch_args


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _recs(n: int) -> List[dict]:
    return [{"i": i, "v": str(i % 3)} for i in range(n)]


# ---------------------------------------------------------------------------
# batch_by_size
# ---------------------------------------------------------------------------

def test_batch_by_size_even_split():
    batches = list(batch_by_size(_recs(6), 2))
    assert len(batches) == 3
    assert all(len(b) == 2 for b in batches)


def test_batch_by_size_remainder():
    batches = list(batch_by_size(_recs(5), 2))
    assert len(batches) == 3
    assert len(batches[-1]) == 1


def test_batch_by_size_larger_than_input():
    batches = list(batch_by_size(_recs(3), 10))
    assert len(batches) == 1
    assert len(batches[0]) == 3


def test_batch_by_size_invalid_raises():
    with pytest.raises(ValueError):
        list(batch_by_size(_recs(4), 0))


def test_batch_by_size_empty_input():
    assert list(batch_by_size([], 3)) == []


# ---------------------------------------------------------------------------
# batch_by_field
# ---------------------------------------------------------------------------

def test_batch_by_field_groups_runs():
    recs = [
        {"env": "prod", "x": 1},
        {"env": "prod", "x": 2},
        {"env": "dev",  "x": 3},
        {"env": "dev",  "x": 4},
        {"env": "prod", "x": 5},
    ]
    batches = list(batch_by_field(recs, "env"))
    assert len(batches) == 3
    assert len(batches[0]) == 2
    assert len(batches[1]) == 2
    assert len(batches[2]) == 1


def test_batch_by_field_missing_key_grouped_together():
    recs = [{"x": 1}, {"x": 2}, {"env": "prod", "x": 3}]
    batches = list(batch_by_field(recs, "env"))
    assert len(batches) == 2
    assert len(batches[0]) == 2  # both missing grouped


def test_batch_by_field_empty_input():
    assert list(batch_by_field([], "env")) == []


# ---------------------------------------------------------------------------
# default_reducer
# ---------------------------------------------------------------------------

def test_default_reducer_merges_records():
    batch = [{"a": 1, "b": 2}, {"b": 99, "c": 3}]
    result = default_reducer(batch)
    assert result["a"] == 1
    assert result["b"] == 99
    assert result["c"] == 3
    assert result["_batch_size"] == 2


def test_default_reducer_single_record():
    rec = {"a": 1}
    result = default_reducer([rec])
    assert result["_batch_size"] == 1


# ---------------------------------------------------------------------------
# apply_batch passthrough
# ---------------------------------------------------------------------------

def test_apply_batch_no_options_passthrough():
    recs = _recs(4)
    result = list(apply_batch(recs, size=None, field=None, reducer=default_reducer))
    assert result == recs


# ---------------------------------------------------------------------------
# CLI glue
# ---------------------------------------------------------------------------

def _make_args(**kwargs) -> argparse.Namespace:
    defaults = {"batch_size": None, "batch_field": None}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_add_batch_args_registers_size():
    p = argparse.ArgumentParser()
    add_batch_args(p)
    args = p.parse_args(["--batch-size", "5"])
    assert args.batch_size == 5


def test_add_batch_args_registers_field():
    p = argparse.ArgumentParser()
    add_batch_args(p)
    args = p.parse_args(["--batch-field", "env"])
    assert args.batch_field == "env"


def test_apply_batch_args_no_flags_passthrough():
    recs = _recs(4)
    result = list(apply_batch_args(recs, _make_args()))
    assert result == recs


def test_apply_batch_args_size_flag():
    recs = _recs(6)
    result = list(apply_batch_args(recs, _make_args(batch_size=3)))
    assert len(result) == 2
    assert result[0]["_batch_size"] == 3
