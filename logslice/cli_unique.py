"""cli_unique.py – argparse integration for the --unique feature."""
from __future__ import annotations

import argparse
from typing import Iterable, List

from logslice.unique import apply_unique


def add_unique_args(parser: argparse.ArgumentParser) -> None:
    """Register --unique flag on *parser*."""
    parser.add_argument(
        "--unique",
        metavar="FIELD",
        dest="unique_fields",
        nargs="+",
        default=None,
        help=(
            "Emit only the first record for each distinct combination of FIELD "
            "values.  Multiple fields may be supplied."
        ),
    )


def apply_unique_args(
    args: argparse.Namespace,
    records: Iterable[dict],
) -> Iterable[dict]:
    """Return *records* filtered by uniqueness according to *args*."""
    fields: List[str] = args.unique_fields or []
    return apply_unique(records, fields)
