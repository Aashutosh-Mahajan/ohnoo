"""fish hook.

fish has no bash/zsh-style `>(...)` process substitution for writing, so this
hook can't transparently tee stderr to a log file the way bash.py/zsh.py do.
Instead it reacts to a non-zero exit via the `fish_postexec` event and points
the user at manual pipe mode (`cmd 2>&1 | ohnoo`) with the actual failing
command already filled in, rather than pretending to have data it doesn't.
"""

from __future__ import annotations

import os
from pathlib import Path

from ohnoo.hook.common import install_block, uninstall_block

RC_FILE = "~/.config/fish/config.fish"

_BODY = """\
function __ohnoo_postexec --on-event fish_postexec
    set -l __ohnoo_exit $status
    if test $__ohnoo_exit -ne 0
        echo "ohnoo: exited $__ohnoo_exit. fish can't auto-capture stderr yet -- retry as: $argv 2>&1 | ohnoo" >&2
    end
end
"""


def _rc_path() -> Path:
    override = os.environ.get("OHNOO_FISH_CONFIG")
    return Path(override).expanduser() if override else Path(RC_FILE).expanduser()


def install() -> list[tuple[Path, bool]]:
    return [install_block(_rc_path(), _BODY)]


def uninstall() -> list[tuple[Path, bool]]:
    rc_path = _rc_path()
    return [(rc_path, uninstall_block(rc_path))]
