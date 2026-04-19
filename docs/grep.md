# Grep

The `grep` module provides full-text and regex search across structured log record fields.

## Functions

### `grep_records(records, pattern, fields=None, ignore_case=False, invert=False)`

Yields records whose field values match the given regex `pattern`.

- `fields` — restrict matching to a subset of field names; defaults to all fields.
- `ignore_case` — perform case-insensitive matching.
- `invert` — yield records that do **not** match (like `grep -v`).

### `grep_record(record, pattern, fields=None, invert=False)`

Returns `True` if a single record matches the compiled pattern.

## CLI Flags

| Flag | Description |
|---|---|
| `--grep PATTERN` | Keep records matching this regex |
| `--grep-fields FIELD [FIELD ...]` | Restrict search to these fields |
| `--grep-ignore-case` | Case-insensitive matching |
| `--grep-invert` | Invert — keep non-matching records |

## Examples

```bash
# Find all records mentioning "timeout"
logslice app.log --grep timeout

# Case-insensitive search in the msg field only
logslice app.log --grep error --grep-fields msg --grep-ignore-case

# Exclude debug records
logslice app.log --grep debug --grep-fields level --grep-invert
```

## Notes

- Patterns are standard Python `re` regular expressions.
- Non-string field values are coerced to strings before matching.
- Missing fields are silently skipped.
