"""CLI integration for the label feature."""

from __future__ import annotations

import argparse
from typing import Any, Dict, Iterable, Optional

from logslice.label import label_records, parse_label_args

Record = Dict[str, Any]


def add_label_args(parser: argparse.ArgumentParser) -> None:
    """Register --label and --label-default flags on *parser*."""
    parser.add_argument(
        "--label",
        metavar="DEST:SRC:PATTERN:VALUE",
        action="append",
        default=[],
        help=(
            "Add a label field to each record.  Format: "
            "dest_field:src_field:regex_pattern:label_value.  "
            "First matching rule wins.  May be repeated."
        ),
    )
    parser.add_argument(
        "--label-default",
        metavar="VALUE",
        default=None,
        help="Default label value when no rule matches.",
    )


def apply_label_args(
    args: argparse.Namespace,
    records: Iterable[Record],
) -> Iterable[Record]:
    """Apply label rules from parsed CLI args to *records*.

    Returns the original iterable unchanged when no --label flags are given.
    """
    if not args.label:
        return records
    rules = parse_label_args(args.label)
    default: Optional[str] = args.label_default
    return label_records(records, rules, default=default)
