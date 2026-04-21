"""CLI integration for the scoring feature."""
from __future__ import annotations

import argparse
from typing import Any, Dict, Iterable, Iterator, Optional

from logslice.score import build_rules, score_records

Record = Dict[str, Any]


def add_score_args(parser: argparse.ArgumentParser) -> None:
    """Register --score, --score-threshold and --score-field flags."""
    parser.add_argument(
        "--score",
        metavar="FIELD:PATTERN[:WEIGHT]",
        action="append",
        default=[],
        help=(
            "Score records by matching PATTERN in FIELD, weighted by WEIGHT "
            "(default 1.0). May be repeated. Records are annotated with their "
            "cumulative score."
        ),
    )
    parser.add_argument(
        "--score-threshold",
        metavar="NUM",
        type=float,
        default=0.0,
        help="Only emit records whose score is >= NUM (default: 0.0).",
    )
    parser.add_argument(
        "--score-field",
        metavar="NAME",
        default="_score",
        help="Name of the field added to each record (default: _score).",
    )


def apply_score_args(
    args: argparse.Namespace,
    records: Iterable[Record],
) -> Iterator[Record]:
    """Apply scoring if --score flags are present; otherwise pass through."""
    if not args.score:
        yield from records
        return

    rules = build_rules(args.score)
    yield from score_records(
        records,
        rules,
        threshold=args.score_threshold,
        score_field=args.score_field,
    )
