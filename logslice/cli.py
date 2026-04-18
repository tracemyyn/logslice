"""Command-line interface for logslice."""
from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from logslice.field_filter import apply_filters, parse_filter_arg
from logslice.output import write_record
from logslice.parser import parse_line
from logslice.sampler import reservoir_sample, sample_records
from logslice.time_filter import extract_timestamp, in_range


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="logslice",
        description="Filter and slice structured log files.",
    )
    p.add_argument("file", nargs="?", help="Log file (default: stdin)")
    p.add_argument("--start", help="Start time (ISO-8601)")
    p.add_argument("--end", help="End time (ISO-8601)")
    p.add_argument("-f", "--filter", dest="filters", action="append", default=[])
    p.add_argument("--format", dest="fmt", default="json",
                   choices=["json", "logfmt", "pretty"])
    p.add_argument("--count", action="store_true", help="Print match count only")
    p.add_argument("--sample", type=float, default=None,
                   help="Sampling rate (0, 1]")
    p.add_argument("--sample-field", default=None,
                   help="Field for deterministic sampling")
    p.add_argument("--reservoir", type=int, default=None,
                   help="Reservoir sample: keep exactly N records")
    return p


def run(argv: Optional[List[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    fh = open(args.file) if args.file else sys.stdin

    try:
        filters = [parse_filter_arg(f) for f in args.filters]

        records = []
        for raw in fh:
            record = parse_line(raw)
            if record is None:
                continue
            ts = extract_timestamp(record)
            if not in_range(ts, args.start, args.end):
                continue
            if not apply_filters(record, filters):
                continue
            records.append(record)

        # Apply sampling
        if args.reservoir is not None:
            records = reservoir_sample(iter(records), k=args.reservoir)
        elif args.sample is not None:
            records = list(
                sample_records(
                    iter(records),
                    rate=args.sample,
                    field=args.sample_field,
                )
            )

        if args.count:
            print(len(records))
            return

        for record in records:
            write_record(record, fmt=args.fmt)
    finally:
        if args.file:
            fh.close()


def main() -> None:  # pragma: no cover
    run()
