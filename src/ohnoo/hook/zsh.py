"""zsh hook: tees stderr to a log file and calls `ohnoo check` after a non-zero exit."""

from __future__ import annotations

import os
from pathlib import Path

from ohnoo.hook.common import install_block, uninstall_block

RC_FILE = "~/.zshrc"

_BODY = """\
export OHNOO_LOG="${OHNOO_LOG:-$HOME/.cache/ohnoo/stderr.log}"
mkdir -p "$(dirname "$OHNOO_LOG")"
if [ -f "$OHNOO_LOG" ] && [ "$(wc -c < "$OHNOO_LOG" 2>/dev/null || echo 0)" -gt 5242880 ]; then
  : > "$OHNOO_LOG"
fi
if [ -z "$OHNOO_STDERR_TEE" ]; then
  export OHNOO_STDERR_TEE=1
  exec 2> >(tee -a "$OHNOO_LOG" >&2)
fi

__ohnoo_precmd() {
  local __ohnoo_exit=$?
  if [ "$__ohnoo_exit" -ne 0 ]; then
    OHNOO_LAST_COMMAND="$(fc -ln -1 2>/dev/null)" ohnoo check --exit-code "$__ohnoo_exit"
  fi
  return $__ohnoo_exit
}

autoload -Uz add-zsh-hook 2>/dev/null
if typeset -f add-zsh-hook >/dev/null; then
  add-zsh-hook precmd __ohnoo_precmd
else
  case ";${precmd_functions[*]:-};" in
    *";__ohnoo_precmd;"*) ;;
    *) precmd_functions+=(__ohnoo_precmd) ;;
  esac
fi
"""


def _rc_path() -> Path:
    override = os.environ.get("OHNOO_ZSH_RC")
    return Path(override).expanduser() if override else Path(RC_FILE).expanduser()


def install() -> list[tuple[Path, bool]]:
    return [install_block(_rc_path(), _BODY)]


def uninstall() -> list[tuple[Path, bool]]:
    rc_path = _rc_path()
    return [(rc_path, uninstall_block(rc_path))]
