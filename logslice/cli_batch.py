"""cli_batch.py — CLI glue for the batch module."""
from __future__ import annotations

import argparse
from typing import Iterable, Iterator, List, Optional

from logslice.batch import apply_batch, default_reducer

Record = dict


def add_batch_args(parser: argparse.ArgumentParser) -> None:
    """Register --batch-size and --batch-field flags on *parser*."""
    grp = parser.add_argument_group("batching")
    grp.add_argument(
        "--batch-size",
        metavar="N",
        type=int,
        default=None,
        help="Merge every N records into a single summary record.",
    )
    grp.add_argument(
        "--batch-field",
        metavar="FIELD",
        default=None,
        help="Start a new batch whenever FIELD changes value.",
    )


def apply_batch_args(
    records: Iterable[Record],
    args: argparse.Namespace,
) -> Iterator[Record]:
    """Apply batching according to parsed *args*.

    Returns an iterator of records; if no batching flags are set the original
    records are passed through without modification.
    """
    size: Optional[int] = getattr(args, "batch_size", None)
    field: Optional[str] = getattr(args, "batch_field", None)
    return apply_batch(records, size=size, field=field, reducer=default_reducer)
