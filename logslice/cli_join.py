"""CLI helpers for the join feature."""
import argparse
from typing import Dict, Iterable, Iterator, List, Optional

from logslice.join import apply_join
from logslice.parser import parse_line


def add_join_args(parser: argparse.ArgumentParser) -> None:
    """Register --join-file, --join-key, --join-how, --join-prefix flags."""
    parser.add_argument(
        "--join-file",
        metavar="FILE",
        help="Path to the file whose records are joined onto the input stream.",
    )
    parser.add_argument(
        "--join-key",
        metavar="FIELD",
        help="Field name used as the join key on both sides.",
    )
    parser.add_argument(
        "--join-how",
        choices=["inner", "left"],
        default="inner",
        help="Join strategy: 'inner' (default) or 'left'.",
    )
    parser.add_argument(
        "--join-prefix",
        default="right_",
        metavar="PREFIX",
        help="Prefix applied to fields from the right-hand file (default: 'right_').",
    )


def _load_right(path: str) -> List[Dict]:
    records: List[Dict] = []
    with open(path) as fh:
        for line in fh:
            rec = parse_line(line)
            if rec is not None:
                records.append(rec)
    return records


def apply_join_args(
    args: argparse.Namespace,
    records: Iterable[Dict],
) -> Iterable[Dict]:
    """Return *records* joined with --join-file when the flags are set."""
    if not getattr(args, "join_file", None) or not getattr(args, "join_key", None):
        return records
    right = _load_right(args.join_file)
    return apply_join(
        records,
        right,
        key=args.join_key,
        how=args.join_how,
        prefix=args.join_prefix,
    )
