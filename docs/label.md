# Label

The `label` feature adds computed string fields to each record based on
pattern-matching rules applied to existing fields.

## How it works

Each rule has the form:

```
dest_field:src_field:regex_pattern:label_value
```

For every record, rules are evaluated in order.  The **first** rule whose
`regex_pattern` matches the value of `src_field` sets `dest_field` to
`label_value`.  Subsequent rules for the same `dest_field` are skipped.

If no rule matches and `--label-default` is provided, `dest_field` is set to
the default value.

## CLI flags

| Flag | Description |
|---|---|
| `--label DEST:SRC:PATTERN:VALUE` | Add a label rule (repeatable) |
| `--label-default VALUE` | Fallback label when no rule matches |

## Examples

Tag records by severity:

```bash
logslice app.log \
  --label tier:level:error:high \
  --label tier:level:warn:medium \
  --label-default low
```

Classify requests by path prefix:

```bash
logslice access.log \
  --label area:path:^/api:backend \
  --label area:path:^/static:assets \
  --label-default other \
  --output json
```

## Python API

```python
from logslice.label import label_records, parse_label_args

rules = parse_label_args([
    "tier:level:error:high",
    "tier:level:warn:medium",
])

for record in label_records(records, rules, default="low"):
    print(record)
```
