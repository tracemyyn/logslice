"""CLI helpers for the --frequency feature."""

from __future__ import annotations

import argparse
from typing import Iterator

from .frequency import iter_frequency


def add_frequency_args(parser: argparse.ArgumentParser) -> None:
    """Register frequency-related flags on *parser*."""
    grp = parser.add_argument_group("frequency")
    grp.add_argument(
        "--freq",
        metavar="FIELD",
        default=None,
        help="emit a frequency table for FIELD instead of raw records",
    )
    grp.add_argument(
        "--freq-top",
        metavar="N",
        type=int,
        default=None,
        help="limit frequency table to top N values",
    )
    grp.add_argument(
        "--freq-asc",
        action="store_true",
        default=False,
        help="sort frequency table least-frequent first",
    )


def apply_frequency_args(
    args: argparse.Namespace,
    records: Iterator[dict],
) -> Iterator[dict] | None:
    """Return a frequency iterator when --freq is set, else None.

    Returning None signals the caller that normal record output should proceed.
    """
    if not getattr(args, "freq", None):
        return None
    return iter_frequency(
        records,
        field=args.freq,
        top=getattr(args, "freq_top", None),
        ascending=getattr(args, "freq_asc", False),
    )
