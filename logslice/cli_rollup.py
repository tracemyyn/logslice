"""cli_rollup.py – CLI glue for the rollup feature."""
from __future__ import annotations

import argparse
from typing import Iterable, Iterator

from logslice.rollup import rollup_records


def add_rollup_args(parser: argparse.ArgumentParser) -> None:
    """Register rollup-related flags on *parser*."""
    grp = parser.add_argument_group("rollup")
    grp.add_argument(
        "--rollup",
        metavar="FIELD",
        help="aggregate FIELD into time buckets",
    )
    grp.add_argument(
        "--rollup-interval",
        metavar="SECONDS",
        type=int,
        default=60,
        help="bucket width in seconds (default: 60)",
    )
    grp.add_argument(
        "--rollup-op",
        metavar="OP",
        default="sum",
        choices=["sum", "avg", "min", "max", "count"],
        help="aggregation operation (default: sum)",
    )
    grp.add_argument(
        "--rollup-ts",
        metavar="FIELD",
        default="ts",
        help="timestamp field name (default: ts)",
    )


def apply_rollup_args(
    args: argparse.Namespace,
    records: Iterable[dict],
) -> Iterator[dict]:
    """If ``--rollup`` was requested, replace *records* with rollup output."""
    if not getattr(args, "rollup", None):
        yield from records
        return
    yield from rollup_records(
        records,
        interval=args.rollup_interval,
        agg_field=args.rollup,
        ts_field=args.rollup_ts,
        operation=args.rollup_op,
    )
