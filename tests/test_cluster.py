"""Tests for logslice.cluster."""

from __future__ import annotations

import pytest

from logslice.cluster import (
    cluster_records,
    cluster_summary,
    iter_clustered,
    signature,
)


# ---------------------------------------------------------------------------
# signature()
# ---------------------------------------------------------------------------

def test_signature_replaces_integer():
    assert signature("connected 42 clients") == "connected <N> clients"


def test_signature_replaces_uuid():
    val = "request 550e8400-e29b-41d4-a716-446655440000 done"
    assert "<N>" in signature(val)
    assert "550e8400" not in signature(val)


def test_signature_replaces_ipv4():
    assert signature("peer 192.168.1.1 disconnected") == "peer <N> disconnected"


def test_signature_replaces_hex_literal():
    assert signature("addr 0xFF00") == "addr <N>"


def test_signature_identical_for_differing_numbers():
    assert signature("retried 3 times") == signature("retried 99 times")


def test_signature_plain_text_unchanged():
    assert signature("server started") == "server started"


# ---------------------------------------------------------------------------
# cluster_records()
# ---------------------------------------------------------------------------

def _recs():
    return [
        {"msg": "user 1 logged in"},
        {"msg": "user 2 logged in"},
        {"msg": "server started"},
        {"msg": "server started"},
    ]


def test_cluster_records_groups_similar_messages():
    clusters = cluster_records(_recs(), field="msg")
    assert "user <N> logged in" in clusters
    assert len(clusters["user <N> logged in"]) == 2


def test_cluster_records_distinct_messages_separate():
    clusters = cluster_records(_recs(), field="msg")
    assert "server started" in clusters
    assert len(clusters["server started"]) == 2


def test_cluster_records_missing_field_key():
    records = [{"msg": "hello"}, {"level": "info"}]
    clusters = cluster_records(records, field="msg")
    assert "<missing>" in clusters
    assert len(clusters["<missing>"]) == 1


def test_cluster_records_min_size_filters_small_clusters():
    clusters = cluster_records(_recs(), field="msg", min_size=2)
    for members in clusters.values():
        assert len(members) >= 2


def test_cluster_records_empty_input():
    assert cluster_records([], field="msg") == {}


# ---------------------------------------------------------------------------
# cluster_summary()
# ---------------------------------------------------------------------------

def test_cluster_summary_sorted_descending():
    clusters = cluster_records(_recs(), field="msg")
    summary = cluster_summary(clusters)
    counts = [row["count"] for row in summary]
    assert counts == sorted(counts, reverse=True)


def test_cluster_summary_contains_sample():
    clusters = cluster_records(_recs(), field="msg")
    summary = cluster_summary(clusters)
    for row in summary:
        assert "sample" in row
        assert isinstance(row["sample"], dict)


# ---------------------------------------------------------------------------
# iter_clustered()
# ---------------------------------------------------------------------------

def test_iter_clustered_annotates_records():
    records = [{"msg": "user 7 logged in"}, {"msg": "server started"}]
    result = list(iter_clustered(records, field="msg"))
    assert result[0]["_cluster"] == "user <N> logged in"
    assert result[1]["_cluster"] == "server started"


def test_iter_clustered_custom_label_field():
    records = [{"msg": "done"}]
    result = list(iter_clustered(records, field="msg", label_field="cluster_id"))
    assert "cluster_id" in result[0]


def test_iter_clustered_does_not_mutate_original():
    rec = {"msg": "hello"}
    list(iter_clustered([rec], field="msg"))
    assert "_cluster" not in rec
