# Field Transformation

`logslice` can rename, drop, or keep fields in each log record before output.

## CLI Flags

| Flag | Description |
|------|-------------|
| `--rename old=new,...` | Rename one or more fields |
| `--drop field,...` | Remove fields from output |
| `--keep field,...` | Keep only specified fields |

Transformations are applied in order: **rename → drop → keep**.

## Examples

### Rename `msg` to `message`

```bash
logslice app.log --rename msg=message
```

### Drop noisy fields

```bash
logslice app.log --drop caller,stacktrace
```

### Keep only essential fields

```bash
logslice app.log --keep ts,level,msg
```

### Combine transforms

```bash
logslice app.log --rename msg=message --drop host --keep ts,level,message
```

## Python API

```python
from logslice.transform import apply_transforms

record = {"ts": "...", "level": "info", "msg": "hello", "host": "web-1"}

cleaned = apply_transforms(
    record,
    rename={"msg": "message"},
    drop=["host"],
    keep=["ts", "level", "message"],
)
# -> {"ts": "...", "level": "info", "message": "hello"}
```
