"""CLI integration for the split feature."""
from __future__ import annotations

import argparse
from typing import Dict, Iterable, List, Optional

from logslice.split import apply_split, bucket_sizes


def add_split_args(parser: argparse.ArgumentParser) -> None:
    """Register --split-by and --split-pattern flags on *parser*."""
    parser.add_argument(
        "--split-by",
        metavar="FIELD",
        default=None,
        help="Split records into buckets by the value of FIELD.",
    )
    parser.add_argument(
        "--split-pattern",
        metavar="LABEL:PATTERN",
        dest="split_patterns",
        action="append",
        default=None,
        help=(
            "Assign records to LABEL when FIELD value matches PATTERN (regex). "
            "May be repeated; first match wins."
        ),
    )
    parser.add_argument(
        "--split-missing",
        metavar="KEY",
        default="__missing__",
        help="Bucket name for records where --split-by field is absent (default: __missing__).",
    )


def apply_split_args(
    args: argparse.Namespace,
    records: Iterable[dict],
) -> Dict[str, List[dict]]:
    """Apply split arguments from *args* to *records*.

    Returns a dict of bucket_name -> list[record].  When no split flag is
    given the single key ``"all"`` contains every record unchanged.
    """
    field: Optional[str] = getattr(args, "split_by", None)
    patterns: Optional[List[str]] = getattr(args, "split_patterns", None)
    missing_key: str = getattr(args, "split_missing", "__missing__")

    return apply_split(
        records,
        field=field,
        patterns=patterns or [],
        missing_key=missing_key,
    )
