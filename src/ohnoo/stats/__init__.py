"""--stats: local roast usage tracking.

Keeps a local, non-telemetric flat-file JSON log of roast counts and
categories for the `ohnoo --stats` command. Nothing here ever makes a network
call, and recording a roast must never be able to break the main roast flow.
"""

from __future__ import annotations

import json
import os
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

_ENV_OVERRIDE = "OHNOO_STATS_FILE"


def _stats_path() -> Path:
    override = os.environ.get(_ENV_OVERRIDE)
    if override:
        return Path(override)
    return Path.home() / ".local" / "share" / "ohnoo" / "stats.json"


def _load_records(path: Path) -> list[dict]:
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return []
    if not isinstance(data, list):
        return []
    return [r for r in data if isinstance(r, dict)]


def record_roast(pattern_id: str, language: str) -> None:
    """Append a roast record. Never raises — I/O errors are swallowed."""
    try:
        path = _stats_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        records = _load_records(path)
        records.append(
            {
                "pattern_id": pattern_id,
                "language": language,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
        with path.open("w", encoding="utf-8") as f:
            json.dump(records, f, indent=2)
    except OSError:
        pass


def _prettify(pattern_id: str) -> str:
    """Turn a pattern id into a rough human-readable label.

    Best-effort heuristic, e.g. "py-module-not-found" -> "module not found".
    Doesn't need to be exhaustive — just readable.
    """
    label = re.sub(r"^(py|node|git|docker|npm|pip)-", "", pattern_id)
    label = label.replace("-", " ").strip()
    return label or pattern_id


def summary() -> str:
    """Return a human-readable one-or-two-line usage summary."""
    records = _load_records(_stats_path())
    if not records:
        return "No roasts yet. Go break something."

    total = len(records)
    counts = Counter(r.get("pattern_id", "unknown") for r in records)
    top_id, _ = counts.most_common(1)[0]
    label = _prettify(top_id)

    times = "time" if total == 1 else "times"
    return f"Roasted {total} {times} this month, mostly for {label}."
