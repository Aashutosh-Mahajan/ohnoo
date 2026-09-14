"""Layer 2 invocation of Codex CLI (`codex`) headlessly."""

from __future__ import annotations

from ohnoo.agents._common import FixResult, invoke_fix_subprocess, run_cli


def invoke_explain(prompt: str, cwd: str | None = None) -> str:
    """Run `codex exec` and return its stdout text.

    Codex exec has no fine-grained read-only tool flag like claude's
    --allowedTools, so the prompt itself is what constrains it to
    diagnosis-only (see prompt_builder.build_scoped_prompt mode="explain").
    Never raises — returns a message describing the failure instead.
    """
    result = run_cli(["codex", "exec", prompt], cwd=cwd)
    if result is None:
        return "ohnoo: could not invoke codex (binary missing, timed out, or errored)."
    if result.returncode != 0:
        return f"ohnoo: codex exited with an error: {result.stderr.strip() or 'unknown error'}"
    return result.stdout


def invoke_fix(prompt: str, cwd: str | None = None) -> FixResult:
    """Run `codex exec` (which may edit files directly), then capture `git diff` in cwd.

    See FixResult docstring: the diff is captured after the run, not before.
    """
    return invoke_fix_subprocess(["codex", "exec", prompt], cwd=cwd, binary_name="codex")
