"""Layer 2 invocation of Antigravity CLI (`agy`) headlessly."""

from __future__ import annotations

from ohnoo.agents._common import FixResult, capture_git_diff, run_cli


def invoke_explain(prompt: str, cwd: str | None = None) -> str:
    """Run `agy exec` and return its stdout text.

    agy exec has no fine-grained read-only tool flag, so the prompt itself
    is what constrains it to diagnosis-only (see
    prompt_builder.build_scoped_prompt mode="explain"). Never raises —
    returns a message describing the failure instead.
    """
    result = run_cli(["agy", "exec", prompt], cwd=cwd)
    if result is None:
        return "ohnoo: could not invoke agy (binary missing, timed out, or errored)."
    if result.returncode != 0:
        return f"ohnoo: agy exited with an error: {result.stderr.strip() or 'unknown error'}"
    return result.stdout


def invoke_fix(prompt: str, cwd: str | None = None) -> FixResult:
    """Run `agy exec` (which may edit files directly), then capture `git diff` in cwd.

    See FixResult docstring: the diff is captured after the run, not before.
    """
    result = run_cli(["agy", "exec", prompt], cwd=cwd)
    if result is None:
        return FixResult(
            success=False,
            stdout="",
            diff="",
            error="could not invoke agy (binary missing, timed out, or errored)",
        )
    diff = capture_git_diff(cwd)
    if result.returncode != 0:
        return FixResult(
            success=False,
            stdout=result.stdout,
            diff=diff,
            error=result.stderr.strip() or "agy exited with a nonzero status",
        )
    return FixResult(success=True, stdout=result.stdout, diff=diff, error=None)
