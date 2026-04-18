"""Tests for logslice.cli_tail helpers."""

import argparse
import io
import json
import tempfile
import os

import pytest

from logslice.cli_tail import add_tail_args, apply_tail


def _make_args(**kwargs) -> argparse.Namespace:
    defaults = {"tail": None, "follow": False, "follow_poll": 0.2, "file": None}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def _json_line(msg: str) -> str:
    return json.dumps({"msg": msg})


@pytest.fixture()
def log_file(tmp_path):
    p = tmp_path / "test.log"
    lines = [_json_line(f"msg{i}") for i in range(10)]
    p.write_text("\n".join(lines) + "\n")
    return str(p)


def test_add_tail_args_registers_tail(tmp_path):
    parser = argparse.ArgumentParser()
    add_tail_args(parser)
    args = parser.parse_args(["--tail", "5"])
    assert args.tail == 5


def test_add_tail_args_registers_follow(tmp_path):
    parser = argparse.ArgumentParser()
    add_tail_args(parser)
    args = parser.parse_args(["--follow"])
    assert args.follow is True


def test_add_tail_args_follow_poll_default():
    parser = argparse.ArgumentParser()
    add_tail_args(parser)
    args = parser.parse_args([])
    assert args.follow_poll == 0.2


def test_apply_tail_no_flags_returns_false(log_file):
    args = _make_args(file=log_file)
    out = io.StringIO()
    result = apply_tail(args, output=out)
    assert result is False
    assert out.getvalue() == ""


def test_apply_tail_tail_flag_outputs_n_records(log_file):
    args = _make_args(file=log_file, tail=3)
    out = io.StringIO()
    result = apply_tail(args, fmt="json", output=out)
    assert result is True
    lines = [l for l in out.getvalue().splitlines() if l.strip()]
    assert len(lines) == 3


def test_apply_tail_tail_flag_last_record(log_file):
    args = _make_args(file=log_file, tail=1)
    out = io.StringIO()
    apply_tail(args, fmt="json", output=out)
    record = json.loads(out.getvalue().strip())
    assert record["msg"] == "msg9"


def test_apply_tail_no_file_returns_false():
    args = _make_args(file=None, tail=5)
    out = io.StringIO()
    result = apply_tail(args, output=out)
    assert result is False
