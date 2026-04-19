"""High-level report generation: aggregate log records and format the results."""

import json
from typing import Any, Dict, Iterable, List, Optional

from logslice.aggregator import count_by_field, summarise


def _table_row(cols: List[str], widths: List[int]) -> str:
    return "  ".join(str(c).ljust(w) for c, w in zip(cols, widths))


def _compute_widths(header: List[str], rows: List[List[str]]) -> List[int]:
    """Compute column widths based on the header and all data rows."""
    all_rows = [header] + rows
    return [max(len(r[i]) for r in all_rows) for i in range(len(header))]


def _build_table(header: List[str], rows: List[List[str]]) -> str:
    """Build a plain-text table string from a header and data rows."""
    widths = _compute_widths(header, rows)
    lines = [
        _table_row(header, widths),
        "-" * (sum(widths) + 2 * (len(widths) - 1)),
    ]
    for row in rows:
        lines.append(_table_row(row, widths))
    return "\n".join(lines)


def render_count_table(counts: List[tuple], field: str) -> str:
    """Render count_by_field results as a plain-text table."""
    header = [field, "count"]
    rows = [[str(v), str(c)] for v, c in counts]
    return _build_table(header, rows)


def render_summary_table(summary: List[Dict[str, Any]], group_field: str) -> str:
    """Render summarise() results as a plain-text table."""
    if not summary:
        return "(no data)"
    col_keys = list(summary[0].keys())
    header = [group_field if k == "group" else k for k in col_keys]
    rows = [[str(entry[k]) for k in col_keys] for entry in summary]
    return _build_table(header, rows)


def report(
    records: Iterable[Dict[str, Any]],
    group_field: str,
    count_field: Optional[str] = None,
    output_format: str = "table",
) -> str:
    """Generate a report string from an iterable of log records.

    Parameters
    ----------
    records:       parsed log records
    group_field:   field to group/count by
    count_field:   optional field for unique-value counting within each group
    output_format: ``'table'`` (default) or ``'json'``
    """
    record_list = list(records)

    if count_field is None:
        data = count_by_field(record_list, group_field)
        if output_format == "json":
            return json.dumps(
                [{"value": v, "count": c} for v, c in data], indent=2
            )
        return render_count_table(data, group_field)

    data_summary = summarise(record_list, group_field, count_field=count_field)
    if output_format == "json":
        return json.dumps(data_summary, indent=2)
    return render_summary_table(data_summary, group_field)
