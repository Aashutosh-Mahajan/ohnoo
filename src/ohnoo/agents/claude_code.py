"""Layer 2 invocation of Claude Code (`claude`) headlessly."""

from __future__ import annotations

from ohnoo.agents._common import FixResult, capture_git_diff, run_cli


def invoke_explain(prompt: str, cwd: str | None = None) -> str:
    """Run `claude -p` in read-only mode and return its stdout text.

    Never raises — returns a message describing the failure instead.
    """
    result = run_cli(["claude", "-p", prompt, "--allowedTools", "Read"], cwd=cwd)
    if result is None:
        return "ohnoo: could not invoke claude (binary missing, timed out, or errored)."
    if result.returncode != 0:
        return f"ohnoo: claude exited with an error: {result.stderr.strip() or 'unknown error'}"
    return result.stdout


def invoke_fix(prompt: str, cwd: str | None = None) -> FixResult:
    """Run `claude -p` with edit tools allowed, then capture `git diff` in cwd.

    See FixResult docstring: the diff is captured after the run, not before.
    """
    result = run_cli(["claude", "-p", prompt, "--allowedTools", "Read,Edit,Bash"], cwd=cwd)
    if result is None:
        return FixResult(
            success=False,
            stdout="",
            diff="",
            error="could not invoke claude (binary missing, timed out, or errored)",
        )
    diff = capture_git_diff(cwd)
    if result.returncode != 0:
        return FixResult(
            success=False,
            stdout=result.stdout,
            diff=diff,
            error=result.stderr.strip() or "claude exited with a nonzero status",
        )
    return FixResult(success=True, stdout=result.stdout, diff=diff, error=None)
