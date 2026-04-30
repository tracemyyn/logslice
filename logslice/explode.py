"""explode.py – expand a repeated/array field into one record per element.

If a field contains a list, ``explode_field`` emits one copy of the record
for every element, replacing the field value with the individual element.
Records where the field is absent or not a list are passed through unchanged
(or optionally dropped).
"""

from __future__ import annotations

from typing import Dict, Any, Iterable, Iterator, List, Optional


Record = Dict[str, Any]


def explode_field(
    record: Record,
    field: str,
    *,
    drop_non_list: bool = False,
) -> List[Record]:
    """Return one record per element of *field* if it holds a list.

    Parameters
    ----------
    record:
        The source log record.
    field:
        Key whose value should be exploded.
    drop_non_list:
        When *True*, records where *field* is absent or not a list are
        discarded; otherwise they are returned as-is.
    """
    value = record.get(field)
    if not isinstance(value, list):
        return [] if drop_non_list else [record]
    if not value:
        return [] if drop_non_list else [record]
    results: List[Record] = []
    for element in value:
        new_record = dict(record)
        new_record[field] = element
        results.append(new_record)
    return results


def explode_records(
    records: Iterable[Record],
    field: str,
    *,
    drop_non_list: bool = False,
) -> Iterator[Record]:
    """Yield exploded records from an iterable of log records."""
    for record in records:
        yield from explode_field(record, field, drop_non_list=drop_non_list)


def parse_explode_arg(arg: Optional[str]) -> Optional[str]:
    """Validate and return the field name, or *None* if *arg* is falsy."""
    if not arg:
        return None
    arg = arg.strip()
    if not arg:
        raise ValueError("explode field name must not be blank")
    return arg
