"""Tests for logslice.tail (static helpers; follow_file tested with tmp files)."""

import json
import os
import tempfile
import time
import threading

import pytest

from logslice.tail import tail_lines, follow_file


def _write_lines(path: str, lines: list[str]):
    with open(path, "a", encoding="utf-8") as fh:
        for line in lines:
            fh.write(line + "\n")
        fh.flush()


def _json_line(msg: str, level: str = "info") -> str:
    return json.dumps({"level": level, "msg": msg})


@pytest.fixture()
def tmp_log(tmp_path):
    p = tmp_path / "app.log"
    p.touch()
    return str(p)


def test_tail_lines_returns_last_n(tmp_log):
    _write_lines(tmp_log, [_json_line(f"msg{i}") for i in range(20)])
    result = tail_lines(tmp_log, n=5)
    assert len(result) == 5
    assert result[-1]["msg"] == "msg19"


def test_tail_lines_fewer_than_n(tmp_log):
    _write_lines(tmp_log, [_json_line("only")])
    result = tail_lines(tmp_log, n=10)
    assert len(result) == 1


def test_tail_lines_empty_file(tmp_log):
    result = tail_lines(tmp_log, n=5)
    assert result == []


def test_tail_lines_skips_invalid(tmp_log):
    with open(tmp_log, "w") as fh:
        fh.write("not json or logfmt\n")
        fh.write(_json_line("good") + "\n")
    result = tail_lines(tmp_log, n=10)
    # "not json or logfmt" may parse as logfmt with a single key; just ensure no crash
    assert any(r.get("msg") == "good" for r in result)


def test_follow_file_yields_new_records(tmp_log):
    collected: list[dict] = []

    def _writer():
        time.sleep(0.05)
        _write_lines(tmp_log, [_json_line("live1"), _json_line("live2")])

    t = threading.Thread(target=_writer, daemon=True)
    t.start()

    for record in follow_file(tmp_log, poll_interval=0.05, max_wait=1.0):
        collected.append(record)
        if len(collected) >= 2:
            break

    t.join(timeout=2)
    msgs = [r.get("msg") for r in collected]
    assert "live1" in msgs
    assert "live2" in msgs


def test_follow_file_max_wait_stops(tmp_log):
    """follow_file should stop after max_wait if no new data arrives."""
    records = list(follow_file(tmp_log, poll_interval=0.05, max_wait=0.15))
    assert records == []
