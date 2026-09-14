"""Tests for persistent default-vibe storage, always via OHNOO_VIBE_FILE
override -- never the real ~/.config/ohnoo/vibe."""

import pytest
from click.testing import CliRunner

from ohnoo.cli import main
from ohnoo.vibes.config import get_default_vibe, set_default_vibe


def test_get_default_vibe_with_no_file_is_default(tmp_path, monkeypatch):
    monkeypatch.setenv("OHNOO_VIBE_FILE", str(tmp_path / "vibe"))
    assert get_default_vibe() == "default"


def test_set_and_get_default_vibe_round_trips(tmp_path, monkeypatch):
    monkeypatch.setenv("OHNOO_VIBE_FILE", str(tmp_path / "vibe"))
    set_default_vibe("zen")
    assert get_default_vibe() == "zen"


def test_set_default_vibe_rejects_unknown_name(tmp_path, monkeypatch):
    monkeypatch.setenv("OHNOO_VIBE_FILE", str(tmp_path / "vibe"))
    with pytest.raises(ValueError, match="Unknown vibe"):
        set_default_vibe("shakespearean-insult-generator")


def test_corrupt_vibe_file_degrades_to_default(tmp_path, monkeypatch):
    vibe_file = tmp_path / "vibe"
    vibe_file.write_text("not-a-real-vibe\n", encoding="utf-8")
    monkeypatch.setenv("OHNOO_VIBE_FILE", str(vibe_file))
    assert get_default_vibe() == "default"


def test_cli_vibe_command_shows_and_sets(tmp_path, monkeypatch):
    monkeypatch.setenv("OHNOO_VIBE_FILE", str(tmp_path / "vibe"))
    runner = CliRunner()

    show = runner.invoke(main, ["vibe"])
    assert show.exit_code == 0
    assert "default vibe is 'default'" in show.output

    set_result = runner.invoke(main, ["vibe", "gordon-ramsay"])
    assert set_result.exit_code == 0
    assert "set to 'gordon-ramsay'" in set_result.output

    show_again = runner.invoke(main, ["vibe"])
    assert "default vibe is 'gordon-ramsay'" in show_again.output


def test_cli_vibe_command_rejects_unknown_name(tmp_path, monkeypatch):
    monkeypatch.setenv("OHNOO_VIBE_FILE", str(tmp_path / "vibe"))
    runner = CliRunner()

    result = runner.invoke(main, ["vibe", "nonsense"])
    assert result.exit_code != 0
    assert "Unknown vibe" in result.output


def test_persisted_default_vibe_is_used_when_no_flag_passed(tmp_path, monkeypatch):
    monkeypatch.setenv("OHNOO_VIBE_FILE", str(tmp_path / "vibe"))
    monkeypatch.setenv("OHNOO_LAST_ROAST_FILE", str(tmp_path / "last_roast.json"))
    monkeypatch.setenv("OHNOO_STATS_FILE", str(tmp_path / "stats.json"))
    set_default_vibe("zen")

    runner = CliRunner()
    result = runner.invoke(main, [], input="ModuleNotFoundError: No module named 'flask'\n")
    assert result.exit_code == 0
    assert "flask" in result.output
