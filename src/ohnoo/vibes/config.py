"""Persists the user's default --vibe choice across invocations.

Plain-text file, one vibe name, at ~/.config/ohnoo/vibe (overridable via
OHNOO_VIBE_FILE for tests). Deliberately not part of the Layer 4 TOML config
in llm_fallback/config.py -- vibe choice has nothing to do with the hosted
LLM fallback and shouldn't be coupled to it.
"""

from __future__ import annotations

import os
from pathlib import Path

from ohnoo.vibes import KNOWN_VIBES, resolve_vibe

_ENV_OVERRIDE = "OHNOO_VIBE_FILE"


def _vibe_file() -> Path:
    override = os.environ.get(_ENV_OVERRIDE)
    if override:
        return Path(override)
    return Path.home() / ".config" / "ohnoo" / "vibe"


def get_default_vibe() -> str:
    """Return the persisted default vibe, or "default" if none is set/valid."""
    try:
        raw = _vibe_file().read_text(encoding="utf-8").strip()
    except OSError:
        return "default"
    return resolve_vibe(raw)


def set_default_vibe(name: str) -> None:
    """Persist `name` as the default vibe.

    Raises ValueError for a name that isn't a known vibe -- this is an
    explicit user command (`ohnoo vibe <name>`), so unlike resolve_vibe's
    silent runtime fallback, bad input here should be reported, not swallowed.
    """
    if name not in KNOWN_VIBES:
        known = ", ".join(KNOWN_VIBES)
        raise ValueError(f"Unknown vibe {name!r}. Known vibes: {known}")

    path = _vibe_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(name + "\n", encoding="utf-8")
