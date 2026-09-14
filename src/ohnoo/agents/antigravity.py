"""Layer 2 invocation of Antigravity CLI (`agy`) headlessly."""

from __future__ import annotations

from ohnoo.agents._common import FixResult, invoke_fix_subprocess, run_cli


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
    return invoke_fix_subprocess(["agy", "exec", prompt], cwd=cwd, binary_name="agy")
