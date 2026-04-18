# Tail & Follow

`logslice` can display the last *N* records from a log file or stream new
records in real time as they are appended — similar to `tail -f`.

## Static tail

Print the last 20 records and exit:

```bash
logslice app.log --tail 20
```

Combine with output formatting:

```bash
logslice app.log --tail 50 --format pretty
```

## Follow (live stream)

Watch a file for new log lines and print them as they arrive:

```bash
logslice app.log --follow
```

Press **Ctrl-C** to stop.

Adjust the polling interval (default 0.2 s):

```bash
logslice app.log --follow --follow-poll 0.5
```

## Combining with filters

All standard filters work alongside `--follow` and `--tail`:

```bash
# Follow and show only error records
logslice app.log --follow --filter level=error

# Last 10 records from a specific service
logslice app.log --tail 10 --filter service=payments
```

## Log rotation

When `--follow` is active, `logslice` detects if the file has been rotated
(i.e. its size drops below the current read position) and automatically
reopens it from the beginning of the new file.

## Python API

```python
from logslice.tail import tail_lines, follow_file

# Static snapshot
for record in tail_lines("app.log", n=10):
    print(record)

# Live stream
for record in follow_file("app.log", poll_interval=0.1):
    print(record)
```
