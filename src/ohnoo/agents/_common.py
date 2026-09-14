"""Shared helpers for Layer 2 agent invocation modules.

Not part of the public API surface (hence the leading underscore) — the
public interface is invoke_explain()/invoke_fix() on each of claude_code,
codex, and antigravity.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

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

    To make up for that, ``status_before``/``status_after`` capture a
    `git status --porcelain` snapshot from just before and just after the
    agent ran (None if ``cwd`` isn't a git repo / git isn't available), so
    the caller can offer a real "keep or revert" choice once the diff is
    actually visible — see revert_changes() below.
    """

    success: bool
    stdout: str
    diff: str
    error: str | None = None
    diff_captured_after_run: bool = True
    status_before: str | None = None
    status_after: str | None = None


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


def snapshot_git_status(cwd: str | None) -> str | None:
    """Best-effort `git status --porcelain` snapshot. None if not a git repo / no git."""
    result = run_cli(["git", "status", "--porcelain"], cwd=cwd, timeout=30)
    if result is None or result.returncode != 0:
        return None
    return result.stdout


def _porcelain_entries(status_text: str) -> list[tuple[str, str]]:
    entries = []
    for line in status_text.splitlines():
        if not line:
            continue
        status, path = line[:2], line[3:]
        if " -> " in path:  # rename/copy: "old -> new"
            path = path.split(" -> ", 1)[1]
        entries.append((status, path.strip('"')))
    return entries


def revert_changes(cwd: str | None, status_before: str, status_after: str) -> bool:
    """Best-effort revert of exactly what changed between two status snapshots.

    Restores newly modified/staged tracked files with `git checkout --`, and
    deletes newly created untracked files that weren't present before.
    Returns True if anything was reverted, False if there was nothing to do.
    Never raises — this is a best-effort safety net, not a guarantee.
    """
    before_paths = {path for _, path in _porcelain_entries(status_before)}
    changed_tracked = []
    new_untracked = []
    for status, path in _porcelain_entries(status_after):
        if path in before_paths:
            continue
        if status == "??":
            new_untracked.append(path)
        else:
            changed_tracked.append(path)

    if changed_tracked:
        run_cli(["git", "checkout", "--", *changed_tracked], cwd=cwd, timeout=30)

    base = Path(cwd) if cwd else Path.cwd()
    for path in new_untracked:
        try:
            target = (base / path).resolve()
            if target.is_relative_to(base.resolve()) and target.is_file():
                target.unlink()
        except (OSError, ValueError):
            continue

    return bool(changed_tracked or new_untracked)


def invoke_fix_subprocess(args: list[str], cwd: str | None, binary_name: str) -> FixResult:
    """Shared invoke_fix logic for every Layer 2 backend (claude/codex/agy).

    Snapshots git status before running so a caller can later offer to
    revert, runs the agent, then captures the diff and an after-snapshot.
    """
    status_before = snapshot_git_status(cwd)
    result = run_cli(args, cwd=cwd)
    if result is None:
        return FixResult(
            success=False,
            stdout="",
            diff="",
            error=f"could not invoke {binary_name} (binary missing, timed out, or errored)",
            status_before=status_before,
        )
    diff = capture_git_diff(cwd)
    status_after = snapshot_git_status(cwd)
    if result.returncode != 0:
        return FixResult(
            success=False,
            stdout=result.stdout,
            diff=diff,
            error=result.stderr.strip() or f"{binary_name} exited with a nonzero status",
            status_before=status_before,
            status_after=status_after,
        )
    return FixResult(
        success=True,
        stdout=result.stdout,
        diff=diff,
        error=None,
        status_before=status_before,
        status_after=status_after,
    )
