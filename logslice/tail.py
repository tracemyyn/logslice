"""Live tail support: follow a log file and emit new records as they arrive."""

import time
import os
from typing import Iterator, Optional

from logslice.parser import parse_line


def _open_at_end(path: str):
    """Open a file seeked to the end."""
    f = open(path, "r", encoding="utf-8", errors="replace")
    f.seek(0, 2)  # seek to end
    return f


def follow_file(
    path: str,
    poll_interval: float = 0.2,
    max_wait: Optional[float] = None,
) -> Iterator[dict]:
    """Yield parsed records from *path* as new lines are appended.

    Parameters
    ----------
    path:          path to the log file to follow
    poll_interval: seconds between read attempts
    max_wait:      stop after this many seconds of total waiting (None = forever)
    """
    waited = 0.0
    with _open_at_end(path) as fh:
        while True:
            line = fh.readline()
            if line:
                waited = 0.0
                record = parse_line(line)
                if record is not None:
                    yield record
            else:
                time.sleep(poll_interval)
                waited += poll_interval
                if max_wait is not None and waited >= max_wait:
                    return
                # Handle log rotation: if the file shrank, reopen
                try:
                    if os.path.getsize(path) < fh.tell():
                        fh.close()
                        fh = open(path, "r", encoding="utf-8", errors="replace")
                except OSError:
                    pass


def tail_lines(
    path: str,
    n: int = 10,
) -> list[dict]:
    """Return the last *n* parsed records from *path* (static snapshot)."""
    records: list[dict] = []
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            record = parse_line(line)
            if record is not None:
                records.append(record)
                if len(records) > n:
                    records.pop(0)
    return records
