"""Cluster log records by similarity of a given field value.

Records are grouped into clusters based on a normalised 'signature'
derived from the chosen field.  Numbers, UUIDs and hex strings are
replaced by a placeholder so that messages that differ only in dynamic
parts land in the same cluster.
"""

from __future__ import annotations

import re
from collections import defaultdict
from typing import Dict, Iterable, Iterator, List, Optional

_DYNAMIC = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"  # UUID
    r"|0x[0-9a-fA-F]+"  # hex literal
    r"|\b\d+\.\d+\.\d+\.\d+\b"  # IPv4
    r"|\b\d+\b",  # plain integer
    re.IGNORECASE,
)


def signature(value: str) -> str:
    """Return a normalised signature for *value* by collapsing dynamic tokens."""
    return _DYNAMIC.sub("<N>", value).strip()


def cluster_records(
    records: Iterable[dict],
    field: str,
    min_size: int = 1,
) -> Dict[str, List[dict]]:
    """Group *records* into clusters keyed by the signature of *field*.

    Records missing *field* are collected under the key ``"<missing>"``.
    Clusters with fewer than *min_size* members are dropped.
    """
    buckets: Dict[str, List[dict]] = defaultdict(list)
    for record in records:
        value = record.get(field)
        key = signature(str(value)) if value is not None else "<missing>"
        buckets[key].append(record)
    if min_size > 1:
        buckets = {k: v for k, v in buckets.items() if len(v) >= min_size}
    return dict(buckets)


def cluster_summary(
    clusters: Dict[str, List[dict]],
) -> List[dict]:
    """Return a list of summary records sorted by cluster size descending."""
    rows = [
        {"signature": sig, "count": len(members), "sample": members[0]}
        for sig, members in clusters.items()
    ]
    rows.sort(key=lambda r: r["count"], reverse=True)
    return rows


def iter_clustered(
    records: Iterable[dict],
    field: str,
    label_field: str = "_cluster",
) -> Iterator[dict]:
    """Yield each record annotated with its cluster signature in *label_field*."""
    for record in records:
        value = record.get(field)
        key = signature(str(value)) if value is not None else "<missing>"
        yield {**record, label_field: key}
