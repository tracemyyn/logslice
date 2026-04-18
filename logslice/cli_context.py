"""CLI helpers for context-lines feature."""
import argparse
from typing import Iterable, Iterator

from logslice.context import with_context


def add_context_args(parser: argparse.ArgumentParser) -> None:
    """Register --before / --after / --context flags on *parser*."""
    grp = parser.add_argument_group("context lines")
    grp.add_argument(
        "-B", "--before",
        metavar="N",
        type=int,
        default=0,
        help="Include N lines of context before each match.",
    )
    grp.add_argument(
        "-A", "--after",
        metavar="N",
        type=int,
        default=0,
        help="Include N lines of context after each match.",
    )
    grp.add_argument(
        "-C", "--context",
        metavar="N",
        type=int,
        default=None,
        help="Include N lines of context before AND after each match.",
    )


def apply_context(
    records: Iterable[dict],
    args: argparse.Namespace,
) -> Iterator[dict]:
    """Apply context windowing based on parsed CLI *args*."""
    before = args.before
    after = args.after
    if getattr(args, "context", None) is not None:
        before = after = args.context
    if before == 0 and after == 0:
        yield from records
        return
    yield from with_context(records, before=before, after=after)
