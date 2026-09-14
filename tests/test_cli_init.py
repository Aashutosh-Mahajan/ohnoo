"""Tests `ohnoo init` end-to-end via the CLI, always targeting a throwaway rc
file through the OHNOO_BASH_RC/OHNOO_ZSH_RC override — never the real rc.
"""

from click.testing import CliRunner

from ohnoo.cli import main


def test_init_bash_is_idempotent(tmp_path, monkeypatch):
    rc = tmp_path / "fake_bashrc"
    monkeypatch.setenv("OHNOO_BASH_RC", str(rc))

    runner = CliRunner()
    result1 = runner.invoke(main, ["init", "--shell", "bash"])
    assert result1.exit_code == 0
    assert "installed" in result1.output
    assert rc.exists()

    result2 = runner.invoke(main, ["init", "--shell", "bash"])
    assert result2.exit_code == 0
    assert "already present" in result2.output


def test_init_zsh_is_idempotent(tmp_path, monkeypatch):
    rc = tmp_path / "fake_zshrc"
    monkeypatch.setenv("OHNOO_ZSH_RC", str(rc))

    runner = CliRunner()
    result1 = runner.invoke(main, ["init", "--shell", "zsh"])
    assert result1.exit_code == 0
    assert "installed" in result1.output
    assert rc.exists()

    result2 = runner.invoke(main, ["init", "--shell", "zsh"])
    assert "already present" in result2.output
