# logslice

A CLI tool to filter and slice structured log files by time range and field patterns.

## Installation

```bash
pip install logslice
```

## Usage

```bash
logslice [OPTIONS] <logfile>
```

### Examples

Filter logs within a time range:
```bash
logslice --start "2024-01-15T08:00:00" --end "2024-01-15T09:00:00" app.log
```

Filter by field pattern:
```bash
logslice --field "level=ERROR" --field "service=api" app.log
```

Combine time range and field filters:
```bash
logslice --start "2024-01-15T08:00:00" --end "2024-01-15T09:00:00" --field "level=WARN" app.log
```

Output to a file:
```bash
logslice --start "2024-01-15T08:00:00" --field "level=ERROR" app.log -o errors.log
```

### Options

| Option | Description |
|--------|-------------|
| `--start` | Start of time range (ISO 8601) |
| `--end` | End of time range (ISO 8601) |
| `--field` | Field pattern to match (`key=value`), repeatable |
| `-o, --output` | Write output to file instead of stdout |
| `--format` | Input log format: `json`, `logfmt` (default: `json`) |

## Supported Formats

- **JSON** — one JSON object per line
- **logfmt** — `key=value` pairs per line

## License

MIT © [logslice contributors](LICENSE)