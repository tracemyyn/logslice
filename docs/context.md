# Context Lines

The context-lines feature lets you include neighbouring log records around each
matching line — similar to `grep -A`, `-B`, and `-C`.

## CLI flags

| Flag | Long form | Description |
|------|-----------|-------------|
| `-B N` | `--before N` | Include *N* records **before** each match |
| `-A N` | `--after N` | Include *N* records **after** each match |
| `-C N` | `--context N` | Include *N* records both before **and** after each match |

## Example

```bash
# Show 2 lines of context around every ERROR record
logslice -f level=ERROR -C 2 app.log

# Show only the 3 records that follow each WARNING
logslice -f level=WARN -A 3 app.log
```

## Context markers

Records that are included purely as context (not because they matched the filter
themselves) carry an extra field `_context` set to `"before"` or `"after"`.
You can use this with the highlight module to dim context lines:

```python
from logslice.highlight import colorize

for record in results:
    role = record.get("_context")
    if role:
        print(colorize(str(record), "dim"))
    else:
        print(record)
```

## Python API

```python
from logslice.context import with_context

matched_records = [...]  # list of dicts
for rec in with_context(matched_records, before=2, after=2):
    print(rec)
```

`with_context` is a generator and works with any iterable of record dicts.
Each record is yielded at most once, so there are no duplicates even when
context windows overlap.
