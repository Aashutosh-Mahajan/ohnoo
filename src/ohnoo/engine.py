"""Ties the pattern engine together into a single diagnose() call used by the CLI."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path

import click

from ohnoo.patterns import find_match, load_all_patterns

_patterns_cache = None
_LAST_ROAST_ENV = "OHNOO_LAST_ROAST_FILE"


def _patterns():
    global _patterns_cache
    if _patterns_cache is None:
        _patterns_cache = load_all_patterns()
    return _patterns_cache


@dataclass
class Diagnosis:
    matched: bool
    joke: str = ""
    fix_summary: str = ""
    fix_command: str = ""
    pattern_id: str = ""
    language: str = ""

    def render(self) -> str:
        if not self.matched:
            return click.style("ohnoo: ", fg="yellow", bold=True) + (
                "no known pattern matched that error. Try `ohnoo explain` or `ohnoo fix` "
                "if you have an AI coding agent installed, or `ohnoo setup-ai` for a "
                "hosted fallback."
            )
        lines = [click.style("ohnoo: ", fg="red", bold=True) + self.joke]
        if self.fix_command:
            lines.append(click.style("  fix: ", fg="green", bold=True) + self.fix_command)
        elif self.fix_summary:
            lines.append(click.style("  fix: ", fg="green", bold=True) + self.fix_summary)
        return "\n".join(lines)


def diagnose(text: str, vibe: str = "default", last_command: str = "") -> Diagnosis:
    pattern, slots = find_match(text, _patterns())
    if pattern is None:
        return Diagnosis(matched=False)

    joke = pattern.joke(slots, vibe=vibe)
    fix = pattern.rendered_fix(slots)
    return Diagnosis(
        matched=True,
        joke=joke,
        fix_summary=fix.summary,
        fix_command=fix.command,
        pattern_id=pattern.id,
        language=pattern.language,
    )


def _last_roast_path() -> Path:
    override = os.environ.get(_LAST_ROAST_ENV)
    if override:
        return Path(override)
    return Path.home() / ".cache" / "ohnoo" / "last_roast.json"


def save_last(diagnosis: Diagnosis, command: str = "") -> None:
    """Cache the last matched diagnosis so `ohnoo share` can render it later.

    Never raises — a failure to cache must not break the main roast flow.
    """
    try:
        path = _last_roast_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"diagnosis": asdict(diagnosis), "command": command}
        with path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
    except OSError:
        pass


def load_last() -> tuple[Diagnosis, str] | None:
    """Load the last cached diagnosis, or None if there isn't one."""
    path = _last_roast_path()
    try:
        with path.open("r", encoding="utf-8") as f:
            payload = json.load(f)
        return Diagnosis(**payload["diagnosis"]), payload.get("command", "")
    except (OSError, ValueError, KeyError, TypeError):
        return None
