"""batch.py — process records in fixed-size or time-based batches."""
from __future__ import annotations

from typing import Callable, Iterable, Iterator, List, Optional

Record = dict


def batch_by_size(records: Iterable[Record], size: int) -> Iterator[List[Record]]:
    """Yield lists of *size* records.  The last batch may be smaller."""
    if size < 1:
        raise ValueError(f"batch size must be >= 1, got {size}")
    buf: List[Record] = []
    for rec in records:
        buf.append(rec)
        if len(buf) >= size:
            yield buf
            buf = []
    if buf:
        yield buf


def batch_by_field(
    records: Iterable[Record],
    field: str,
    missing: str = "__missing__",
) -> Iterator[List[Record]]:
    """Yield a new batch whenever *field* changes value (run-length grouping)."""
    buf: List[Record] = []
    current_val: Optional[str] = None
    first = True
    for rec in records:
        val = str(rec.get(field, missing))
        if first:
            current_val = val
            first = False
        if val != current_val:
            if buf:
                yield buf
            buf = []
            current_val = val
        buf.append(rec)
    if buf:
        yield buf


def apply_batch(
    records: Iterable[Record],
    size: Optional[int],
    field: Optional[str],
    reducer: Callable[[List[Record]], Record],
) -> Iterator[Record]:
    """Apply *reducer* to each batch and yield the resulting summary records.

    If both *size* and *field* are None the records are passed through unchanged.
    *size* takes precedence over *field* when both are supplied.
    """
    if size is not None:
        for batch in batch_by_size(records, size):
            yield reducer(batch)
    elif field is not None:
        for batch in batch_by_field(records, field):
            yield reducer(batch)
    else:
        yield from records


def default_reducer(batch: List[Record]) -> Record:
    """Merge all records in *batch*; later records overwrite earlier ones."""
    merged: Record = {}
    for rec in batch:
        merged.update(rec)
    merged["_batch_size"] = len(batch)
    return merged
