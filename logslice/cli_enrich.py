"""CLI integration for the enrich module."""

from __future__ import annotations

import argparse
from typing import Any, Dict, Iterable, List

from logslice.enrich import apply_enrichments, parse_enrich_arg, EnrichRule

Record = Dict[str, Any]


def add_enrich_args(parser: argparse.ArgumentParser) -> None:
    """Register --enrich flags on *parser*."""
    parser.add_argument(
        "--enrich",
        metavar="RULE",
        action="append",
        default=[],
        help=(
            "Enrich records with derived fields. "
            "Format: kind:dst:src_or_value[:extra]. "
            "Kinds: static, copy, extract, concat. "
            "Example: --enrich static:env:production "
            "         --enrich copy:svc:service "
            "         --enrich extract:code:message:(\\d{3}) "
            "         --enrich concat:full_id:host:pid"
        ),
    )


def apply_enrich_args(
    records: Iterable[Record], args: argparse.Namespace
) -> Iterable[Record]:
    """Apply enrichments from parsed CLI *args* to *records*.

    Returns *records* unchanged when no --enrich flags were supplied.
    """
    raw: List[str] = getattr(args, "enrich", []) or []
    if not raw:
        return records
    rules: List[EnrichRule] = [parse_enrich_arg(r) for r in raw]
    return apply_enrichments(records, rules)
