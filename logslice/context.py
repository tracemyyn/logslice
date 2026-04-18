"""Context lines: include N lines before/after matching records."""
from collections import deque
from typing import Iterable, Iterator, List, Optional


def with_context(
    records: Iterable[dict],
    before: int = 0,
    after: int = 0,
) -> Iterator[dict]:
    """Yield records with context neighbours included.

    Records added as context carry a ``_context`` key set to ``"before"`` or
    ``"after"`` so callers can optionally style them differently.
    """
    if before == 0 and after == 0:
        yield from records
        return

    buf: deque = deque(maxlen=before)
    pending_after: List[dict] = []  # (record, remaining_after_count)
    after_counters: deque = deque()  # counts of after-lines still owed

    emitted_ids = set()

    def _mark(record: dict, role: Optional[str]) -> dict:
        out = dict(record)
        if role:
            out["_context"] = role
        return out

    for record in records:
        # Emit any still-pending after-context that this record satisfies
        new_counters: deque = deque()
        for count in after_counters:
            rid = id(record)
            if rid not in emitted_ids:
                emitted_ids.add(rid)
                yield _mark(record, "after")
            if count - 1 > 0:
                new_counters.append(count - 1)
        after_counters = new_counters

        # Emit before-context
        for prev in buf:
            pid = id(prev)
            if pid not in emitted_ids:
                emitted_ids.add(pid)
                yield _mark(prev, "before")

        # Emit the matching record itself
        rid = id(record)
        if rid not in emitted_ids:
            emitted_ids.add(rid)
            yield _mark(record, None)

        if after > 0:
            after_counters.append(after)

        buf.append(record)
