"""Simple aggregation utilities for counted/grouped log summaries."""

from collections import Counter, defaultdict
from typing import Any, Dict, Iterable, List, Optional, Tuple


def count_by_field(
    records: Iterable[Dict[str, Any]], field: str
) -> List[Tuple[str, int]]:
    """Count occurrences of each unique value for *field* across records.

    Returns a list of (value, count) tuples sorted by count descending.
    Records missing the field are grouped under the key '<missing>'.
    """
    counter: Counter = Counter()
    for record in records:
        value = str(record.get(field, "<missing>"))
        counter[value] += 1
    return counter.most_common()


def group_by_field(
    records: Iterable[Dict[str, Any]], field: str
) -> Dict[str, List[Dict[str, Any]]]:
    """Group records by the unique values of *field*.

    Returns a dict mapping each distinct value to the list of matching records.
    """
    groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for record in records:
        key = str(record.get(field, "<missing>"))
        groups[key].append(record)
    return dict(groups)


def summarise(
    records: Iterable[Dict[str, Any]],
    group_field: str,
    count_field: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Return a summary list with group key, record count, and optional field stats.

    Each entry in the returned list has:
      - ``group``  – the value of *group_field*
      - ``count``  – number of records in the group
      - ``unique`` – number of unique values for *count_field* (if supplied)
    """
    groups = group_by_field(records, group_field)
    summary = []
    for key, group_records in sorted(groups.items()):
        entry: Dict[str, Any] = {"group": key, "count": len(group_records)}
        if count_field is not None:
            unique_vals = {str(r.get(count_field, "")) for r in group_records}
            entry["unique"] = len(unique_vals)
        summary.append(entry)
    return summary
