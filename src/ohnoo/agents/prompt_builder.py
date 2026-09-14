"""Builds scoped prompts for Layer 2 CLI agent handoff.

The prompt is built from the traceback text plus, at most, the single
failing file/line — never the whole repo (CLAUDE.md section 2, Layer 2).
"""

from __future__ import annotations

import re

# Python: File "path/to/file.py", line 42, in <module>
_PYTHON_FRAME_RE = re.compile(r'File "([^"]+)", line (\d+)')

# Node/JS: at foo (path/to/file.js:42:7)  OR  at path/to/file.js:42:7
_NODE_FRAME_RE = re.compile(r"at (?:.*\()?([^\s()]+):(\d+):\d+\)?")

# Generic fallback: path/to/file.ext:42
_GENERIC_FRAME_RE = re.compile(r"([./\w\-]+\.\w+):(\d+)\b")


def extract_file_line(traceback_text: str) -> tuple[str | None, int | None]:
    """Best-effort extraction of (file_path, line_number) from a traceback.

    Tries Python's ``File "path", line N`` form, then Node's
    ``at ... (path:N:col)`` form, then a generic ``path:N`` form. Returns
    (None, None) if nothing matches. Never raises.
    """
    if not traceback_text:
        return None, None

    try:
        matches = _PYTHON_FRAME_RE.findall(traceback_text)
        if matches:
            path, line = matches[-1]
            return path, int(line)

        matches = _NODE_FRAME_RE.findall(traceback_text)
        if matches:
            path, line = matches[0]
            return path, int(line)

        matches = _GENERIC_FRAME_RE.findall(traceback_text)
        if matches:
            path, line = matches[0]
            return path, int(line)
    except (ValueError, TypeError):
        return None, None

    return None, None


def build_scoped_prompt(
    traceback_text: str,
    file_path: str | None,
    line_number: int | None,
    mode: str,
) -> str:
    """Build a bounded prompt describing the error for an agentic CLI.

    ``mode`` is "explain" (read-only diagnosis, no edits) or "fix" (make
    the minimal edit needed, nothing else). If ``file_path``/``line_number``
    are not given, they are best-effort extracted from ``traceback_text``.
    """
    if mode not in ("explain", "fix"):
        raise ValueError(f"mode must be 'explain' or 'fix', got {mode!r}")

    if file_path is None and line_number is None:
        file_path, line_number = extract_file_line(traceback_text)

    lines = [
        "A shell command just crashed. Here is the exact error output:",
        "",
        "```",
        traceback_text.strip(),
        "```",
        "",
    ]

    if file_path is not None:
        location = f"The failing location appears to be {file_path}"
        if line_number is not None:
            location += f", line {line_number}"
        location += "."
        lines.append(location)
        lines.append(
            "Only look at that file (and directly related files if strictly necessary "
            "to understand the error) — do not explore or summarize the rest of the "
            "repository."
        )
    else:
        lines.append(
            "No specific file/line could be extracted from the error text above — "
            "use only the information in the error output."
        )

    lines.append("")

    if mode == "explain":
        lines.append(
            "Diagnose the root cause in a few clear sentences. This is READ-ONLY: "
            "do not edit, create, or delete any files, and do not run commands that "
            "change repository state."
        )
    else:
        lines.append(
            "Make the minimal code change needed to fix this specific error, and "
            "nothing else. Do not refactor unrelated code, do not touch unrelated "
            "files, and do not make stylistic changes beyond what's required to fix "
            "the bug."
        )

    return "\n".join(lines)
