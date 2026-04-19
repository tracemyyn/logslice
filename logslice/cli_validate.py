"""CLI integration for record validation."""
from __future__ import annotations

import argparse
from typing import Any, List, Optional

from logslice.validate import apply_validation, parse_rule_arg


def add_validate_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--validate",
        metavar="RULE",
        action="append",
        default=[],
        help="Validation rule: 'field' (required), 'field:type', or 'field~pattern'",
    )
    parser.add_argument(
        "--drop-invalid",
        action="store_true",
        default=False,
        help="Drop records that fail validation instead of passing them through",
    )
    parser.add_argument(
        "--tag-errors",
        metavar="FIELD",
        default=None,
        help="Attach validation errors to this field on each record",
    )


def apply_validate(
    records: List[Any],
    args: argparse.Namespace,
) -> List[Any]:
    if not args.validate:
        return records
    rules = [parse_rule_arg(r) for r in args.validate]
    result, _ = apply_validation(
        records,
        rules,
        drop_invalid=args.drop_invalid,
        tag_field=args.tag_errors,
    )
    return result
