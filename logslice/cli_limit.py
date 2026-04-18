"""CLI helpers for --limit and --offset flags."""
import argparse
from typing import Iterable, Iterator

from logslice.limit import apply_limit


def add_limit_args(parser: argparse.ArgumentParser) -> None:
    """Register --limit and --offset arguments on *parser*."""
    parser.add_argument(
        "--limit",
        metavar="N",
        type=int,
        default=0,
        help="Stop after emitting N records (0 = no limit).",
    )
    parser.add_argument(
        "--offset",
        metavar="N",
        type=int,
        default=0,
        help="Skip the first N records before applying limit (0 = no skip).",
    )


def apply_limit_args(args: argparse.Namespace, records: Iterable[dict]) -> Iterator[dict]:
    """Apply limit/offset from parsed *args* to *records*.

    Returns the original iterator unchanged when neither flag is set.
    """
    limit: int = getattr(args, "limit", 0) or 0
    offset: int = getattr(args, "offset", 0) or 0
    if limit == 0 and offset == 0:
        yield from records
        return
    yield from apply_limit(records, offset=offset, limit=limit)
