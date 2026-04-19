"""CLI integration for window aggregation."""
from __future__ import annotations

import argparse
from typing import Iterable, Iterator

from logslice.window import tumbling_windows, sliding_windows, window_counts


def add_window_args(parser: argparse.ArgumentParser) -> None:
    """Register window-related flags on *parser*."""
    grp = parser.add_argument_group("windowing")
    grp.add_argument(
        "--window",
        metavar="SECONDS",
        type=int,
        default=None,
        help="tumbling window width in seconds",
    )
    grp.add_argument(
        "--window-step",
        metavar="SECONDS",
        type=int,
        default=None,
        dest="window_step",
        help="sliding window step; requires --window",
    )
    grp.add_argument(
        "--window-field",
        metavar="FIELD",
        default=None,
        dest="window_field",
        help="count distinct values of FIELD within each window",
    )


def apply_window(
    records: Iterable[dict],
    args: argparse.Namespace,
) -> Iterator[dict]:
    """Apply window aggregation if requested; otherwise pass records through."""
    if args.window is None:
        yield from records
        return

    if args.window_step is not None:
        windows = sliding_windows(records, args.window, args.window_step)
    else:
        windows = tumbling_windows(records, args.window)

    yield from window_counts(windows, field=args.window_field)
