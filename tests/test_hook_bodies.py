"""Regression guards for the Windows argv-injection fix.

The PowerShell hook used to build `ohnoo check ... --last-command "$cmd"`
by interpolating the user's last-typed command line into a string handed
to a native executable. Windows PowerShell 5.1's argv quoting for native
commands can't reliably escape arbitrary text (embedded quotes/backslashes),
so a crafted last command could smuggle extra CLI flags into that
invocation. The fix: never build that invocation as a string containing
untrusted content -- pass it through an environment variable instead,
which isn't parsed as argv at all. bash/zsh's quoted command-substitution
form was already safe, but were moved to the same env-var scheme too, and
--log was dropped as a CLI flag entirely (see cli.py's _log_path()).
"""

from ohnoo.hook import bash, pwsh, zsh


def test_pwsh_hook_passes_last_command_via_env_var_not_inline_string():
    invocation_line = next(
        line for line in pwsh._BODY.splitlines() if line.strip().startswith("try {") and "ohnoo check" in line
    )
    assert "--last-command" not in invocation_line
    assert "$env:OHNOO_LAST_COMMAND = (Get-History" in pwsh._BODY
    assert invocation_line.strip() == 'try { ohnoo check --exit-code $__ohnoo_exit } catch {}'


def test_bash_hook_passes_last_command_as_env_var_prefix_not_cli_flag():
    assert 'OHNOO_LAST_COMMAND="$(fc -ln -1' in bash._BODY
    assert "--last-command" not in bash._BODY


def test_zsh_hook_passes_last_command_as_env_var_prefix_not_cli_flag():
    assert 'OHNOO_LAST_COMMAND="$(fc -ln -1' in zsh._BODY
    assert "--last-command" not in zsh._BODY


def test_no_hook_passes_an_explicit_log_path_argument():
    assert "--log" not in bash._BODY
    assert "--log" not in zsh._BODY
    assert "--log" not in pwsh._BODY
