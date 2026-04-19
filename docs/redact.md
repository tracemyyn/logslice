# Redact

The `redact` module lets you mask sensitive data in log records before
displaying or forwarding them.

## Functions

### `redact_fields(record, fields)`

Returns a copy of `record` with each key in `fields` replaced by `***`.

```python
from logslice.redact import redact_fields

out = redact_fields({"user": "alice", "token": "s3cr3t"}, ["token"])
# {"user": "alice", "token": "***"}
```

### `redact_pattern(record, pattern, replacement="***")`

Returns a copy of `record` where every string value whose content matches
`pattern` (a regular expression) has the matching portion replaced.

```python
from logslice.redact import redact_pattern

out = redact_pattern({"msg": "token=abc123"}, r"token=\w+")
# {"msg": "***"}
```

### `apply_redactions(records, fields=None, pattern=None, replacement="***")`

Generator that applies both field-level and pattern-level redactions to an
iterable of records.  Either argument may be omitted.

```python
from logslice.redact import apply_redactions

cleaned = list(apply_redactions(records, fields=["password"], pattern=r"\d{16}"))
```

### `redact_nested(record, fields)`

Like `redact_fields`, but also redacts matching keys found in nested
dictionaries within the record.

```python
from logslice.redact import redact_nested

out = redact_nested({"user": "alice", "auth": {"token": "s3cr3t"}}, ["token"])
# {"user": "alice", "auth": {"token": "***"}}
```

## CLI usage

Pass `--redact-field` and/or `--redact-pattern` flags (when wired into the
CLI) to redact data at query time without modifying the source log files.

```
logslice app.log --redact-field token --redact-pattern 'key=\w+'
```
