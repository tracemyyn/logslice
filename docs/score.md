# Score

The `--score` flag annotates each log record with a numeric relevance score
based on weighted field-pattern matches. Records that fall below a configurable
threshold are dropped.

## Usage

```
logslice --score FIELD:PATTERN[:WEIGHT] \
         --score-threshold NUM \
         --score-field NAME \
         <file>
```

| Flag | Default | Description |
|---|---|---|
| `--score FIELD:PATTERN[:WEIGHT]` | — | Add a scoring rule. May be repeated. |
| `--score-threshold NUM` | `0.0` | Minimum score to emit a record. |
| `--score-field NAME` | `_score` | Field name written to each record. |

## How scoring works

Each `--score` rule contributes its *weight* (default `1.0`) to a record's
total score when `PATTERN` (a case-insensitive regular expression) matches
the string representation of `FIELD`'s value.

Rules are additive — a record matching three rules with weights 1, 2, and 3
receives a score of 6.

## Examples

### Flag errors and timeouts

```bash
logslice app.log \
  --score level:error:3 \
  --score msg:timeout:2 \
  --score-threshold 2
```

Only records scoring ≥ 2 are printed. Each matching record gains a `_score`
field showing its total.

### Custom score field

```bash
logslice app.log --score level:warn --score-field relevance
```

The injected field is named `relevance` instead of `_score`.

### Combine with `--format pretty`

```bash
logslice app.log \
  --score level:error:5 \
  --score msg:"connection refused":3 \
  --score-threshold 5 \
  --format pretty
```

## Notes

- Weights must be strictly positive.
- `PATTERN` is matched with `re.search`, so partial matches count.
- Records whose score equals the threshold are **included**.
- The `_score` field is added after all other transforms, so it will not
  interfere with field filters or redactions applied earlier in the pipeline.
