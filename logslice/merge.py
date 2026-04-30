"""Merge multiple streams of log records, optionally sorted by timestamp."""

from __future__ import annotations

import heapq
from typing import Iterable, Iterator, List, Optional

from logslice.time_filter import extract_timestamp


def merge_sorted(
    *streams: Iterable[dict],
    ts_field: str = "ts",
) -> Iterator[dict]:
    """Merge pre-sorted record streams into a single timestamp-ordered stream.

    Uses a min-heap so memory usage is O(number of streams), not O(total records).
    Streams that lack a timestamp are emitted in arrival order after sorted ones.
    """
    iterators = [iter(s) for s in streams]
    heap: List[tuple] = []

    for idx, it in enumerate(iterators):
        rec = next(it, None)
        if rec is None:
            continue
        ts = extract_timestamp(rec, ts_field)
        heap.append((ts or "", idx, rec, it))

    heapq.heapify(heap)

    while heap:
        ts_val, idx, rec, it = heapq.heappop(heap)
        yield rec
        nxt = next(it, None)
        if nxt is not None:
            nts = extract_timestamp(nxt, ts_field)
            heapq.heappush(heap, (nts or "", idx, nxt, it))


def merge_unsorted(
    *streams: Iterable[dict],
) -> Iterator[dict]:
    """Interleave streams without sorting — round-robin until all exhausted."""
    iterators = [iter(s) for s in streams]
    while iterators:
        still_alive = []
        for it in iterators:
            rec = next(it, None)
            if rec is not None:
                yield rec
                still_alive.append(it)
        iterators = still_alive


def apply_merge(
    streams: List[Iterable[dict]],
    sort: bool = True,
    ts_field: str = "ts",
) -> Iterator[dict]:
    """Public entry point: merge *streams*, sorting by *ts_field* when requested."""
    if not streams:
        return iter([])
    if len(streams) == 1:
        return iter(streams[0])
    if sort:
        return merge_sorted(*streams, ts_field=ts_field)
    return merge_unsorted(*streams)
