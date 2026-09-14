"""PowerShell hook.

Unlike bash/zsh's `exec 2> >(tee ...)`, PowerShell has a native way to
continuously capture everything a session prints: `Start-Transcript`. This
hook starts a transcript into $env:OHNOO_LOG once per session, then wraps
the `prompt` function (PowerShell's precmd equivalent) to call `ohnoo check`
whenever $LASTEXITCODE is non-zero, chaining to whatever `prompt` function
was already defined (e.g. oh-my-posh) so this hook doesn't clobber it.

Start-Transcript buffers its writes and doesn't flush them to disk after
every command, so a stopped-then-restarted transcript around each check
was tried as a way to force a flush before `ohnoo check` (a *separate*
process) reads the file -- but calling Stop-Transcript/Start-Transcript
from inside the `prompt` callback itself turned out to be capable of
hanging the shell in some terminal hosts (observed in practice, not just
theoretical), which is a far worse outcome than the staleness it was
meant to fix. So this hook does not touch transcript state mid-session at
all: `Start-Transcript` runs once, and whatever's on disk when `ohnoo
check` reads it is whatever's on disk -- occasionally missing the very
latest line is an acceptable tradeoff for never hanging the prompt.

$LASTEXITCODE stays whatever it was set to until the next native command
changes it -- it is not reset just because `prompt` ran. PowerShell can
invoke `prompt` more than once per actual command typed (PSReadLine
redraws being the most common case), so without tracking which command
was already checked, the hook would re-fire `ohnoo check` on every one of
those redraws for as long as $LASTEXITCODE stayed non-zero -- in practice,
roasting on a loop until the user happened to run a new native command
that changed it. The fix is to remember the history entry ID of the last
command actually checked, and only act again once a genuinely new command
has run (a different ID), regardless of how many times `prompt` itself
gets called in between.

`ohnoo check` is a native process, and letting it write directly to the
console from inside the `prompt` callback -- outside PSReadLine's own
read-eval-print cycle -- can desync PSReadLine's redraw tracking, leaving
the next prompt line undrawn until something (e.g. pressing Enter) forces
a fresh redraw (observed in practice). So its output is captured as a
string and printed via Write-Host instead of letting it hit the console
directly, keeping it inside PowerShell's own output pipeline, which
PSReadLine does track correctly.

Caveat: $LASTEXITCODE only reflects native executable exit codes, not
cmdlet failures surfaced only via $?. That's a real limitation, not a bug.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

from ohnoo.hook.common import install_block, uninstall_block

# PowerShell 7+ ("Core" edition, pwsh.exe) and Windows PowerShell 5.1
# ("Desktop" edition, powershell.exe -- the one that ships on every Windows
# machine by default, launched from the plain "Windows PowerShell" shortcut)
# read their profile from two genuinely different files. Installing into
# only one silently does nothing for whichever edition the user actually
# launches -- which, for most users, is Windows PowerShell, the one *not*
# named "PowerShell" in its own profile path. Both get the hook installed.
#
# These are naive fallbacks only, used when a binary can't be queried
# directly (see _query_profile_path) -- they assume an unredirected
# Documents folder under $HOME, which is wrong whenever Documents has been
# moved (most commonly by OneDrive's "Back up your folders" feature, a
# Windows default many users have on). $PROFILE is what PowerShell itself
# actually reads, and it correctly follows that redirection; querying the
# real binary for it is the only way to reliably get the same answer.
PROFILE_FILE_CORE = "~/Documents/PowerShell/Microsoft.PowerShell_profile.ps1"
PROFILE_FILE_DESKTOP = "~/Documents/WindowsPowerShell/Microsoft.PowerShell_profile.ps1"

_BODY = """\
if (-not $env:OHNOO_LOG) { $env:OHNOO_LOG = Join-Path $HOME ".cache/ohnoo/stderr.log" }
New-Item -ItemType Directory -Force -Path (Split-Path $env:OHNOO_LOG) -ErrorAction SilentlyContinue | Out-Null

