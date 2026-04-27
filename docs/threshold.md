# Threshold Alerting

The `threshold` module lets you flag or filter log records when a numeric
field crosses a boundary. It is useful for surfacing latency spikes, error
rate anomalies, or any measurable signal embedded in your logs.

## Supported operators

| Operator | Meaning            |
|----------|--------------------|
| `gt`     | greater than       |
| `gte`    | greater than or equal |
| `lt`     | less than          |
| `lte`    | less than or equal |
| `eq`     | equal              |
| `ne`     | not equal          |

## CLI flags

```
--threshold FIELD:OP:VALUE
```

May be repeated to apply multiple rules. Each triggered rule is recorded
in the output record under a tag field.

```
--threshold-tag FIELD   Field used to store triggered labels (default: _threshold)
--threshold-only        Only emit records that trigger at least one rule
```

## Examples

### Flag slow requests

```bash
logslice app.log --threshold ms:gt:500
```

Records where `ms > 500` will gain a `_threshold` field:

```json
{"ts": "2024-01-01T12:00:00Z", "ms": 750, "_threshold": "ms:gt:500"}
```

### Only emit records above threshold

```bash
logslice app.log --threshold ms:gt:500 --threshold-only
```

### Combine multiple rules

```bash
logslice app.log --threshold ms:gt:500 --threshold error_rate:gte:0.05
```

Both conditions are evaluated independently; a record may carry labels
for more than one triggered rule, comma-separated.

### Custom tag field

```bash
logslice app.log --threshold ms:gt:500 --threshold-tag alert
```

## Python API

```python
from logslice.threshold import apply_thresholds, parse_threshold_arg

rules = [parse_threshold_arg("ms:gt:500")]
for record in apply_thresholds(records, rules, only_triggered=True):
    print(record)
```
