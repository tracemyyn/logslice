# Window Aggregation

`logslice` can group log records into time-based windows and emit per-window
counts or value breakdowns.

## Tumbling windows

Non-overlapping fixed-width buckets:

```bash
logslice app.log --window 60
```

Outputs one record per minute with a `count` field.

## Sliding windows

Overlapping windows that advance by a step:

```bash
logslice app.log --window 90 --window-step 30
```

Each window is 90 seconds wide and starts every 30 seconds.

## Count by field

Break down each window by a field value:

```bash
logslice app.log --window 60 --window-field level
```

Output records contain `window_start`, `value`, and `count`.

## Output fields

| Field | Description |
|---|---|
| `window_start` | ISO-8601 timestamp of window start |
| `count` | number of matching records |
| `value` | field value (only with `--window-field`) |

## Notes

- Records without a parseable timestamp are silently skipped.
- Windows are aligned to Unix epoch boundaries.
- `--window-step` requires `--window`.
- Output is sorted chronologically.
