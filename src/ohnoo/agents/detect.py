"""Detection of installed agentic CLIs on $PATH (Layer 2, Phase 3).

Priority order defaults to claude (Claude Code) > codex (Codex CLI) > agy
(Antigravity CLI), per CLAUDE.md section 2. Callers may override the
priority list to reconfigure it.
"""

from __future__ import annotations

import shutil

DEFAULT_PRIORITY = ["claude", "codex", "agy"]


def detect_available_agents(priority: list[str] | None = None) -> list[str]:
    """Return the subset of agent names found on $PATH, in priority order.

    ``priority`` defaults to :data:`DEFAULT_PRIORITY` (claude, codex, agy).
    """
    order = priority if priority is not None else DEFAULT_PRIORITY
    return [name for name in order if shutil.which(name) is not None]


def pick_agent(preferred: list[str] | None = None) -> str | None:
    """Return the first available agent from ``preferred`` (default priority), or None."""
    priority = preferred if preferred is not None else DEFAULT_PRIORITY
    available = detect_available_agents(priority)
    return available[0] if available else None
