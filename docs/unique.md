# `--unique` — deduplicate by field value

Emit only the **first** record for each distinct combination of one or more
field values.  Unlike `--dedup` (which compares whole records), `--unique`
lets you target specific fields.

## Usage

```
logslice [OPTIONS] FILE --unique FIELD [FIELD ...]
```

## Examples

### One unique request per user

```bash
logslice app.log --unique user_id
```

### First event per (service, level) pair

```bash
logslice app.log --unique svc level
```

## Behaviour

- Records are processed in stream order; the **first** record with a given
  key is emitted, all later duplicates are dropped.
- Fields that are absent from a record are treated as `null` for comparison
  purposes.
- When `--unique` is not supplied the flag is a no-op and all records pass
  through unchanged.

## Python API

```python
from logslice.unique import unique_by, count_unique

records = load_records("app.log")

for rec in unique_by(records, ["user_id"]):
    print(rec)

print("distinct users:", count_unique(records, ["user_id"]))
```

## Related

- `--dedup` – whole-record deduplication
- `--sort`  – sort before `--unique` to control which record wins
