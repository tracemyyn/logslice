"""Tests for the CLI entry point."""

import json
import textwrap
from unittest.mock import patch
import pytest

from logslice.cli import run


JSON_LINES = textwrap.dedent("""\
    {"ts":"2024-01-01T10:00:00Z","level":"info","msg":"started"}
    {"ts":"2024-01-01T10:05:00Z","level":"error","msg":"failed"}
    {"ts":"2024-01-01T10:10:00Z","level":"info","msg":"done"}
""")


def _lines_file(tmp_path, content):
    f = tmp_path / "test.log"
    f.write_text(content)
    return str(f)


def test_run_no_filters_outputs_all(tmp_path, capsys):
    path = _lines_file(tmp_path, JSON_LINES)
    rc = run([path, "--output", "json"])
    assert rc == 0
    captured = capsys.readouterr().out.strip().splitlines()
    assert len(captured) == 3


def test_run_count_flag(tmp_path, capsys):
    path = _lines_file(tmp_path, JSON_LINES)
    rc = run([path, "--count"])
    assert rc == 0
    assert capsys.readouterr().out.strip() == "3"


def test_run_field_filter(tmp_path, capsys):
    path = _lines_file(tmp_path, JSON_LINES)
    rc = run([path, "--filter", "level=error", "--count"])
    assert rc == 0
    assert capsys.readouterr().out.strip() == "1"


def test_run_start_filter(tmp_path, capsys):
    path = _lines_file(tmp_path, JSON_LINES)
    rc = run([path, "--start", "2024-01-01T10:05:00Z", "--count"])
    assert rc == 0
    assert capsys.readouterr().out.strip() == "2"


def test_run_end_filter(tmp_path, capsys):
    path = _lines_file(tmp_path, JSON_LINES)
    rc = run([path, "--end", "2024-01-01T10:05:00Z", "--count"])
    assert rc == 0
    assert capsys.readouterr().out.strip() == "2"


def test_run_missing_file_returns_1(capsys):
    rc = run(["/nonexistent/path/file.log"])
    assert rc == 1
    assert "logslice:" in capsys.readouterr().err


def test_run_output_logfmt(tmp_path, capsys):
    path = _lines_file(tmp_path, JSON_LINES)
    rc = run([path, "--output", "logfmt"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "level=" in out


def test_run_stdin(capsys):
    import io
    fake_stdin = io.StringIO(JSON_LINES)
    with patch("sys.stdin", fake_stdin):
        rc = run(["--count"])
    assert rc == 0
    assert capsys.readouterr().out.strip() == "3"
