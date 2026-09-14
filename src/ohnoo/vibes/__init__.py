"""Personality packs (Phase 2, partially implemented).

Vibes are already selectable per-pattern via the `vibes` field in the pattern
JSON files (see patterns/__init__.py: Pattern.joke(vibe=...)). What's missing
for full Phase 2 completion is CLI ergonomics: persisting a default --vibe
choice and filling out vibe coverage across all patterns.
"""

KNOWN_VIBES = ["default", "gordon-ramsay", "zen", "sarcastic-senior-dev"]


def list_vibes() -> list[str]:
    """Return the list of known vibe/personality names."""
    return list(KNOWN_VIBES)


def resolve_vibe(name: str) -> str:
    """Resolve a user-supplied vibe name to a known vibe.

    Never raises: an unknown/blank/garbage name degrades to "default" rather
    than crashing the roast flow, per the project's graceful-degradation rule.
    """
    if name in KNOWN_VIBES:
        return name
    return "default"
