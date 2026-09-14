"""Layer 2 orchestration: pick an agent, build a scoped prompt, invoke it.

Combines detect.py, prompt_builder.py, and the per-agent invoke modules
into the two entry points the CLI needs: explain() and fix().
"""

from __future__ import annotations

from ohnoo.agents import antigravity, claude_code, codex
from ohnoo.agents._common import FixResult
from ohnoo.agents.detect import pick_agent
from ohnoo.agents.prompt_builder import build_scoped_prompt

_AGENT_MODULES = {
    "claude": claude_code,
    "codex": codex,
    "agy": antigravity,
}

NO_AGENT_FOUND_MESSAGE = (
    "ohnoo: no agentic CLI found on $PATH (looked for: claude, codex, agy). "
    "Install one of these to enable Layer 2 diagnosis/fix, or configure Layer 4 "
    "(hosted LLM fallback) with `ohnoo setup-ai`."
)

# Per-process only: a real "once per shell session" would need a file lock /
# on-disk marker keyed to the session, which is out of scope here.
_warned_this_process = False


def should_warn_this_session() -> bool:
    """Return True only the first time this is called in this process.

    Subsequent calls return False. This is a per-process flag, not a true
    per-shell-session one — a fresh `ohnoo` invocation each time (the
    common case for a shell hook) will warn again every time; genuine
    cross-invocation session tracking is out of scope for now.
    """
    global _warned_this_process
    if _warned_this_process:
        return False
    _warned_this_process = True
    return True


def cost_warning_text() -> str:
    """Short message about headless-agent billing, shown once before the first --fix."""
    return (
        "ohnoo: heads up — invoking your AI coding agent headlessly for --fix can be "
        "billed separately from your normal interactive usage, depending on your plan. "
        "This warning is shown once per ohnoo run."
    )


def explain(
    traceback_text: str,
    cwd: str | None = None,
    priority: list[str] | None = None,
) -> str:
    """Pick an available agent and ask it to diagnose the error, read-only.

    Returns the agent's explanation text, or a clear message if no
    agentic CLI is available. Never raises.
    """
    agent_name = pick_agent(priority)
    if agent_name is None:
        return NO_AGENT_FOUND_MESSAGE

    prompt = build_scoped_prompt(traceback_text, None, None, mode="explain")
    module = _AGENT_MODULES[agent_name]
    return module.invoke_explain(prompt, cwd=cwd)


def fix(
    traceback_text: str,
    cwd: str | None = None,
    priority: list[str] | None = None,
) -> FixResult:
    """Pick an available agent and ask it to fix the error, capturing a diff.

    Returns a FixResult; if no agentic CLI is available, returns a FixResult
    with success=False and an explanatory error. Never raises.
    """
    agent_name = pick_agent(priority)
    if agent_name is None:
        return FixResult(
            success=False,
            stdout="",
            diff="",
            error=NO_AGENT_FOUND_MESSAGE,
            diff_captured_after_run=False,
        )

    prompt = build_scoped_prompt(traceback_text, None, None, mode="fix")
    module = _AGENT_MODULES[agent_name]
    return module.invoke_fix(prompt, cwd=cwd)
