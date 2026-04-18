"""Tests for logslice.session."""
import pytest
from pathlib import Path

from logslice.session import (
    delete_session,
    list_sessions,
    load_session,
    save_session,
)


@pytest.fixture()
def sdir(tmp_path):
    return tmp_path / "sessions"


def test_save_creates_file(sdir):
    path = save_session("myfilter", {"start": "2024-01-01"}, sdir)
    assert path.exists()


def test_save_and_load_roundtrip(sdir):
    cfg = {"start": "2024-01-01", "field": "level=error"}
    save_session("demo", cfg, sdir)
    loaded = load_session("demo", sdir)
    assert loaded == cfg


def test_load_missing_raises(sdir):
    with pytest.raises(FileNotFoundError, match="No session named 'ghost'"):
        load_session("ghost", sdir)


def test_list_sessions_empty(sdir):
    assert list_sessions(sdir) == []


def test_list_sessions_sorted(sdir):
    for name in ("zebra", "alpha", "middle"):
        save_session(name, {}, sdir)
    assert list_sessions(sdir) == ["alpha", "middle", "zebra"]


def test_delete_existing(sdir):
    save_session("temp", {}, sdir)
    result = delete_session("temp", sdir)
    assert result is True
    assert list_sessions(sdir) == []


def test_delete_missing_returns_false(sdir):
    assert delete_session("nope", sdir) is False


def test_save_overwrites(sdir):
    save_session("cfg", {"a": 1}, sdir)
    save_session("cfg", {"a": 99}, sdir)
    assert load_session("cfg", sdir)["a"] == 99
