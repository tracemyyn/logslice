"""CLI helpers for --template output formatting."""
from __future__ import annotations
import argparse
from typing import Any

from logslice.template import compile_template


def add_template_args(parser: argparse.ArgumentParser) -> None:
    """Register --template flag on *parser*."""
    parser.add_argument(
        "--template",
        metavar="TMPL",
        default=None,
        help=(
            "Output each record using a template string. "
            "Reference fields as {field} or {field:default}. "
            "Example: '{ts} [{level}] {msg}'"
        ),
    )


def apply_template(
    args: argparse.Namespace,
    records: list[dict[str, Any]],
) -> list[str] | None:
    """If --template is set, render each record and return the lines.

    Returns *None* when no template is configured so the caller can
    fall back to its normal output path.
    """
    tmpl: str | None = getattr(args, "template", None)
    if not tmpl:
        return None
    render = compile_template(tmpl)
    return [render(r) for r in records]
