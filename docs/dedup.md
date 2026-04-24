# Deduplication

`logslice` can remove duplicate log lines from a stream using the `--dedup` family of flags.

## Flags

| Flag | Description |
|---|---|
| `--dedup` | Remove exact duplicate records (all fields must match). |
| `--dedup-fields FIELD [FIELD ...]` | Use only the specified fields as the dedup key. |
| `--dedup-keep {first,last}` | Which occurrence to retain (default: `first`). |

## Examples

### Remove exact duplicates

```bash
logslice app.log --dedup
```

### Deduplicate by selected fields

Keep only the first record sharing the same `level` and `msg`:

```bash
logslice app.log --dedup-fields level msg
```

### Keep the last occurrence

Useful when later records contain updated context:

```bash
logslice app.log --dedup-fields request_id --dedup-keep last
```

### Combine with time filters

Deduplicate error messages within a specific time window:

```bash
logslice app.log --start 2024-01-15T08:00:00 --end 2024-01-15T09:00:00 --dedup-fields level msg
```

## Notes

- `--dedup` (exact) and `--dedup-fields` can be combined; when `--dedup-fields` is
  provided it takes precedence as the key definition.
- `--dedup-keep last` buffers all records in memory. For very large files prefer
  `--dedup-keep first` (the default) which streams with O(n) memory in keys only.
- Deduplication runs **after** time and field filters, so only matching records
  are considered.
- If a field specified in `--dedup-fields` is missing from a record, that record
  is treated as having `null` for that field when computing the dedup key.
