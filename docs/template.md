# Template Output

The `--template` flag lets you format each log record using a custom template string instead of JSON, logfmt, or pretty output.

## Syntax

Reference fields with `{field_name}`. Provide a fallback with `{field_name:default}`.

```
{ts} [{level}] {msg}
```

## Examples

### Basic template

```bash
logslice --template '{ts} [{level}] {msg}' app.log
```

Output:

```
2024-01-15T12:00:00Z [info] server started
2024-01-15T12:01:00Z [error] connection refused
```

### With defaults

When a field may be absent, supply a default after `:` inside the braces:

```bash
logslice --template '{ts} {request_id:n/a} {msg}' app.log
```

### Combined with filters

```bash
logslice --start 2024-01-15T12:00:00Z --filter level=error \
         --template '{ts} {svc} — {msg}' app.log
```

## API

```python
from logslice.template import render_template, compile_template, list_template_fields

render_template("{ts} {msg}", record)        # render once
render = compile_template("{ts} {msg}")      # reusable callable
render(record)
list_template_fields("{ts} [{level}] {msg}") # ['ts', 'level', 'msg']
```
