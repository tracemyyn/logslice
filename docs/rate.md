# Rate

The `rate` module computes per-time-bucket event rates from a stream of log
records, useful for spotting traffic spikes or quiet periods.

## Functions

### `compute_rate(records, interval=60, ts_field=None)`

Groups records into fixed-width time buckets and returns a list of summary
rows sorted by bucket start time.

| Parameter   | Type            | Default | Description                              |
|-------------|-----------------|---------|------------------------------------------|
| `records`   | `Iterable[dict]`| —       | Parsed log records                       |
| `interval`  | `int`           | `60`    | Bucket width in seconds                  |
| `ts_field`  | `str \| None`   | `None`  | Override timestamp field (default: `ts`) |

Each returned dict contains:

- `bucket` — Unix timestamp of the bucket start
- `count`  — Number of events in the bucket
- `rate`   — Events per second (`count / interval`)

Records without a parseable timestamp are silently skipped.

### `peak_bucket(rate_rows)`

Returns the row with the highest `count`, or `None` for an empty list.

## Example

```python
from logslice.rate import compute_rate, peak_bucket

rows = compute_rate(records, interval=300)  # 5-minute buckets
peak = peak_bucket(rows)
print(f"Peak: {peak['count']} events in bucket starting {peak['bucket']}")
```

## Notes

- `interval` must be a positive integer; a `ValueError` is raised otherwise.
- Bucket boundaries are aligned to Unix epoch (e.g. every 60 s from 00:00:00 UTC).
