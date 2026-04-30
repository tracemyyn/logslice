"""CLI helpers for the --merge feature."""

from __future__ import annotations

import argparse
from typing import Iterator, List

from logslice.merge import apply_merge
from logslice.parser import parse_line


def add_merge_args(parser: argparse.ArgumentParser) -> None:
    """Register merge-related flags on *parser*."""
    parser.add_argument(
        "--merge",
        metavar="FILE",
        nargs="+",
        default=None,
        help="Additional log files to merge into the output stream.",
    )
    parser.add_argument(
        "--merge-no-sort",
        action="store_true",
        default=False,
        help="Interleave merged files without sorting by timestamp.",
    )
    parser.add_argument(
        "--merge-ts-field",
        metavar="FIELD",
        default="ts",
        help="Timestamp field used when sorting merged streams (default: ts).",
    )


def _load_file(path: str) -> List[dict]:
    records: List[dict] = []
    with open(path, "r", encoding="utf-8") as fh:
        for raw in fh:
            rec = parse_line(raw)
            if rec is not None:
                records.append(rec)
    return records


def apply_merge_args(
    args: argparse.Namespace,
    primary: List[dict],
) -> Iterator[dict]:
    """If --merge flags are present, merge additional files with *primary*.

    Returns an iterator over the combined records.
    """
    if not getattr(args, "merge", None):
        return iter(primary)

    streams = [primary] + [_load_file(p) for p in args.merge]
    sort = not getattr(args, "merge_no_sort", False)
    ts_field = getattr(args, "merge_ts_field", "ts")
    return apply_merge(streams, sort=sort, ts_field=ts_field)
