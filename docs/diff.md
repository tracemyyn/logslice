# Diff / Change Detection

The `--diff` feature annotates consecutive log records with the fields that
changed between them, making it easy to spot state transitions in a log stream.

## Flags

| Flag | Description |
|------|-------------|
| `--diff` | Annotate every record with a `_changed` list of field names. |
| `--diff-fields FIELD [FIELD ...]` | Limit change detection to specific fields. |
| `--diff-only` | Output **only** records where at least one tracked field changed. |

## How it works

Each output record gains a `_changed` key containing the names of fields whose
value differs from the **previous** record.  The very first record always
receives an empty list because there is nothing to compare it against.

When `--diff-only` is used the first record is always suppressed.

## Examples

```bash
# Annotate all records with changed fields
logslice app.log --diff

# Show only records where 'level' or 'code' changed
logslice app.log --diff-only --diff-fields level code
```

## Output example

```json
{"ts":"2024-01-02T10:00:01Z","level":"error","msg":"failed","_changed":["level","msg"]}
```

The `_changed` field is injected at output time and does **not** affect
field-filter or redaction steps that run before diff annotation.
