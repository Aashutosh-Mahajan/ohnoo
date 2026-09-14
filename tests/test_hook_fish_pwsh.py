"""Tests for the fish and PowerShell hook installers, always targeting a
throwaway rc/profile file via env override -- never the real one."""

from ohnoo.hook import fish, pwsh
from ohnoo.hook.common import BEGIN_MARKER


def test_fish_install_is_idempotent(tmp_path, monkeypatch):
    rc = tmp_path / "config.fish"
    monkeypatch.setenv("OHNOO_FISH_CONFIG", str(rc))

    _, installed1 = fish.install()
    assert installed1 is True
    assert rc.exists()
    assert "fish_postexec" in rc.read_text(encoding="utf-8")

    _, installed2 = fish.install()
    assert installed2 is False
    assert rc.read_text(encoding="utf-8").count(BEGIN_MARKER) == 1


def test_pwsh_install_is_idempotent(tmp_path, monkeypatch):
    profile = tmp_path / "profile.ps1"
    monkeypatch.setenv("OHNOO_PWSH_PROFILE", str(profile))

    _, installed1 = pwsh.install()
    assert installed1 is True
    assert profile.exists()
    assert "Start-Transcript" in profile.read_text(encoding="utf-8")

    _, installed2 = pwsh.install()
    assert installed2 is False
    assert profile.read_text(encoding="utf-8").count(BEGIN_MARKER) == 1
