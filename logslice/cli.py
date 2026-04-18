"""Command-line interface for logslice."""

import sys
import argparse
from typing import Optional, List

from logslice.parser import parse_line
from logslice.time_filter import extract_timestamp, in_range
from logslice.field_filter import apply_filters, parse_filter_arg
from logslice.output import write_record


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="logslice",
        description="Filter and slice structured log files by time range and field patterns.",
    )
    p.add_argument("file", nargs="?", help="Log file to read (default: stdin)")
    p.add_argument("--start", metavar="TIME", help="Include records at or after this time")
    p.add_argument("--end", metavar="TIME", help="Include records at or before this time")
    p.add_argument(
        "--filter", "-f",
        metavar="FIELD=PATTERN",
        action="append",
        dest="filters",
        default=[],
        help="Field filter as field=pattern (repeatable)",
    )
    p.add_argument(
        "--output", "-o",
        choices=["json", "logfmt", "pretty"],
        default="json",
        help="Output format (default: json)",
    )
    p.add_argument(
        "--count", "-c",
        action="store_true",
        help="Print count of matched records instead of records",
    )
    return p


def run(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    filters = [parse_filter_arg(f) for f in args.filters]

    if args.file:
        try:
            stream = open(args.file, "r", encoding="utf-8")
        except OSError as exc:
            print(f"logslice: {exc}", file=sys.stderr)
            return 1
    else:
        stream = sys.stdin

    matched = 0
    try:
        for raw_line in stream:
            record = parse_line(raw_line)
            if record is None:
                continue
            ts = extract_timestamp(record)
            if not in_range(ts, args.start, args.end):
                continue
            if not apply_filters(record, filters):
                continue
            matched += 1
            if not args.count:
                write_record(record, fmt=args.output)
    finally:
        if args.file:
            stream.close()

    if args.count:
        print(matched)
    return 0


def main() -> None:
    sys.exit(run())
