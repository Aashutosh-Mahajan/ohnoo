"""Tests for the Layer 1 pattern loader's fail-safe behavior.

A single malformed or invalid community-contributed pattern must never
crash pattern loading/matching for every other pattern -- Layer 1 is
promised to never fail (see CLAUDE.md section 2).
"""

import json

from ohnoo.patterns import Fix, Pattern, _load_file, find_match


def test_load_file_skips_malformed_entry_but_keeps_valid_ones(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text(
        json.dumps(
            [
                {"id": "missing-required-keys"},
                {
                    "id": "valid-one",
                    "language": "python",
                    "matcher": {"type": "substring", "pattern": "boom"},
                    "jokes": ["oops {x}"],
                    "fix": {"summary": "fix it", "command": ""},
                },
            ]
        ),
        encoding="utf-8",
    )
    patterns = _load_file(path)
    assert len(patterns) == 1
    assert patterns[0].id == "valid-one"


def test_load_file_returns_empty_list_for_corrupt_json(tmp_path):
    path = tmp_path / "corrupt.json"
    path.write_text("this is not { valid json", encoding="utf-8")
    assert _load_file(path) == []


def test_load_file_returns_empty_list_for_non_array_json(tmp_path):
    path = tmp_path / "notarray.json"
    path.write_text(json.dumps({"not": "a list"}), encoding="utf-8")
    assert _load_file(path) == []


def test_pattern_with_invalid_regex_never_matches_instead_of_raising():
    pattern = Pattern(
        id="broken-regex",
        language="generic",
        matcher_type="regex",
        matcher_pattern="(unclosed",
        jokes=["nope"],
        fix=Fix(summary="", command=""),
    )
    assert pattern.match("anything") is None
    # Second call exercises the cached-failure path.
    assert pattern.match("anything else") is None


def test_find_match_skips_a_broken_pattern_and_still_matches_a_later_one():
    broken = Pattern(
        id="broken",
        language="generic",
        matcher_type="regex",
        matcher_pattern="(unclosed",
        jokes=["nope"],
        fix=Fix(summary="", command=""),
    )
    working = Pattern(
        id="working",
        language="generic",
        matcher_type="substring",
        matcher_pattern="kaboom",
        jokes=["boom"],
        fix=Fix(summary="", command=""),
    )
    pattern, slots = find_match("this is a kaboom error", patterns=[broken, working])
    assert pattern is working
    assert slots == {}
