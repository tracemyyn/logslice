# join

Enrich log records by joining them with a second log file on a shared field.

## Flags

| Flag | Description |
|---|---|
| `--join-file FILE` | Path to the right-hand log file. |
| `--join-key FIELD` | Field used as the join key on both sides. |
| `--join-how inner\|left` | Join strategy (default: `inner`). |
| `--join-prefix PREFIX` | Prefix for fields from the right file (default: `right_`). |

## Strategies

### inner (default)

Only records whose key value appears in **both** files are emitted.

```
logslice app.log --join-file meta.log --join-key request_id
```

### left

All records from the primary file are emitted. Where a match exists in the
right file the extra fields are merged in; otherwise the record is passed
through unchanged.

```
logslice app.log --join-file meta.log --join-key request_id --join-how left
```

## Field naming

Fields from the right file are prefixed with `right_` by default to avoid
collisions. Use `--join-prefix` to change this:

```
logslice app.log --join-file meta.log --join-key id --join-prefix meta_
```

## Notes

- The right file is loaded fully into memory before streaming begins.
- Records missing the join key on either side are silently skipped (inner)
  or passed through unmodified (left).
- Multiple right-side matches for the same key produce one output record per
  match, mirroring SQL join semantics.
