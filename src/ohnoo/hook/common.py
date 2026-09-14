"""Shared idempotent rc-file patching used by every shell's hook installer."""

from __future__ import annotations

from pathlib import Path

BEGIN_MARKER = "# >>> ohnoo hook >>>"
END_MARKER = "# <<< ohnoo hook <<<"


def block(body: str) -> str:
    return f"\n{BEGIN_MARKER}\n{body.rstrip()}\n{END_MARKER}\n"


def install_block(rc_path: Path, body: str) -> tuple[Path, bool]:
    """Append the hook block to rc_path unless it's already present.

    Returns (rc_path, installed) where installed is False if the block already existed.
    """
    rc_path.parent.mkdir(parents=True, exist_ok=True)
    existing = rc_path.read_text(encoding="utf-8") if rc_path.exists() else ""

    if BEGIN_MARKER in existing:
        return rc_path, False

    with rc_path.open("a", encoding="utf-8") as f:
        f.write(block(body))

    return rc_path, True


def uninstall_block(rc_path: Path) -> bool:
    """Remove a previously installed hook block. Returns True if something was removed."""
    if not rc_path.exists():
        return False

    text = rc_path.read_text(encoding="utf-8")
    start = text.find(BEGIN_MARKER)
    end = text.find(END_MARKER)
    if start == -1 or end == -1:
        return False

    end += len(END_MARKER)
    new_text = text[:start].rstrip("\n") + "\n" + text[end:].lstrip("\n")
    rc_path.write_text(new_text, encoding="utf-8")
    return True
