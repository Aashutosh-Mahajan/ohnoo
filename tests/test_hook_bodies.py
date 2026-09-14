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
    invocation_line = next(line for line in pwsh._BODY.splitlines() if "ohnoo check --exit-code" in line)
    assert "--last-command" not in invocation_line
    assert "$env:OHNOO_LAST_COMMAND = $__ohnoo_hist.CommandLine" in pwsh._BODY
    assert invocation_line.strip() == "$__ohnoo_output = ohnoo check --exit-code $__ohnoo_exit 2>&1 | Out-String"


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


def test_pwsh_hook_only_checks_once_per_new_command_not_every_prompt_redraw():
    """Regression test: $LASTEXITCODE isn't reset just because `prompt` ran,
    and PowerShell can invoke `prompt` more than once per actual command
    (PSReadLine redraws being the most common case). Without tracking which
    command was already checked, the hook would re-fire `ohnoo check` on
    every such redraw for as long as $LASTEXITCODE stayed non-zero -- in
    practice, roasting on a loop that only "ends" once the user runs a new
    native command. The fix tracks the last-checked history entry ID and
    only acts again once a genuinely new command has run."""
    assert "$global:__ohnoo_last_checked_id" in pwsh._BODY
    assert "$__ohnoo_hist.Id -ne $global:__ohnoo_last_checked_id" in pwsh._BODY
    # The dedup check must actually gate the ohnoo-check block, not just
    # exist somewhere unused: the assignment that records "we checked
    # this one" must appear before the `ohnoo check` invocation.
    id_assignment_pos = pwsh._BODY.index("$global:__ohnoo_last_checked_id = $__ohnoo_hist.Id")
    check_call_pos = pwsh._BODY.index("ohnoo check --exit-code")
    assert id_assignment_pos < check_call_pos


def test_pwsh_hook_never_touches_transcript_state_inside_the_prompt_callback():
    """Regression test: an earlier version of this hook called
    Stop-Transcript/Start-Transcript from inside the `prompt` callback (to
    force a flush before `ohnoo check` read the log), but doing that from
    within `prompt` specifically was observed to hang the shell in real
    interactive use on at least one terminal host. `Start-Transcript` must
    only ever be called once, outside of `prompt`, and `Stop-Transcript`
    must never appear in this hook at all."""
    prompt_fn_start = pwsh._BODY.index("function global:prompt")
    prompt_fn_body = pwsh._BODY[prompt_fn_start:]

    assert "Stop-Transcript" not in pwsh._BODY
    assert "Start-Transcript" not in prompt_fn_body
    assert pwsh._BODY.count("Start-Transcript") == 1


def test_pwsh_hook_captures_check_output_instead_of_letting_it_hit_the_console_directly():
    """Regression test: `ohnoo check` writing straight to the console from
    inside the `prompt` callback -- outside PSReadLine's own read-eval-print
    cycle -- was observed to desync PSReadLine's redraw tracking, leaving
    the next prompt line undrawn until something (e.g. Enter) forced a
    fresh redraw. The fix captures its output as a string and prints it via
    Write-Host, which stays inside PowerShell's own output pipeline."""
    assert "ohnoo check --exit-code $__ohnoo_exit 2>&1 | Out-String" in pwsh._BODY
    assert "Write-Host $__ohnoo_output" in pwsh._BODY
