"""Sampling utilities for reducing log output volume."""
from __future__ import annotations

import hashlib
from typing import Any, Dict, Iterator, List, Optional


def sample_records(
    records: Iterator[Dict[str, Any]],
    rate: float,
    field: Optional[str] = None,
) -> Iterator[Dict[str, Any]]:
    """Yield a subset of records according to *rate* (0.0–1.0).

    If *field* is given, sampling is deterministic and consistent per unique
    value of that field (useful for keeping all lines for a given request-id).
    Otherwise a simple modulo counter is used.
    """
    if not 0.0 < rate <= 1.0:
        raise ValueError(f"rate must be in (0, 1], got {rate}")

    if field is not None:
        yield from _field_sample(records, rate, field)
    else:
        yield from _counter_sample(records, rate)


def _counter_sample(
    records: Iterator[Dict[str, Any]],
    rate: float,
) -> Iterator[Dict[str, Any]]:
    every_n = max(1, round(1.0 / rate))
    for idx, record in enumerate(records):
        if idx % every_n == 0:
            yield record


def _field_sample(
    records: Iterator[Dict[str, Any]],
    rate: float,
    field: str,
) -> Iterator[Dict[str, Any]]:
    """Deterministic sampling: hash the field value and keep if below threshold."""
    threshold = int(rate * 0xFFFFFFFF)
    for record in records:
        value = str(record.get(field, ""))
        digest = int(hashlib.md5(value.encode()).hexdigest()[:8], 16)
        if digest <= threshold:
            yield record


def reservoir_sample(
    records: Iterator[Dict[str, Any]],
    k: int,
) -> List[Dict[str, Any]]:
    """Return exactly *k* records chosen uniformly at random (reservoir sampling)."""
    import random

    reservoir: List[Dict[str, Any]] = []
    for idx, record in enumerate(records):
        if idx < k:
            reservoir.append(record)
        else:
            j = random.randint(0, idx)
            if j < k:
                reservoir[j] = record
    return reservoir
