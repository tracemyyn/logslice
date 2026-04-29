"""Top-N and bottom-N record selection by a numeric field."""
from __future__ import annotations

from typing import Iterable, Iterator, List


def _coerce(value: object) -> float:
    """Try to convert *value* to float; raise ValueError on failure."""
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Cannot coerce {value!r} to float") from exc


def top_n(
    records: Iterable[dict],
    field: str,
    n: int,
    *,
    skip_missing: bool = True,
) -> List[dict]:
    """Return the *n* records with the highest value for *field*.

    Records that lack *field* (or whose value cannot be coerced to float)
    are skipped when *skip_missing* is True; otherwise a ValueError is raised.
    """
    if n < 0:
        raise ValueError(f"n must be non-negative, got {n}")

    scored: list[tuple[float, dict]] = []
    for rec in records:
        raw = rec.get(field)
        if raw is None:
            if skip_missing:
                continue
            raise ValueError(f"Field {field!r} missing from record")
        try:
            scored.append((_coerce(raw), rec))
        except ValueError:
            if not skip_missing:
                raise

    scored.sort(key=lambda t: t[0], reverse=True)
    return [r for _, r in scored[:n]]


def bottom_n(
    records: Iterable[dict],
    field: str,
    n: int,
    *,
    skip_missing: bool = True,
) -> List[dict]:
    """Return the *n* records with the lowest value for *field*."""
    if n < 0:
        raise ValueError(f"n must be non-negative, got {n}")

    scored: list[tuple[float, dict]] = []
    for rec in records:
        raw = rec.get(field)
        if raw is None:
            if skip_missing:
                continue
            raise ValueError(f"Field {field!r} missing from record")
        try:
            scored.append((_coerce(raw), rec))
        except ValueError:
            if not skip_missing:
                raise

    scored.sort(key=lambda t: t[0])
    return [r for _, r in scored[:n]]


def iter_top_n(
    records: Iterable[dict],
    field: str,
    n: int,
    *,
    reverse: bool = True,
    skip_missing: bool = True,
) -> Iterator[dict]:
    """Yield records from :func:`top_n` (or :func:`bottom_n`) one at a time."""
    fn = top_n if reverse else bottom_n
    yield from fn(records, field, n, skip_missing=skip_missing)
