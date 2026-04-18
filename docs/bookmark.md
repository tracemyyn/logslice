# Bookmark

The bookmark feature lets you save your position in a log file and resume
reading from that byte offset in a later session.

## Concepts

- A **bookmark** records the file path and a byte offset.
- Bookmarks are stored in `~/.logslice/bookmarks/` as small JSON files.
- An optional **label** can annotate the bookmark (e.g. `"after-deploy"`).

## API

### `save_bookmark(log_path, offset, label=None) -> Path`

Persist the offset for the given log file. Overwrites any existing bookmark
for the same path.

```python
from logslice.bookmark import save_bookmark
save_bookmark("/var/log/app.log", 40960, label="post-release")
```

### `load_bookmark(log_path) -> dict`

Load a previously saved bookmark. Raises `FileNotFoundError` if none exists.

```python
from logslice.bookmark import load_bookmark
bm = load_bookmark("/var/log/app.log")
print(bm["offset"])  # 40960
```

### `delete_bookmark(log_path) -> bool`

Remove the bookmark for a file. Returns `True` if it existed.

### `list_bookmarks() -> list[dict]`

Return all saved bookmarks.

### `offset_lines(log_path, offset)`

Generator that opens *log_path*, seeks to *offset*, and yields lines from
that point onward. Combine with the parser to resume processing:

```python
from logslice.bookmark import load_bookmark, offset_lines, save_bookmark
from logslice.parser import parse_line
import os

bm = load_bookmark("/var/log/app.log")
for line in offset_lines(bm["log_path"], bm["offset"]):
    record = parse_line(line)
    if record:
        process(record)

# Save new position
with open("/var/log/app.log") as fh:
    fh.seek(0, os.SEEK_END)
    save_bookmark("/var/log/app.log", fh.tell())
```

## Storage

Bookmark files are named after a sanitised version of the log path and stored
in `~/.logslice/bookmarks/`. Each file contains a JSON object:

```json
{"log_path": "/var/log/app.log", "offset": 40960, "label": "post-release"}
```
