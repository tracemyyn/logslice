# Session Management

logslice lets you save and replay named filter configurations so you don't have
to retype common flag combinations.

## Saving a session

```bash
logslice app.log --start 2024-06-01 --field level=error --save-session prod-errors
```

The options are written to `~/.logslice/sessions/prod-errors.json`.

## Loading a session

```bash
logslice app.log --load-session prod-errors
```

Options from the session file are merged in before command-line processing.
Explicit CLI flags take precedence over the stored values.

## Listing sessions

```bash
logslice --list-sessions
```

Prints one session name per line, sorted alphabetically.

## Deleting a session

```bash
logslice --delete-session prod-errors
```

## Session file format

Sessions are plain JSON files stored in `~/.logslice/sessions/`:

```json
{
  "start": "2024-06-01T00:00:00",
  "field": ["level=error"],
  "format": "pretty"
}
```

You can edit them by hand or share them with teammates.

## Custom session directory

Set `LOGSLICE_SESSION_DIR` to override the default location:

```bash
export LOGSLICE_SESSION_DIR=/etc/logslice/sessions
```
