# Column Selection and Reordering

The `--columns`, `--exclude-columns`, and `--reorder` flags let you control which fields appear in output and in what order.

## Flags

| Flag | Description |
|------|-------------|
| `--columns FIELD [FIELD ...]` | Keep only the listed fields, in the given order |
| `--exclude-columns FIELD [FIELD ...]` | Remove the listed fields from every record |
| `--reorder FIELD [FIELD ...]` | Move listed fields to the front; remaining fields follow |

Flags may be combined. `--columns` is applied first, then `--exclude-columns`, then `--reorder`.

## Examples

### Select specific columns

```bash
logslice app.log --columns ts level msg
```

Output records will contain only `ts`, `level`, and `msg` in that order.

### Exclude noisy fields

```bash
logslice app.log --exclude-columns trace_id span_id
```

### Bring important fields to the front

```bash
logslice app.log --reorder msg level
```

`msg` and `level` will appear first; all other fields follow in their original order.

### Combined usage

```bash
logslice app.log --columns ts level msg host --reorder msg
```

Select four fields, then move `msg` to position 0.

## Python API

```python
from logslice.column import select_columns, exclude_columns, reorder_columns, apply_column_args

record = {"ts": "...", "level": "info", "msg": "hello", "host": "web1"}

# Keep only two fields
print(select_columns(record, ["ts", "msg"]))

# Remove a field
print(exclude_columns(record, ["host"]))

# Reorder
print(reorder_columns(record, ["msg", "ts"]))

# Apply all at once to a list of records
results = apply_column_args(records, select=["ts", "msg"], reorder=["msg"])
```
