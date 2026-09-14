"""Tests for the fish and PowerShell hook installers, always targeting a
throwaway rc/profile file via env override -- never the real one."""

import subprocess
from unittest.mock import patch

from ohnoo.hook import fish, pwsh
from ohnoo.hook.common import BEGIN_MARKER


def test_fish_install_is_idempotent(tmp_path, monkeypatch):
    rc = tmp_path / "config.fish"
    monkeypatch.setenv("OHNOO_FISH_CONFIG", str(rc))

    [(_, installed1)] = fish.install()
    assert installed1 is True
    assert rc.exists()
    assert "fish_postexec" in rc.read_text(encoding="utf-8")

    [(_, installed2)] = fish.install()
    assert installed2 is False
    assert rc.read_text(encoding="utf-8").count(BEGIN_MARKER) == 1


def test_pwsh_install_is_idempotent(tmp_path, monkeypatch):
    profile = tmp_path / "profile.ps1"
    monkeypatch.setenv("OHNOO_PWSH_PROFILE", str(profile))

    [(_, installed1)] = pwsh.install()
    assert installed1 is True
    assert profile.exists()
    assert "Start-Transcript" in profile.read_text(encoding="utf-8")

    [(_, installed2)] = pwsh.install()
    assert installed2 is False
    assert profile.read_text(encoding="utf-8").count(BEGIN_MARKER) == 1


def test_pwsh_install_respects_env_override_with_a_single_path(tmp_path, monkeypatch):
    profile = tmp_path / "only_this_one.ps1"
    monkeypatch.setenv("OHNOO_PWSH_PROFILE", str(profile))

    assert pwsh._rc_paths() == [profile]


# --- _query_profile_path() / _default_rc_paths(): OneDrive-redirected --
# Documents regression. Naive `~/Documents/...` silently points at the
# wrong physical file when Documents has been redirected (most commonly by
# OneDrive's "Back up your folders" feature, a Windows default many users
# have on) -- PowerShell's own $PROFILE correctly follows that redirection,
# so querying the real binary for it is the only fully robust fix.


def test_query_profile_path_returns_none_when_binary_missing():
    with patch("ohnoo.hook.pwsh.shutil.which", return_value=None):
        assert pwsh._query_profile_path("pwsh") is None


def test_query_profile_path_returns_the_resolved_path_from_the_binary():
    fake_result = subprocess.CompletedProcess(
        args=["powershell"],
        returncode=0,
        stdout="C:\\Users\\mahaj\\OneDrive\\Documents\\WindowsPowerShell\\Microsoft.PowerShell_profile.ps1\n",
        stderr="",
    )
    with patch("ohnoo.hook.pwsh.shutil.which", return_value="C:\\Windows\\powershell.exe"), patch(
        "ohnoo.hook.pwsh.subprocess.run", return_value=fake_result
    ):
        result = pwsh._query_profile_path("powershell")

    assert result is not None
    assert "OneDrive" in str(result)
    assert result.name == "Microsoft.PowerShell_profile.ps1"


def test_query_profile_path_returns_none_on_nonzero_exit_or_empty_output():
    failed = subprocess.CompletedProcess(args=["powershell"], returncode=1, stdout="", stderr="boom")
    with patch("ohnoo.hook.pwsh.shutil.which", return_value="powershell.exe"), patch(
        "ohnoo.hook.pwsh.subprocess.run", return_value=failed
    ):
        assert pwsh._query_profile_path("powershell") is None


def test_query_profile_path_returns_none_when_launch_itself_fails():
    with patch("ohnoo.hook.pwsh.shutil.which", return_value="powershell.exe"), patch(
        "ohnoo.hook.pwsh.subprocess.run", side_effect=OSError("nope")
    ):
        assert pwsh._query_profile_path("powershell") is None


def test_default_rc_paths_prefers_queried_path_over_naive_guess(monkeypatch):
    """Regression test for the OneDrive-redirection bug: when the real
    binary can be queried, its answer must win over the naive `~/Documents`
    guess, even though both point at files with the same edition-folder
    name."""
    queried_desktop = subprocess.CompletedProcess(
        args=["powershell"],
        returncode=0,
        stdout="C:\\Users\\mahaj\\OneDrive\\Documents\\WindowsPowerShell\\Microsoft.PowerShell_profile.ps1\n",
        stderr="",
    )

    def fake_which(binary):
        return f"{binary}.exe" if binary == "powershell" else None

    def fake_run(args, **kwargs):
        if args[0] == "powershell":
            return queried_desktop
        raise AssertionError(f"unexpected binary queried: {args[0]}")

    with patch("ohnoo.hook.pwsh.shutil.which", side_effect=fake_which), patch(
        "ohnoo.hook.pwsh.subprocess.run", side_effect=fake_run
    ):
        rc_paths = pwsh._default_rc_paths()

    assert len(rc_paths) == 2
    onedrive_paths = [p for p in rc_paths if "OneDrive" in str(p)]
    assert len(onedrive_paths) == 1
    assert "WindowsPowerShell" in onedrive_paths[0].parts
    # pwsh wasn't found -> falls back to the naive guess for that one.
    fallback_paths = [p for p in rc_paths if "OneDrive" not in str(p)]
    assert len(fallback_paths) == 1
    assert "PowerShell" in fallback_paths[0].parts
    assert "WindowsPowerShell" not in fallback_paths[0].parts


def test_default_rc_paths_falls_back_to_naive_guess_for_both_when_no_binaries_found():
    with patch("ohnoo.hook.pwsh.shutil.which", return_value=None):
        rc_paths = pwsh._default_rc_paths()

    assert len(rc_paths) == 2
    all_parts = [path.parts for path in rc_paths]
    assert any("WindowsPowerShell" in parts for parts in all_parts)
    assert any("PowerShell" in parts and "WindowsPowerShell" not in parts for parts in all_parts)
