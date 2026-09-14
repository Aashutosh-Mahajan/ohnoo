"""Tests for the vibes system: resolution helpers and pattern-file coverage."""

import json

from ohnoo.engine import diagnose
from ohnoo.patterns import _NON_PATTERN_FILES, PATTERNS_DIR
from ohnoo.vibes import KNOWN_VIBES, list_vibes, resolve_vibe


def test_list_vibes_returns_known_vibes():
    assert list_vibes() == KNOWN_VIBES
    # Must be a copy, not the live list, so callers can't mutate global state.
    assert list_vibes() is not KNOWN_VIBES


def test_resolve_vibe_passes_through_known_names():
    for vibe in KNOWN_VIBES:
        assert resolve_vibe(vibe) == vibe


def test_resolve_vibe_falls_back_to_default_for_unknown_input():
    assert resolve_vibe("nonexistent-vibe") == "default"
    assert resolve_vibe("") == "default"
    assert resolve_vibe("GORDON-RAMSAY") == "default"  # case-sensitive, no crash


def test_resolve_vibe_never_raises_on_garbage_input():
    for garbage in (None, 123, [], {}):
        assert resolve_vibe(garbage) == "default"


def test_sarcastic_senior_dev_has_at_least_15_pattern_overrides():
    count = 0
    for path in sorted(PATTERNS_DIR.glob("*.json")):
        if path.name in _NON_PATTERN_FILES:
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        for entry in data:
            if "sarcastic-senior-dev" in entry.get("vibes", {}):
                count += 1
    assert count >= 15


def test_sarcastic_senior_dev_spread_across_multiple_files():
    files_with_coverage = set()
    for path in sorted(PATTERNS_DIR.glob("*.json")):
        if path.name in _NON_PATTERN_FILES:
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        if any("sarcastic-senior-dev" in entry.get("vibes", {}) for entry in data):
            files_with_coverage.add(path.name)
    assert len(files_with_coverage) >= 3


def test_sarcastic_senior_dev_vibe_used_when_present():
    text = "Traceback (most recent call last):\nModuleNotFoundError: No module named 'requests'"
    result = diagnose(text, vibe="sarcastic-senior-dev")
    assert result.matched
    assert "requests" in result.joke
