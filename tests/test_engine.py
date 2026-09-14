"""End-to-end tests for the Layer 1 pattern engine via ohnoo.engine.diagnose()."""

from ohnoo.engine import diagnose


def test_python_module_not_found_matches_and_fills_slot():
    text = "Traceback (most recent call last):\nModuleNotFoundError: No module named 'requests'"
    result = diagnose(text)
    assert result.matched
    assert result.pattern_id == "py-module-not-found"
    assert "requests" in result.joke
    assert result.fix_command == "pip install requests"


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
