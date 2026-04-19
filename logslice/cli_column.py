"""CLI argument handling for column selection and reordering."""
import argparse
from typing import List, Optional
from logslice.column import apply_column_args


def add_column_args(parser: argparse.ArgumentParser) -> None:
    """Register column-related flags on an ArgumentParser."""
    parser.add_argument(
        "--columns",
        metavar="FIELD",
        nargs="+",
        default=None,
        help="Select only these columns (in given order).",
    )
    parser.add_argument(
        "--exclude-columns",
        metavar="FIELD",
        nargs="+",
        default=None,
        dest="exclude_columns",
        help="Exclude these columns from output.",
    )
    parser.add_argument(
        "--reorder",
        metavar="FIELD",
        nargs="+",
        default=None,
        help="Place these columns first, followed by remaining fields.",
    )


def apply_column_cli(args: argparse.Namespace, records: list) -> list:
    """Apply column args from parsed CLI namespace to records."""
    select: Optional[List[str]] = getattr(args, "columns", None)
    exclude: Optional[List[str]] = getattr(args, "exclude_columns", None)
    reorder: Optional[List[str]] = getattr(args, "reorder", None)
    if not any([select, exclude, reorder]):
        return records
    return apply_column_args(records, select=select, exclude=exclude, reorder=reorder)
