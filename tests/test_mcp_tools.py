"""Tests for the Layer 3 MCP tool functions.

These call the plain importable functions directly (not through the MCP
protocol layer), since a real MCP client isn't available in this test
environment. See src/ohnoo/mcp_server/server.py for how the MCP-decorated
tools wrap these same functions.
"""

from ohnoo.mcp_server.server import _diagnose_error, _roast_error, _suggest_fix

PY_MODULE_NOT_FOUND_TRACEBACK = (
    "Traceback (most recent call last):\n"
    '  File "app.py", line 1, in <module>\n'
    "    import requests\n"
    "ModuleNotFoundError: No module named 'requests'"
)


def test_diagnose_error_matches_python_module_not_found():
    result = _diagnose_error(PY_MODULE_NOT_FOUND_TRACEBACK)
    assert result["matched"] is True
    assert result["pattern_id"] == "py-module-not-found"
    assert "py-module-not-found" in result["diagnosis"]
    assert "pip install requests" in result["suggested_fix"]


def test_diagnose_error_includes_file_context_in_matching():
    result = _diagnose_error(
        "ModuleNotFoundError: No module named 'flask'", file_context="app.py:1"
    )
    assert result["matched"] is True
    assert result["pattern_id"] == "py-module-not-found"


def test_diagnose_error_unmatched_returns_graceful_shape():
    result = _diagnose_error("this is not a real error at all")
    assert result["matched"] is False
    assert result["pattern_id"] is None
    assert isinstance(result["diagnosis"], str)
    assert result["suggested_fix"] == ""


def test_diagnose_error_never_raises_on_garbage_input():
    for bad in (None, "", 123, [], {}):
        result = _diagnose_error(bad)  # type: ignore[arg-type]
        assert result["matched"] is False


def test_suggest_fix_matches_recognizable_error_type():
    # error_type + " " + context is used as the search text, so the colon
    # needs to land right after "ModuleNotFoundError" to match the pattern's
    # regex (see src/ohnoo/patterns/python.json: "py-module-not-found").
    result = _suggest_fix("ModuleNotFoundError:", context="No module named 'numpy'")
    assert result["matched"] is True
    assert "pip install" in result["fix_command"]
    assert result["fix_summary"]


def test_suggest_fix_unmatched_returns_graceful_shape():
    result = _suggest_fix("TotallyMadeUpError", context="nonsense")
    assert result["matched"] is False
    assert result["fix_summary"] == ""
    assert result["fix_command"] == ""


def test_suggest_fix_never_raises_on_garbage_input():
    for bad in (None, "", 123, [], {}):
        result = _suggest_fix(bad, bad)  # type: ignore[arg-type]
        assert result["matched"] is False


def test_roast_error_matched_returns_real_joke():
    result = _roast_error(PY_MODULE_NOT_FOUND_TRACEBACK)
    assert result["matched"] is True
    assert result["joke"]
    assert "requests" in result["joke"]


def test_roast_error_unmatched_returns_nonempty_fallback_joke():
    result = _roast_error("some completely unrecognized gibberish error")
    assert result["matched"] is False
    assert isinstance(result["joke"], str)
    assert len(result["joke"]) > 0


def test_roast_error_never_raises_on_garbage_input():
    for bad in (None, "", 123, [], {}):
        result = _roast_error(bad)  # type: ignore[arg-type]
        assert result["matched"] is False
        assert result["joke"]
