"""zsh hook: tees stderr to a log file and calls `ohnoo check` after a non-zero exit."""

from __future__ import annotations

import os
from pathlib import Path

from ohnoo.hook.common import install_block

RC_FILE = "~/.zshrc"

_BODY = """\
export OHNOO_LOG="${OHNOO_LOG:-$HOME/.cache/ohnoo/stderr.log}"
mkdir -p "$(dirname "$OHNOO_LOG")"
if [ -z "$OHNOO_STDERR_TEE" ]; then
  export OHNOO_STDERR_TEE=1
  exec 2> >(tee -a "$OHNOO_LOG" >&2)
fi

__ohnoo_precmd() {
  local __ohnoo_exit=$?
  if [ "$__ohnoo_exit" -ne 0 ]; then
    ohnoo check --exit-code "$__ohnoo_exit" --log "$OHNOO_LOG" --last-command "$(fc -ln -1 2>/dev/null)"
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


def install() -> tuple[Path, bool]:
    override = os.environ.get("OHNOO_ZSH_RC")
    rc_path = Path(override).expanduser() if override else Path(RC_FILE).expanduser()
    return install_block(rc_path, _BODY)
