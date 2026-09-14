"""End-to-end tests for the Layer 1 pattern engine via ohnoo.engine.diagnose()."""

from ohnoo.engine import diagnose


def test_python_module_not_found_matches_and_fills_slot():
    text = "Traceback (most recent call last):\nModuleNotFoundError: No module named 'requests'"
    result = diagnose(text)
    assert result.matched
    assert result.pattern_id == "py-module-not-found"
    assert "requests" in result.joke
    # Shell-quoted so the suggested command can't be turned into an
    # injection vector by a crafted module name in the crash text.
    assert result.fix_command == "pip install 'requests'"


def test_node_eaddrinuse_matches_and_fills_port():
    text = "Error: listen EADDRINUSE: address already in use :::3000"
    result = diagnose(text)
    assert result.matched
    assert result.pattern_id == "node-eaddrinuse"
    assert "3000" in result.joke
    assert "3000" in result.fix_command


def test_git_not_a_repository_matches():
    text = "fatal: not a git repository (or any of the parent directories): .git"
    result = diagnose(text)
    assert result.matched
    assert result.pattern_id == "git-not-a-repository"


def test_unrecognized_error_does_not_match():
    result = diagnose("this is not a real error message at all")
    assert not result.matched
    assert "no known pattern matched" in result.render()


def test_vibe_override_is_used_when_present():
    text = "ModuleNotFoundError: No module named 'flask'"
    result = diagnose(text, vibe="zen")
    assert result.matched
    assert "flask" in result.joke


def test_captured_slot_with_shell_metacharacters_is_neutralized_in_fix_command():
    """Regression test: a crafted crash message could previously inject
    live shell syntax into a *suggested* fix command via an unquoted slot
    substitution -- e.g. a FileNotFoundError whose path is attacker text
    containing `$(...)`. If a user copy-pasted the suggested command, that
    would execute. Slot values must now always render as inert, quoted
    data."""
    payload = "/tmp/$(touch /tmp/pwned)"
    text = f"FileNotFoundError: [Errno 2] No such file or directory: '{payload}'"
    result = diagnose(text)
    assert result.matched
    assert result.pattern_id == "py-file-not-found"
    # The payload must be wrapped in single quotes -- inside single quotes
    # a POSIX shell performs no expansion at all, so $(...) is inert.
    assert result.fix_command == "ls -la $(dirname '/tmp/$(touch /tmp/pwned)')"
