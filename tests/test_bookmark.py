"""Tests for logslice.bookmark."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch

from logslice import bookmark as bm_mod


@pytest.fixture(autouse=True)
def _tmp_bookmark_dir(tmp_path, monkeypatch):
    bm_dir = tmp_path / "bookmarks"
    monkeypatch.setattr(bm_mod, "_BOOKMARK_DIR", bm_dir)
    yield bm_dir


def test_save_creates_file(_tmp_bookmark_dir):
    bm_mod.save_bookmark("/var/log/app.log", 1024)
    files = list(_tmp_bookmark_dir.glob("*.json"))
    assert len(files) == 1


def test_save_and_load_roundtrip():
    bm_mod.save_bookmark("/var/log/app.log", 2048, label="after-deploy")
    data = bm_mod.load_bookmark("/var/log/app.log")
    assert data["offset"] == 2048
    assert data["label"] == "after-deploy"
    assert data["log_path"] == "/var/log/app.log"


def test_load_missing_raises():
    with pytest.raises(FileNotFoundError):
        bm_mod.load_bookmark("/nonexistent/file.log")


def test_delete_existing_returns_true():
    bm_mod.save_bookmark("/tmp/x.log", 0)
    assert bm_mod.delete_bookmark("/tmp/x.log") is True


def test_delete_missing_returns_false():
    assert bm_mod.delete_bookmark("/tmp/ghost.log") is False


def test_list_bookmarks_empty():
    assert bm_mod.list_bookmarks() == []


def test_list_bookmarks_multiple():
    bm_mod.save_bookmark("/a.log", 10)
    bm_mod.save_bookmark("/b.log", 20)
    result = bm_mod.list_bookmarks()
    assert len(result) == 2
    offsets = {r["offset"] for r in result}
    assert offsets == {10, 20}


def test_offset_lines_reads_from_position(tmp_path):
    log = tmp_path / "test.log"
    log.write_text("line1\nline2\nline3\n")
    offset = len("line1\n")
    lines = list(bm_mod.offset_lines(str(log), offset))
    assert lines[0].strip() == "line2"
    assert len(lines) == 2


def test_offset_lines_zero_reads_all(tmp_path):
    log = tmp_path / "test.log"
    log.write_text("a\nb\nc\n")
    lines = list(bm_mod.offset_lines(str(log), 0))
    assert len(lines) == 3
