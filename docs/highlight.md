# Terminal Highlighting

`logslice` can colorize output when writing to a terminal, making it easier to
scan log streams at a glance.

## Level-based colors

When pretty output is enabled, the log level field is automatically detected
(`level`, `severity`, or `lvl`) and the entire record is colored accordingly:

| Level            | Color   |
|------------------|---------|
| error / err      | red     |
| warn / warning   | yellow  |
| info             | green   |
| debug            | cyan    |
| trace            | magenta |

## Highlighting search terms

Use `--highlight <pattern>` to bold-highlight a literal string inside every
output line:

```bash
logslice app.log --highlight "connection refused"
```

## Highlighting specific fields

Use `--highlight-fields field1,field2` to colorize the values of named fields:

```bash
logslice app.log --highlight-fields user_id,request_id
```

## API

```python
from logslice.highlight import colorize, highlight_level, highlight_matches, highlight_fields

# Wrap a string in a color
colorize("ERROR", "red", bold=True)

# Determine color from a record dict
color = highlight_level({"level": "warn"})  # -> "yellow"

# Highlight a substring everywhere it appears
highlight_matches(line, "timeout", color="yellow")

# Colorize specific fields in a record dict
highlight_fields(record, ["user_id"], color="cyan")
```

All functions are pure — they return new strings or dicts and never mutate
their inputs.
