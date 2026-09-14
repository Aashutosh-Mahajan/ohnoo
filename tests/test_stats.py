"""Tests for local --stats tracking, always redirected via OHNOO_STATS_FILE."""

import json

from ohnoo.stats import record_roast, summary


def test_summary_with_no_records_is_friendly(tmp_path, monkeypatch):
    monkeypatch.setenv("OHNOO_STATS_FILE", str(tmp_path / "stats.json"))
    assert summary() == "No roasts yet. Go break something."


def test_summary_with_missing_file_does_not_raise(tmp_path, monkeypatch):
    monkeypatch.setenv("OHNOO_STATS_FILE", str(tmp_path / "does_not_exist" / "stats.json"))
    assert summary() == "No roasts yet. Go break something."


def test_summary_with_corrupt_file_degrades_gracefully(tmp_path, monkeypatch):
    stats_file = tmp_path / "stats.json"
    stats_file.write_text("not valid json {{{", encoding="utf-8")
    monkeypatch.setenv("OHNOO_STATS_FILE", str(stats_file))
    assert summary() == "No roasts yet. Go break something."


def test_record_roast_creates_file_and_dirs(tmp_path, monkeypatch):
    stats_file = tmp_path / "nested" / "stats.json"
    monkeypatch.setenv("OHNOO_STATS_FILE", str(stats_file))

    record_roast("py-module-not-found", "python")

    assert stats_file.exists()
    records = json.loads(stats_file.read_text(encoding="utf-8"))
    assert len(records) == 1
    assert records[0]["pattern_id"] == "py-module-not-found"
    assert records[0]["language"] == "python"
    assert "timestamp" in records[0]


def test_record_roast_appends(tmp_path, monkeypatch):
    stats_file = tmp_path / "stats.json"
    monkeypatch.setenv("OHNOO_STATS_FILE", str(stats_file))

    record_roast("py-module-not-found", "python")
    record_roast("node-eaddrinuse", "node")

    records = json.loads(stats_file.read_text(encoding="utf-8"))
    assert len(records) == 2


def test_summary_reports_total_and_most_common_pattern(tmp_path, monkeypatch):
    stats_file = tmp_path / "stats.json"
    monkeypatch.setenv("OHNOO_STATS_FILE", str(stats_file))

    record_roast("py-module-not-found", "python")
    record_roast("py-module-not-found", "python")
    record_roast("node-eaddrinuse", "node")

    text = summary()
    assert "3" in text
    assert "module not found" in text


def test_summary_singular_wording_for_one_roast(tmp_path, monkeypatch):
    stats_file = tmp_path / "stats.json"
    monkeypatch.setenv("OHNOO_STATS_FILE", str(stats_file))

    record_roast("git-not-a-repository", "git")

    assert "1 time" in summary()


def test_record_roast_never_raises_on_unwritable_path(tmp_path, monkeypatch):
    # Point the stats file *inside* a plain file, so mkdir(parents=True) on its
    # parent must fail — simulates a broken/unwritable path without touching
    # anything outside tmp_path.
    blocking_file = tmp_path / "not_a_directory"
    blocking_file.write_text("blocked", encoding="utf-8")
    stats_file = blocking_file / "nested" / "stats.json"
    monkeypatch.setenv("OHNOO_STATS_FILE", str(stats_file))

    record_roast("py-module-not-found", "python")  # should not raise
