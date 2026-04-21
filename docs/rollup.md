# Rollup

The **rollup** feature aggregates numeric fields across fixed-width time buckets,
producing one summary record per bucket.

## CLI flags

| Flag | Default | Description |
|------|---------|-------------|
| `--rollup FIELD` | *(off)* | Enable rollup; aggregate `FIELD` |
| `--rollup-interval SECONDS` | `60` | Bucket width in seconds |
| `--rollup-op OP` | `sum` | Aggregation: `sum`, `avg`, `min`, `max`, `count` |
| `--rollup-ts FIELD` | `ts` | Timestamp field used for bucketing |

## Output record schema

Each emitted record contains:

```json
{
  "bucket": "2024-01-15T12:00:00+00:00",
  "count":  42,
  "field":  "latency",
  "operation": "avg",
  "value": 123.4
}
```

- **bucket** – ISO-8601 timestamp of the bucket's start.
- **count** – number of input records that contributed to this bucket.
- **value** – aggregated result.

## Examples

### Sum latency per minute

```bash
logslice app.log --rollup latency
```

### Average latency in 5-minute windows

```bash
logslice app.log --rollup latency --rollup-interval 300 --rollup-op avg
```

### Count events per hour

```bash
logslice app.log --rollup latency --rollup-interval 3600 --rollup-op count
```

## Notes

- Records missing the timestamp field or the target numeric field are silently
  skipped.
- Buckets are emitted in ascending chronological order.
- The output can be piped into `--format json` or `--format pretty` like any
  other logslice output.
