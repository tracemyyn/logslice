"""CLI integration for record sorting."""

import argparse
from typing import Any, Dict, List, Optional

from logslice.sort import sort_records

Record = Dict[str, Any]


def add_sort_args(parser: argparse.ArgumentParser) -> None:
    """Register sort-related CLI arguments on *parser*."""
    parser.add_argument(
        "--sort",
        metavar="FIELD",
        nargs="+",
        dest="sort_fields",
        help="Sort output records by these fields (left = primary key).",
    )
    parser.add_argument(
        "--sort-desc",
        action="store_true",
        default=False,
        help="Sort in descending order.",
    )
    parser.add_argument(
        "--sort-numeric",
        action="store_true",
        default=False,
        help="Coerce sort field values to numbers before comparing.",
    )


def apply_sort(
    records: List[Record],
    args: argparse.Namespace,
) -> List[Record]:
    """Apply sorting to *records* according to parsed *args*.

    Returns the original list unchanged when no sort fields are specified.
    """
    fields: Optional[List[str]] = getattr(args, "sort_fields", None)
    if not fields:
        return records
    return sort_records(
        records,
        fields=fields,
        reverse=getattr(args, "sort_desc", False),
        numeric=getattr(args, "sort_numeric", False),
    )
