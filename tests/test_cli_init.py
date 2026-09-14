"""Tests `ohnoo init` end-to-end via the CLI, always targeting a throwaway rc
file through the OHNOO_BASH_RC/OHNOO_ZSH_RC override — never the real rc.
"""

import os

from click.testing import CliRunner

from ohnoo.cli import _check_ohnoo_on_path, main


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


def test_init_uninstall_removes_a_previously_installed_hook(tmp_path, monkeypatch):
    rc = tmp_path / "fake_bashrc"
    monkeypatch.setenv("OHNOO_BASH_RC", str(rc))
    runner = CliRunner()

    runner.invoke(main, ["init", "--shell", "bash"])
    assert "ohnoo hook" in rc.read_text(encoding="utf-8")

    result = runner.invoke(main, ["init", "--shell", "bash", "--uninstall"])
    assert result.exit_code == 0
    assert "removed" in result.output
    assert "ohnoo hook" not in rc.read_text(encoding="utf-8")


def test_init_uninstall_on_never_installed_hook_is_a_noop(tmp_path, monkeypatch):
    rc = tmp_path / "fake_bashrc"
    monkeypatch.setenv("OHNOO_BASH_RC", str(rc))
    runner = CliRunner()

    result = runner.invoke(main, ["init", "--shell", "bash", "--uninstall"])
    assert result.exit_code == 0
    assert "not found" in result.output


# --- _check_ohnoo_on_path(): the pip-installs-outside-PATH regression ----
#
# `pip install --user` (the common non-venv case, especially on Windows)
# frequently installs the `ohnoo` console-script shim into a directory
# that isn't on PATH by default. The shell hooks wrap `ohnoo check` in a
# catch-everything guard so a *missing agent CLI* never breaks the user's
# prompt -- but that guard is indiscriminate, so a missing `ohnoo` itself
# fails in total silence unless `init` catches it up front.


def test_check_ohnoo_on_path_returns_none_when_already_resolvable(monkeypatch):
    monkeypatch.setattr("ohnoo.cli.shutil.which", lambda name: "/usr/bin/ohnoo")
    assert _check_ohnoo_on_path() is None


def test_check_ohnoo_on_path_warns_with_a_concrete_fix_when_shim_exists_but_unreachable(
    monkeypatch, tmp_path
):
    scripts_dir = tmp_path / "Scripts"
    scripts_dir.mkdir()
    exe_name = "ohnoo.exe" if os.name == "nt" else "ohnoo"
    (scripts_dir / exe_name).write_text("", encoding="utf-8")

    monkeypatch.setattr("ohnoo.cli.shutil.which", lambda name: None)
    monkeypatch.setattr("ohnoo.cli.sysconfig.get_path", lambda name: str(scripts_dir))

    warning = _check_ohnoo_on_path()

    assert warning is not None
    assert str(scripts_dir) in warning
    assert "pipx install ohnoo" in warning


def test_check_ohnoo_on_path_returns_none_when_it_cant_locate_a_specific_fix(monkeypatch, tmp_path):
    monkeypatch.setattr("ohnoo.cli.shutil.which", lambda name: None)
    monkeypatch.setattr("ohnoo.cli.sysconfig.get_path", lambda name: str(tmp_path / "nonexistent"))

    assert _check_ohnoo_on_path() is None


def test_init_surfaces_the_path_warning_in_its_output(tmp_path, monkeypatch):
    rc = tmp_path / "fake_bashrc"
    monkeypatch.setenv("OHNOO_BASH_RC", str(rc))
    monkeypatch.setattr("ohnoo.cli._check_ohnoo_on_path", lambda: "PATH is broken, fix it like this")

    runner = CliRunner()
    result = runner.invoke(main, ["init", "--shell", "bash"])

    assert "PATH is broken, fix it like this" in result.output
