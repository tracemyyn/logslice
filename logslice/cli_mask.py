"""CLI integration for field masking."""

import argparse
from typing import List, Dict, Any, Optional

from logslice.mask import apply_masks, _PRESETS


def add_mask_args(parser: argparse.ArgumentParser) -> None:
    """Register --mask and --mask-preset flags on *parser*."""
    parser.add_argument(
        "--mask",
        metavar="FIELD:REGEX",
        action="append",
        default=[],
        help="Mask FIELD using REGEX (matched portion replaced with '*').",
    )
    parser.add_argument(
        "--mask-preset",
        metavar="FIELD:PRESET",
        action="append",
        default=[],
        help=f"Mask FIELD using a named preset. Presets: {list(_PRESETS)}.",
    )
    parser.add_argument(
        "--mask-char",
        default="*",
        help="Replacement character for masked portions (default: '*').",
    )


def _parse_mask_args(args: argparse.Namespace) -> List[Dict[str, Any]]:
    specs: List[Dict[str, Any]] = []
    char = getattr(args, "mask_char", "*")
    for item in getattr(args, "mask", []) or []:
        field, _, pattern = item.partition(":")
        if not field or not pattern:
            raise ValueError(f"--mask requires FIELD:REGEX, got: {item!r}")
        specs.append({"field": field, "pattern": pattern, "char": char})
    for item in getattr(args, "mask_preset", []) or []:
        field, _, preset = item.partition(":")
        if not field or not preset:
            raise ValueError(f"--mask-preset requires FIELD:PRESET, got: {item!r}")
        specs.append({"field": field, "preset": preset, "char": char})
    return specs


def apply_mask_args(
    records: List[Dict[str, Any]],
    args: argparse.Namespace,
) -> List[Dict[str, Any]]:
    specs = _parse_mask_args(args)
    if not specs:
        return records
    return apply_masks(records, specs)
