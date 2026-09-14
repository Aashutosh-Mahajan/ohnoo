"""Shared idempotent rc-file patching used by every shell's hook installer."""

from __future__ import annotations

import os
import time
from pathlib import Path

BEGIN_MARKER = "# >>> ohnoo hook >>>"
END_MARKER = "# <<< ohnoo hook <<<"


def block(body: str) -> str:
    return f"\n{BEGIN_MARKER}\n{body.rstrip()}\n{END_MARKER}\n"


def _lock_path(rc_path: Path) -> Path:
    return rc_path.parent / f".{rc_path.name}.ohnoo.lock"


def _acquire_lock(lock_path: Path, timeout: float = 5.0) -> bool:
    """Best-effort mutual exclusion via an exclusive-create lockfile.

    Returns True if the lock was actually acquired. On timeout (e.g. a
    stale lock left behind by a crashed process) gives up and returns
    False rather than hanging forever -- the caller proceeds unlocked,
    which is no worse than before this existed.
    """
    deadline = time.monotonic() + timeout
    while True:
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
            return True
        except FileExistsError:
            if time.monotonic() >= deadline:
                return False
            time.sleep(0.05)


def _release_lock(lock_path: Path) -> None:
    try:
        lock_path.unlink()
    except OSError:
        pass


def install_block(rc_path: Path, body: str) -> tuple[Path, bool]:
    """Append the hook block to rc_path unless it's already present.

    Returns (rc_path, installed) where installed is False if the block already existed.

    Guards the read-then-append with a lockfile so two concurrent `ohnoo
    init` runs (e.g. two terminals opening at once) can't both pass the
    "not already present" check and duplicate the hook block.
    """
    rc_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = _lock_path(rc_path)
    locked = _acquire_lock(lock_path)
    try:
        existing = rc_path.read_text(encoding="utf-8") if rc_path.exists() else ""

        if BEGIN_MARKER in existing:
            return rc_path, False

        with rc_path.open("a", encoding="utf-8") as f:
            f.write(block(body))

        return rc_path, True
    finally:
        if locked:
            _release_lock(lock_path)


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
