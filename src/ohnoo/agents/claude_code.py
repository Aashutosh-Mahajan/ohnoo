"""Layer 2 invocation of Claude Code (`claude`) headlessly."""

from __future__ import annotations

from ohnoo.agents._common import FixResult, invoke_fix_subprocess, run_cli


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
    return invoke_fix_subprocess(
        ["claude", "-p", prompt, "--allowedTools", "Read,Edit,Bash"], cwd=cwd, binary_name="claude"
    )
