"""cli_threshold.py – CLI integration for threshold alerting."""
from __future__ import annotations

import argparse
from typing import Any, Dict, Iterable, Iterator, List, Optional

from logslice.threshold import apply_thresholds, parse_threshold_arg


def add_threshold_args(parser: argparse.ArgumentParser) -> None:
    """Register --threshold and related flags on *parser*."""
    parser.add_argument(
        "--threshold",
        metavar="FIELD:OP:VALUE",
        action="append",
        dest="thresholds",
        default=[],
        help=(
            "Alert when FIELD satisfies OP against VALUE. "
            "OP is one of gt, gte, lt, lte, eq, ne. "
            "May be repeated."
        ),
    )
    parser.add_argument(
        "--threshold-tag",
        metavar="FIELD",
        default="_threshold",
        help="Field name used to store triggered threshold labels (default: _threshold).",
    )
    parser.add_argument(
        "--threshold-only",
        action="store_true",
        default=False,
        help="Only emit records that trigger at least one threshold.",
    )


def apply_threshold_args(
    args: argparse.Namespace,
    records: Iterable[Dict[str, Any]],
) -> Iterator[Dict[str, Any]]:
    """Apply threshold rules from parsed CLI args to *records*.

    Returns the original iterator unchanged when no --threshold flags given.
    """
    raw_rules: List[str] = getattr(args, "thresholds", []) or []
    if not raw_rules:
        yield from records
        return

    rules = [parse_threshold_arg(r) for r in raw_rules]
    tag_field: str = getattr(args, "threshold_tag", "_threshold")
    only_triggered: bool = getattr(args, "threshold_only", False)

    yield from apply_thresholds(
        records,
        rules=rules,
        tag_field=tag_field,
        only_triggered=only_triggered,
    )
