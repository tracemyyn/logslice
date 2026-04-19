"""Full-text and regex grep across log record fields."""

import re
from typing import Iterable, Iterator, Optional, Pattern


def _compile(pattern: str, ignore_case: bool) -> Pattern:
    flags = re.IGNORECASE if ignore_case else 0
    return re.compile(pattern, flags)


def grep_record(
    record: dict,
    pattern: Pattern,
    fields: Optional[list] = None,
    invert: bool = False,
) -> bool:
    """Return True if record matches the pattern (or doesn't, if invert=True)."""
    targets = fields if fields else list(record.keys())
    for key in targets:
        value = record.get(key)
        if value is None:
            continue
        if pattern.search(str(value)):
            return not invert
    return invert


def grep_records(
    records: Iterable[dict],
    pattern: str,
    fields: Optional[list] = None,
    ignore_case: bool = False,
    invert: bool = False,
) -> Iterator[dict]:
    """Yield records whose fields match (or don't match) the given pattern."""
    compiled = _compile(pattern, ignore_case)
    for record in records:
        if grep_record(record, compiled, fields=fields, invert=invert):
            yield record


def add_grep_args(parser) -> None:
    """Register grep-related CLI arguments on an argparse parser."""
    parser.add_argument(
        "--grep",
        metavar="PATTERN",
        help="Keep records matching this regex pattern",
    )
    parser.add_argument(
        "--grep-fields",
        metavar="FIELD",
        nargs="+",
        help="Restrict grep to these fields (default: all fields)",
    )
    parser.add_argument(
        "--grep-ignore-case",
        action="store_true",
        default=False,
        help="Case-insensitive grep",
    )
    parser.add_argument(
        "--grep-invert",
        action="store_true",
        default=False,
        help="Invert match — keep records that do NOT match",
    )


def apply_grep(records: Iterable[dict], args) -> Iterable[dict]:
    """Apply grep filtering based on parsed CLI args."""
    if not args.grep:
        return records
    return grep_records(
        records,
        pattern=args.grep,
        fields=args.grep_fields,
        ignore_case=args.grep_ignore_case,
        invert=args.grep_invert,
    )
