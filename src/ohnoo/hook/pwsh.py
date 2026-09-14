"""PowerShell hook.

Unlike bash/zsh's `exec 2> >(tee ...)`, PowerShell has a native way to
continuously capture everything a session prints: `Start-Transcript`. This
hook starts a transcript into $env:OHNOO_LOG once per session, then wraps
the `prompt` function (PowerShell's precmd equivalent) to call `ohnoo check`
whenever $LASTEXITCODE is non-zero, chaining to whatever `prompt` function
was already defined (e.g. oh-my-posh) so this hook doesn't clobber it.

Caveat: $LASTEXITCODE only reflects native executable exit codes, not
cmdlet failures surfaced only via $?. That's a real limitation, not a bug.
"""

from __future__ import annotations

import os
from pathlib import Path

from ohnoo.hook.common import install_block

PROFILE_FILE = "~/Documents/PowerShell/Microsoft.PowerShell_profile.ps1"

_BODY = """\
if (-not $env:OHNOO_LOG) { $env:OHNOO_LOG = Join-Path $HOME ".cache/ohnoo/stderr.log" }
New-Item -ItemType Directory -Force -Path (Split-Path $env:OHNOO_LOG) -ErrorAction SilentlyContinue | Out-Null

if (-not $env:OHNOO_TRANSCRIPT_STARTED) {
    $env:OHNOO_TRANSCRIPT_STARTED = "1"
    try { Start-Transcript -Path $env:OHNOO_LOG -Append -Force | Out-Null } catch {}
}

$global:__ohnoo_prev_prompt = $function:prompt

function global:prompt {
    $__ohnoo_exit = $LASTEXITCODE
    if ($__ohnoo_exit -and $__ohnoo_exit -ne 0) {
        $__ohnoo_last_cmd = (Get-History -Count 1).CommandLine
        try { ohnoo check --exit-code $__ohnoo_exit --log $env:OHNOO_LOG --last-command "$__ohnoo_last_cmd" } catch {}
    }
    if ($global:__ohnoo_prev_prompt) { & $global:__ohnoo_prev_prompt } else { "PS $($executionContext.SessionState.Path.CurrentLocation)$('>' * ($nestedPromptLevel + 1)) " }
}
"""


def install() -> tuple[Path, bool]:
    override = os.environ.get("OHNOO_PWSH_PROFILE")
    rc_path = Path(override).expanduser() if override else Path(PROFILE_FILE).expanduser()
    return install_block(rc_path, _BODY)
