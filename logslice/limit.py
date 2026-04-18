"""Record limiting and offset utilities."""
from typing import Iterable, Iterator


def skip_records(records: Iterable[dict], offset: int) -> Iterator[dict]:
    """Skip the first *offset* records."""
    if offset <= 0:
        yield from records
        return
    skipped = 0
    for record in records:
        if skipped < offset:
            skipped += 1
            continue
        yield record


def limit_records(records: Iterable[dict], count: int) -> Iterator[dict]:
    """Yield at most *count* records."""
    if count <= 0:
        return
    emitted = 0
    for record in records:
        yield record
        emitted += 1
        if emitted >= count:
            break


def apply_limit(records: Iterable[dict], offset: int = 0, limit: int = 0) -> Iterator[dict]:
    """Apply optional offset then limit to a record stream.

    Args:
        records: iterable of parsed log records.
        offset:  number of records to skip from the start (0 = no skip).
        limit:   maximum records to emit (0 = no limit).
    """
    result: Iterable[dict] = records
    if offset > 0:
        result = skip_records(result, offset)
    if limit > 0:
        result = limit_records(result, limit)
    yield from result
