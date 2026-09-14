"""Tests for Layer 2 — CLI agent handoff (src/ohnoo/agents/)."""

from __future__ import annotations

import subprocess
from unittest.mock import patch

from ohnoo.agents import handoff
from ohnoo.agents._common import FixResult
from ohnoo.agents.detect import DEFAULT_PRIORITY, detect_available_agents, pick_agent
from ohnoo.agents.prompt_builder import build_scoped_prompt, extract_file_line

PY_TRACEBACK = (
    "Traceback (most recent call last):\n"
    '  File "/home/user/project/app.py", line 42, in <module>\n'
    "    do_thing()\n"
    "ModuleNotFoundError: No module named 'requests'"
)

NODE_TRACEBACK = (
    "Error: listen EADDRINUSE: address already in use :::3000\n"
    "    at Server.setupListenHandle [as _listen2] (net.js:1300:16)\n"
    "    at listenInCluster (net.js:1348:12)\n"
    "    at doListen (net.js:1486:7)\n"
    "    at at (/home/user/project/server.js:10:5)"
)


# --- detect.py ---------------------------------------------------------


def test_detect_available_agents_filters_to_present_binaries():
    def fake_which(name):
        return f"/usr/bin/{name}" if name in ("claude", "agy") else None

    with patch("ohnoo.agents.detect.shutil.which", side_effect=fake_which):
        assert detect_available_agents() == ["claude", "agy"]


def test_detect_available_agents_none_present():
    with patch("ohnoo.agents.detect.shutil.which", return_value=None):
        assert detect_available_agents() == []


def test_detect_available_agents_respects_custom_priority():
    def fake_which(name):
        return f"/usr/bin/{name}" if name in ("codex", "agy") else None

    with patch("ohnoo.agents.detect.shutil.which", side_effect=fake_which):
        assert detect_available_agents(["agy", "codex", "claude"]) == ["agy", "codex"]


def test_pick_agent_returns_first_available_in_default_priority():
    def fake_which(name):
        return f"/usr/bin/{name}" if name in ("codex", "agy") else None

    with patch("ohnoo.agents.detect.shutil.which", side_effect=fake_which):
        assert pick_agent() == "codex"


def test_pick_agent_returns_none_when_nothing_available():
    with patch("ohnoo.agents.detect.shutil.which", return_value=None):
        assert pick_agent() is None


def test_default_priority_order():
    assert DEFAULT_PRIORITY == ["claude", "codex", "agy"]


# --- prompt_builder.py ---------------------------------------------------


def test_extract_file_line_python_style():
    path, line = extract_file_line(PY_TRACEBACK)
    assert path == "/home/user/project/app.py"
    assert line == 42


def test_extract_file_line_node_style():
    path, line = extract_file_line(NODE_TRACEBACK)
    assert path is not None
    assert line is not None


def test_extract_file_line_no_match_returns_none_none():
    path, line = extract_file_line("this is not a traceback at all")
    assert (path, line) == (None, None)


def test_extract_file_line_never_raises_on_empty_string():
    assert extract_file_line("") == (None, None)


def test_build_scoped_prompt_explain_mode_mentions_read_only():
    prompt = build_scoped_prompt(PY_TRACEBACK, "app.py", 42, mode="explain")
    assert "app.py" in prompt
    assert "42" in prompt
    assert "READ-ONLY" in prompt or "read-only" in prompt.lower()
    assert PY_TRACEBACK.split("\n")[-1] in prompt


def test_build_scoped_prompt_fix_mode_mentions_minimal_change():
    prompt = build_scoped_prompt(PY_TRACEBACK, "app.py", 42, mode="fix")
    assert "minimal" in prompt.lower()


def test_build_scoped_prompt_extracts_when_not_given():
    prompt = build_scoped_prompt(PY_TRACEBACK, None, None, mode="explain")
    assert "app.py" in prompt
    assert "42" in prompt


def test_build_scoped_prompt_never_dumps_whole_repo():
    prompt = build_scoped_prompt(PY_TRACEBACK, "app.py", 42, mode="explain")
    assert "do not explore or summarize the rest of the repository" in prompt.lower() or (
        "only look at that file" in prompt.lower()
    )


def test_build_scoped_prompt_invalid_mode_raises_value_error():
    try:
        build_scoped_prompt(PY_TRACEBACK, None, None, mode="destroy")
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for invalid mode")


# --- handoff.py: no agent available -------------------------------------


