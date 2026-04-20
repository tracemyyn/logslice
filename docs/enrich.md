# Field Enrichment (`--enrich`)

The `--enrich` flag lets you derive new fields from existing record values
without modifying the original data. Multiple rules can be chained and are
applied in order.

## Syntax

```
--enrich kind:destination_field:source_or_value[:extra]
```

## Kinds

### `static` — add a constant value

Adds a hard-coded value as a new field. Does not overwrite an existing field.

```bash
logslice --enrich static:env:production app.log
```

### `copy` — copy one field to another

Copies the value of an existing field into a new field name.

```bash
logslice --enrich copy:svc:service app.log
```

### `extract` — extract via regex

Applies a regular-expression pattern to the source field and writes the first
capturing group (or the full match when no group is defined) into the
destination field.

```bash
# Extract HTTP status code from a message field
logslice --enrich 'extract:code:message:(\d{3})' app.log
```

### `concat` — concatenate multiple fields

Joins two or more fields with a separator (default: space) into a new field.
Missing source fields are silently skipped.

```bash
logslice --enrich concat:request_id:host:pid app.log
```

## Chaining Rules

Multiple `--enrich` flags are applied in the order they are specified:

```bash
logslice \
  --enrich static:env:production \
  --enrich copy:svc:service \
  --enrich 'extract:code:msg:(\d{3})' \
  app.log
```

## Notes

- Enrichment never overwrites an existing field with the same name.
- The original record is not mutated; a new dict is produced for each step.
- Rules that cannot be applied (e.g. missing source field) are silently skipped.