if ((Test-Path $env:OHNOO_LOG) -and ((Get-Item $env:OHNOO_LOG -ErrorAction SilentlyContinue).Length -gt 5MB)) {
    Clear-Content $env:OHNOO_LOG -ErrorAction SilentlyContinue
}

if (-not $env:OHNOO_TRANSCRIPT_STARTED) {
    $env:OHNOO_TRANSCRIPT_STARTED = "1"
    try { Start-Transcript -Path $env:OHNOO_LOG -Append -Force | Out-Null } catch {}
}

$global:__ohnoo_prev_prompt = $function:prompt
if (-not (Test-Path Variable:\\__ohnoo_last_checked_id)) { $global:__ohnoo_last_checked_id = -1 }

function global:prompt {
    $__ohnoo_exit = $LASTEXITCODE
    $__ohnoo_hist = Get-History -Count 1
    $__ohnoo_is_new_failure = $__ohnoo_exit -and $__ohnoo_exit -ne 0 -and $__ohnoo_hist -and
        ($__ohnoo_hist.Id -ne $global:__ohnoo_last_checked_id)
    if ($__ohnoo_is_new_failure) {
        $global:__ohnoo_last_checked_id = $__ohnoo_hist.Id

        # Passed via an env var, never interpolated into the invocation
        # string -- native-exe argv quoting in Windows PowerShell can't
        # reliably escape arbitrary text (embedded quotes/backslashes),
        # so building "ohnoo check ... --last-command $cmd" as a string
        # would let a crafted last command smuggle extra arguments in.
        $env:OHNOO_LAST_COMMAND = $__ohnoo_hist.CommandLine
        try {
            # Captured and printed via Write-Host rather than left to hit
            # the console directly -- see module docstring.
            $__ohnoo_output = ohnoo check --exit-code $__ohnoo_exit 2>&1 | Out-String
            if ($__ohnoo_output.Trim()) { Write-Host $__ohnoo_output.TrimEnd() }
        } catch {}
        Remove-Item Env:OHNOO_LAST_COMMAND -ErrorAction SilentlyContinue
    }
    if ($global:__ohnoo_prev_prompt) { & $global:__ohnoo_prev_prompt } else { "PS $($executionContext.SessionState.Path.CurrentLocation)$('>' * ($nestedPromptLevel + 1)) " }
}
"""


def _query_profile_path(binary: str) -> Path | None:
    """Ask a PowerShell binary directly for its own $PROFILE.

    This is the only fully robust way to get this right: $PROFILE depends
    on Documents-folder resolution, which OneDrive, Group Policy, or a
    non-default user profile location can all redirect. Reimplementing
    that resolution ourselves would just relocate the guessing; asking the
    actual binary is authoritative. Returns None if the binary isn't
    installed or the query fails for any reason.
    """
    if shutil.which(binary) is None:
        return None
    try:
        result = subprocess.run(
            [binary, "-NoProfile", "-NonInteractive", "-Command", "$PROFILE"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    output = result.stdout.strip()
    if result.returncode != 0 or not output:
        return None
    return Path(output)


def _default_rc_paths() -> list[Path]:
    core = _query_profile_path("pwsh") or Path(PROFILE_FILE_CORE).expanduser()
    desktop = _query_profile_path("powershell") or Path(PROFILE_FILE_DESKTOP).expanduser()
    # dict.fromkeys instead of a set: preserves order, and Path doesn't
    # need to support ordering for de-duplication (only equality/hash).
    return list(dict.fromkeys([core, desktop]))


def _rc_paths() -> list[Path]:
    override = os.environ.get("OHNOO_PWSH_PROFILE")
    if override:
        return [Path(override).expanduser()]
    return _default_rc_paths()


def install() -> list[tuple[Path, bool]]:
    return [install_block(path, _BODY) for path in _rc_paths()]


def uninstall() -> list[tuple[Path, bool]]:
    return [(path, uninstall_block(path)) for path in _rc_paths()]
