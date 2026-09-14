"""Shared helpers for Layer 2 agent invocation modules.

Not part of the public API surface (hence the leading underscore) — the
public interface is invoke_explain()/invoke_fix() on each of claude_code,
codex, and antigravity.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass

DEFAULT_TIMEOUT_SECONDS = 120


@dataclass
class FixResult:
    """Result of a headless --fix invocation.

    NOTE: today's headless agent CLIs (claude -p, codex exec, agy exec) can
    write files to disk directly when given edit/bash tools, so true
    pre-write confirmation isn't possible with current flags — the diff
    below is captured via `git diff` AFTER the agent already ran, which is
    the best available approximation until these CLIs support a
    dry-run-then-confirm flow (e.g. running read-only first, then a second
    invocation to apply an approved patch).
    """

    success: bool
    stdout: str
    diff: str
    error: str | None = None
    diff_captured_after_run: bool = True


def run_cli(args: list[str], cwd: str | None, timeout: int = DEFAULT_TIMEOUT_SECONDS):
    """Run a subprocess, never raising. Returns a CompletedProcess-like object.

    On failure to even launch the process (binary missing, timeout, etc.)
    returns None; callers should treat that as a failure.
    """
    try:
        return subprocess.run(
            args,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None


def capture_git_diff(cwd: str | None) -> str:
    """Best-effort `git diff` capture in cwd. Returns "" if not a git repo or on error."""
    result = run_cli(["git", "diff"], cwd=cwd, timeout=30)
    if result is None or result.returncode != 0:
        return ""
    return result.stdout
