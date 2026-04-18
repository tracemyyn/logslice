# Stats

The `logslice.stats` module computes numeric statistics over a chosen field
across a stream of parsed log records.

## Functions

### `collect_values(records, field)`

Iterates *records* and extracts the value of *field*, coercing each to
`float`. Records where the field is absent or non-numeric are silently
skipped.

```python
from logslice.stats import collect_values
vals = collect_values(records, "duration_ms")
```

### `compute_stats(values)`

Accepts a list of floats and returns a summary dict:

| Key | Description |
|--------|---------------------|
| count | number of samples |
| min | minimum value |
| max | maximum value |
| mean | arithmetic mean |
| stddev | population std dev |
| p50 | 50th percentile |
| p95 | 95th percentile |
| p99 | 99th percentile |

Returns `{"count": 0}` when *values* is empty.

### `field_stats(records, field)`

Convenience wrapper combining `collect_values` and `compute_stats`.

```python
from logslice.stats import field_stats
result = field_stats(records, "latency")
print(result["p95"])
```

## CLI integration

Pass `--stats <field>` to print a statistics table instead of individual
records (requires CLI wiring — see `cli.py`).
