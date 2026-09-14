"""Integration tests for cli.py's wiring of stats/share/explain/fix/setup-ai.

Every test overrides the relevant env var (OHNOO_LAST_ROAST_FILE,
OHNOO_STATS_FILE, OHNOO_CONFIG_PATH) via monkeypatch + tmp_path so nothing
ever touches the real user home directory.
"""

from __future__ import annotations

from click.testing import CliRunner

from ohnoo.cli import main


def _isolate_state(monkeypatch, tmp_path):
    monkeypatch.setenv("OHNOO_LAST_ROAST_FILE", str(tmp_path / "last_roast.json"))
    monkeypatch.setenv("OHNOO_STATS_FILE", str(tmp_path / "stats.json"))
    monkeypatch.setenv("OHNOO_CONFIG_PATH", str(tmp_path / "config.toml"))


def test_pipe_mode_matched_error_saves_stats_and_last_roast(tmp_path, monkeypatch):
    _isolate_state(monkeypatch, tmp_path)
    runner = CliRunner()

    result = runner.invoke(main, [], input="ModuleNotFoundError: No module named 'requests'\n")
    assert result.exit_code == 0
    assert "requests" in result.output
    assert "pip install requests" in result.output

    from ohnoo import stats

    assert "Roasted 1 time" in stats.summary()

    from ohnoo.engine import load_last

    cached = load_last()
    assert cached is not None
    diagnosis, _command = cached
    assert diagnosis.pattern_id == "py-module-not-found"


def test_pipe_mode_unmatched_error_nudges_setup_ai(tmp_path, monkeypatch):
    _isolate_state(monkeypatch, tmp_path)
    runner = CliRunner()

    result = runner.invoke(main, [], input="totally unrecognized gibberish\n")
    assert result.exit_code == 0
    assert "no known pattern matched" in result.output


def test_stats_command_with_no_data(tmp_path, monkeypatch):
    _isolate_state(monkeypatch, tmp_path)
    runner = CliRunner()

    result = runner.invoke(main, ["stats"])
    assert result.exit_code == 0
    assert "No roasts yet" in result.output


def test_share_command_with_no_cached_roast(tmp_path, monkeypatch):
    _isolate_state(monkeypatch, tmp_path)
    runner = CliRunner()

    result = runner.invoke(main, ["share"])
    assert result.exit_code == 0
    assert "no roast recorded yet" in result.output


def test_share_command_after_a_matched_roast(tmp_path, monkeypatch):
    _isolate_state(monkeypatch, tmp_path)
    runner = CliRunner()

    runner.invoke(main, [], input="ModuleNotFoundError: No module named 'flask'\n")
    result = runner.invoke(main, ["share"])
    assert result.exit_code == 0
    assert "share card saved to" in result.output

    from pathlib import Path

    saved_path = result.output.split("share card saved to", 1)[1].strip()
    assert Path(saved_path).exists()


def test_explain_and_fix_report_no_error_text_when_nothing_piped(tmp_path, monkeypatch):
    _isolate_state(monkeypatch, tmp_path)
    monkeypatch.setenv("OHNOO_LOG", str(tmp_path / "does_not_exist.log"))
    runner = CliRunner()

    explain_result = runner.invoke(main, ["explain"])
    assert "no error text to work with" in explain_result.output

    fix_result = runner.invoke(main, ["fix"])
    assert "no error text to work with" in fix_result.output


def test_setup_ai_disable_never_prompts(tmp_path, monkeypatch):
    _isolate_state(monkeypatch, tmp_path)
    runner = CliRunner()

    result = runner.invoke(main, ["setup-ai", "--disable"])
    assert result.exit_code == 0
    assert "disabled" in result.output.lower()
