"""Layer 1 — the offline pattern engine.

Loads pattern definitions from the JSON files in this directory, matches them
against captured error text, fills mad-libs slots, and picks a joke variant.
"""

from __future__ import annotations

import json
import random
import re
from dataclasses import dataclass, field
from pathlib import Path

PATTERNS_DIR = Path(__file__).parent

# Files that hold pattern definitions, not patterns themselves.
_NON_PATTERN_FILES = {"schema.json"}


@dataclass
class Fix:
    summary: str
    command: str

    def render(self, slots: dict) -> Fix:
        return Fix(
            summary=_fill(self.summary, slots),
            command=_fill_command(self.command, slots),
        )


@dataclass
class Pattern:
    id: str
    language: str
    matcher_type: str
    matcher_pattern: str
    jokes: list
    fix: Fix
    title: str = ""
    matcher_flags: list = field(default_factory=list)
    slots: dict = field(default_factory=dict)
    vibes: dict = field(default_factory=dict)
    personality_tag: str = ""
    tags: list = field(default_factory=list)

    # False is a sentinel meaning "tried to compile, pattern is invalid" --
    # distinct from None, which means "not compiled yet".
    _compiled: re.Pattern | bool | None = field(default=None, repr=False, compare=False)

    def _compile(self) -> re.Pattern | None:
        if self.matcher_type != "regex":
            return None
        if self._compiled is None:
            flags = 0
            if "ignorecase" in self.matcher_flags:
                flags |= re.IGNORECASE
            if "multiline" in self.matcher_flags:
                flags |= re.MULTILINE
            if "dotall" in self.matcher_flags:
                flags |= re.DOTALL
            try:
                self._compiled = re.compile(self.matcher_pattern, flags)
            except re.error:
                # A malformed community-contributed pattern must never take
                # down every other pattern's matching -- treat it as one
                # that never matches instead of raising.
                self._compiled = False
        return self._compiled or None

    def match(self, text: str):
        """Return a dict of filled slot values if this pattern matches, else None."""
        if self.matcher_type == "regex":
            compiled = self._compile()
            if compiled is None:
                return None
            m = compiled.search(text)
            if not m:
                return None
            groups = m.groupdict() if m.groupdict() else {}
            # Also expose numbered groups via the `slots` mapping (e.g. {"1": "module_name"}).
            for idx, name in self.slots.items():
                try:
                    groups[name] = m.group(int(idx))
                except (IndexError, ValueError):
                    continue
            return {k: v for k, v in groups.items() if v is not None}
        if self.matcher_type == "exception_type":
            if re.search(rf"\b{re.escape(self.matcher_pattern)}\b", text):
                return {}
            return None
        if self.matcher_type == "substring":
            if self.matcher_pattern in text:
                return {}
            return None
        return None

    def joke(self, slots: dict, vibe: str = "default") -> str:
        pool = self.vibes.get(vibe) if vibe != "default" else None
        if not pool:
            pool = self.jokes
        template = random.choice(pool)
        return _fill(template, slots)

    def rendered_fix(self, slots: dict) -> Fix:
        return self.fix.render(slots)


_SLOT_RE = re.compile(r"\{(\w+)\}")


def _fill(template: str, slots: dict) -> str:
    def repl(m: re.Match) -> str:
        key = m.group(1)
        return str(slots.get(key, m.group(0)))

    return _SLOT_RE.sub(repl, template)


def _shell_quote(value: str) -> str:
    """POSIX single-quote a value so a shell can only ever see it as inert
    literal data, never as syntax, if a user copies a suggested fix command
    verbatim. Slot values come from regex captures on untrusted crash text
    (which may itself come from an untrusted package/script) -- a captured
    path or ref could contain `$(...)`, backticks, `;`, etc.
    """
    return "'" + str(value).replace("'", "'\\''") + "'"


def _fill_command(template: str, slots: dict) -> str:
    """Like _fill(), but every substituted slot value is shell-quoted.

    Only for Fix.command, which is a literal shell command a user might
    copy-paste and run -- never for jokes or the fix summary, which are
    prose and shouldn't be dressed up with stray quote marks.
    """

    def repl(m: re.Match) -> str:
        key = m.group(1)
        if key not in slots:
            return m.group(0)
        return _shell_quote(slots[key])

    return _SLOT_RE.sub(repl, template)


def _build_pattern(entry: dict) -> Pattern:
    fix = Fix(summary=entry["fix"]["summary"], command=entry["fix"]["command"])
    return Pattern(
        id=entry["id"],
        language=entry["language"],
        title=entry.get("title", ""),
        matcher_type=entry["matcher"]["type"],
        matcher_pattern=entry["matcher"]["pattern"],
        matcher_flags=entry["matcher"].get("flags", []),
        slots=entry.get("slots", {}),
        jokes=entry["jokes"],
        vibes=entry.get("vibes", {}),
        fix=fix,
        personality_tag=entry.get("personality_tag", ""),
        tags=entry.get("tags", []),
    )


def _load_file(path: Path) -> list:
    """Load one pattern file, skipping (not crashing on) malformed entries.

    A single bad community-contributed pattern -- a missing required key, a
    wrong type -- must never break every other pattern in the database, or
    the CLI, for every user. Layer 1 is promised to never fail.
    """
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return []
    if not isinstance(data, list):
        return []

    patterns = []
    for entry in data:
        try:
            patterns.append(_build_pattern(entry))
        except (KeyError, TypeError, AttributeError):
            continue
    return patterns


def load_all_patterns() -> list:
    patterns = []
    for path in sorted(PATTERNS_DIR.glob("*.json")):
        if path.name in _NON_PATTERN_FILES:
            continue
        patterns.extend(_load_file(path))
    return patterns


def find_match(text: str, patterns: list | None = None):
    """Return (Pattern, slots) for the first pattern that matches `text`, else (None, None)."""
    if patterns is None:
        patterns = load_all_patterns()
    for pattern in patterns:
        try:
            slots = pattern.match(text)
        except re.error:
            continue
        if slots is not None:
            return pattern, slots
    return None, None
