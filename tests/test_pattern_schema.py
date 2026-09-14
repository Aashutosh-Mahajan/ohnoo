"""Validates every pattern in src/ohnoo/patterns/*.json against schema.json."""

import json

import jsonschema
import pytest

from ohnoo.patterns import _NON_PATTERN_FILES, PATTERNS_DIR

SCHEMA = json.loads((PATTERNS_DIR / "schema.json").read_text(encoding="utf-8"))
PATTERN_FILES = sorted(p for p in PATTERNS_DIR.glob("*.json") if p.name not in _NON_PATTERN_FILES)


@pytest.mark.parametrize("path", PATTERN_FILES, ids=lambda p: p.name)
def test_pattern_file_is_array_of_valid_patterns(path):
    entries = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(entries, list), f"{path} must contain a JSON array"
    for entry in entries:
        jsonschema.validate(entry, SCHEMA)


def test_pattern_ids_are_globally_unique():
    seen = set()
    for path in PATTERN_FILES:
        for entry in json.loads(path.read_text(encoding="utf-8")):
            pid = entry["id"]
            assert pid not in seen, f"duplicate pattern id: {pid}"
            seen.add(pid)


def test_every_regex_matcher_compiles():
    import re

    for path in PATTERN_FILES:
        for entry in json.loads(path.read_text(encoding="utf-8")):
            if entry["matcher"]["type"] == "regex":
                re.compile(entry["matcher"]["pattern"])
