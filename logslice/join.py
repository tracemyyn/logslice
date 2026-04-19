"""Join records from two streams on a common field."""
from typing import Dict, Iterable, Iterator, List, Optional


def build_index(
    records: Iterable[Dict],
    key: str,
) -> Dict[str, List[Dict]]:
    """Index records by the value of *key*."""
    index: Dict[str, List[Dict]] = {}
    for rec in records:
        val = str(rec.get(key, ""))
        if val:
            index.setdefault(val, []).append(rec)
    return index


def inner_join(
    left: Iterable[Dict],
    right_index: Dict[str, List[Dict]],
    key: str,
    prefix: str = "right_",
) -> Iterator[Dict]:
    """Yield merged records where *key* exists in both sides."""
    for rec in left:
        val = str(rec.get(key, ""))
        for match in right_index.get(val, []):
            merged = dict(rec)
            for k, v in match.items():
                if k != key:
                    merged[prefix + k] = v
            yield merged


def left_join(
    left: Iterable[Dict],
    right_index: Dict[str, List[Dict]],
    key: str,
    prefix: str = "right_",
) -> Iterator[Dict]:
    """Yield all left records, enriched where a right match exists."""
    for rec in left:
        val = str(rec.get(key, ""))
        matches = right_index.get(val, [{}])
        for match in matches:
            merged = dict(rec)
            for k, v in match.items():
                if k != key:
                    merged[prefix + k] = v
            yield merged
            if not right_index.get(val):
                break


def apply_join(
    left: Iterable[Dict],
    right: Iterable[Dict],
    key: str,
    how: str = "inner",
    prefix: str = "right_",
) -> Iterator[Dict]:
    """Apply a join between *left* and *right* streams on *key*."""
    index = build_index(right, key)
    if how == "left":
        yield from left_join(left, index, key, prefix)
    else:
        yield from inner_join(left, index, key, prefix)