def test_handoff_explain_no_agent_available_returns_message_not_raise():
    with patch("ohnoo.agents.detect.shutil.which", return_value=None):
        result = handoff.explain(PY_TRACEBACK)
    assert "no agentic cli found" in result.lower()


def test_handoff_fix_no_agent_available_returns_failure_fixresult():
    with patch("ohnoo.agents.detect.shutil.which", return_value=None):
        result = handoff.fix(PY_TRACEBACK)
    assert isinstance(result, FixResult)
    assert result.success is False
    assert result.error is not None


# --- handoff.py: agent available, subprocess mocked ----------------------


def test_handoff_explain_with_claude_available_returns_stdout():
    fake_which = lambda name: "/usr/bin/claude" if name == "claude" else None
    fake_run_result = subprocess.CompletedProcess(
        args=["claude"], returncode=0, stdout="This crashed because requests isn't installed.",
        stderr="",
    )
    with patch("ohnoo.agents.detect.shutil.which", side_effect=fake_which), patch(
        "ohnoo.agents._common.subprocess.run", return_value=fake_run_result
    ) as mock_run:
        result = handoff.explain(PY_TRACEBACK, cwd="/tmp/project")

    assert result == "This crashed because requests isn't installed."
    args, _kwargs = mock_run.call_args
    assert args[0][:2] == ["claude", "-p"]
    assert "--allowedTools" in args[0]
    assert "Edit" not in args[0][args[0].index("--allowedTools") + 1]


def test_handoff_fix_with_claude_available_captures_diff_via_git():
    fake_which = lambda name: "/usr/bin/claude" if name == "claude" else None
    fake_claude_result = subprocess.CompletedProcess(
        args=["claude"], returncode=0, stdout="Fixed it.", stderr=""
    )
    fake_git_result = subprocess.CompletedProcess(
        args=["git", "diff"], returncode=0, stdout="diff --git a/app.py b/app.py\n...", stderr=""
    )

    def fake_run(args, cwd, capture_output, text, timeout, check):
        if args[0] == "claude":
            return fake_claude_result
        if args[0] == "git":
            return fake_git_result
        raise AssertionError(f"unexpected command: {args}")

    with patch("ohnoo.agents.detect.shutil.which", side_effect=fake_which), patch(
        "ohnoo.agents._common.subprocess.run", side_effect=fake_run
    ):
        result = handoff.fix(PY_TRACEBACK, cwd="/tmp/project")

    assert isinstance(result, FixResult)
    assert result.success is True
    assert result.stdout == "Fixed it."
    assert "diff --git" in result.diff
    assert result.diff_captured_after_run is True


def test_handoff_fix_falls_back_to_codex_when_claude_absent():
    fake_which = lambda name: "/usr/bin/codex" if name == "codex" else None
    fake_codex_result = subprocess.CompletedProcess(
        args=["codex"], returncode=0, stdout="Applied fix.", stderr=""
    )
    fake_git_result = subprocess.CompletedProcess(
        args=["git", "diff"], returncode=0, stdout="", stderr=""
    )

    def fake_run(args, cwd, capture_output, text, timeout, check):
        if args[0] == "codex":
            assert args == ["codex", "exec", args[2]]
            return fake_codex_result
        if args[0] == "git":
            return fake_git_result
        raise AssertionError(f"unexpected command: {args}")

    with patch("ohnoo.agents.detect.shutil.which", side_effect=fake_which), patch(
        "ohnoo.agents._common.subprocess.run", side_effect=fake_run
    ):
        result = handoff.fix(PY_TRACEBACK, cwd="/tmp/project")

    assert result.success is True
    assert result.stdout == "Applied fix."


def test_invoke_explain_handles_missing_binary_gracefully():
    with patch("ohnoo.agents._common.subprocess.run", side_effect=FileNotFoundError):
        result = handoff.explain(PY_TRACEBACK)
    # No agent detected at all in this env (or mocked away) -> graceful message either way
    assert isinstance(result, str)


# --- cost warning ---------------------------------------------------------


def test_should_warn_this_session_is_true_once_then_false():
    # Reset module-level flag to test in isolation.
    handoff._warned_this_process = False
    assert handoff.should_warn_this_session() is True
    assert handoff.should_warn_this_session() is False
    handoff._warned_this_process = False


def test_cost_warning_text_mentions_billing():
    text = handoff.cost_warning_text()
    assert "bill" in text.lower()
