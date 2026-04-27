"""CLI integration for the resample feature."""

from __future__ import annotations

import argparse
from typing import Iterable, Iterator

from logslice.resample import resample_records


def add_resample_args(parser: argparse.ArgumentParser) -> None:
    """Register ``--resample`` and related flags on *parser*."""
    parser.add_argument(
        "--resample",
        metavar="SECONDS",
        type=int,
        default=None,
        help="Resample records into fixed-width time buckets of SECONDS width.",
    )
    parser.add_argument(
        "--resample-fields",
        metavar="FIELD",
        nargs="+",
        default=None,
        dest="resample_fields",
        help="Numeric fields to aggregate (default: all numeric fields).",
    )
    parser.add_argument(
        "--resample-ts",
        metavar="FIELD",
        default="ts",
        dest="resample_ts",
        help="Timestamp field name (default: ts).",
    )


def apply_resample_args(
    args: argparse.Namespace,
    records: Iterable[dict],
) -> Iterator[dict]:
    """Apply resampling if ``--resample`` was requested.

    Returns an iterator of records unchanged when the flag is not set,
    or an iterator of bucket summary records when it is.
    """
    if not args.resample:
        yield from records
        return

    yield from resample_records(
        records,
        interval=args.resample,
        fields=args.resample_fields,
        ts_field=args.resample_ts,
    )
