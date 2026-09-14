"""ohnoo CLI entrypoint."""

from __future__ import annotations

import os
import shutil
import sys
import sysconfig
from pathlib import Path

import click

from ohnoo import __version__
from ohnoo.engine import diagnose, load_last, save_last
from ohnoo.hook import bash as bash_hook
from ohnoo.hook import fish as fish_hook
from ohnoo.hook import pwsh as pwsh_hook
from ohnoo.hook import zsh as zsh_hook
from ohnoo.vibes import KNOWN_VIBES, resolve_vibe
from ohnoo.vibes.config import get_default_vibe, set_default_vibe

_llm_nudged_this_process = False


@click.group(invoke_without_command=True)
@click.option("--vibe", default=None, help="Personality pack to use (default, gordon-ramsay, zen, sarcastic-senior-dev).")
@click.option("--version", is_flag=True, help="Show the ohnoo version and exit.")
@click.pass_context
def main(ctx: click.Context, vibe: str | None, version: bool) -> None:
    """ohnoo - catches your crash, roasts it, and points you at the fix."""
    ctx.ensure_object(dict)
    ctx.obj["vibe"] = resolve_vibe(vibe) if vibe else get_default_vibe()

    if version:
        click.echo(f"ohnoo {__version__}")
        return

    if ctx.invoked_subcommand is not None:
        return

    if not sys.stdin.isatty():
        _handle_pipe_mode(ctx.obj["vibe"])
        return

    click.echo(ctx.get_help())


def _handle_pipe_mode(vibe: str) -> None:
    text = sys.stdin.read()
    if not text.strip():
        return
    _diagnose_and_report(text, vibe=vibe)


def _diagnose_and_report(text: str, vibe: str, last_command: str = "") -> None:
    """Run Layer 1, record stats/cache on a hit, fall back to Layer 4 on a miss."""
    result = diagnose(text, vibe=vibe, last_command=last_command)

    if result.matched:
        click.echo(result.render())
        save_last(result, command=last_command)
        try:
            from ohnoo.stats import record_roast

            record_roast(result.pattern_id, result.language)
        except Exception:  # noqa: BLE001, S110 - stats must never break the roast flow
            pass
        return

    llm_result = _try_llm_fallback(text)
    if llm_result is not None:
        click.echo(click.style("ohnoo (hosted): ", fg="cyan", bold=True) + llm_result)
        return

    click.echo(result.render())
    _maybe_nudge_setup_ai()


def _try_llm_fallback(text: str) -> str | None:
    try:
        from ohnoo.llm_fallback.fallback import try_llm_fallback
    except ImportError:
        return None
    try:
        return try_llm_fallback(text)
    except Exception:  # noqa: BLE001 - Layer 4 must never break the roast flow
        return None


def _maybe_nudge_setup_ai() -> None:
    global _llm_nudged_this_process
    if _llm_nudged_this_process:
        return
    _llm_nudged_this_process = True
    click.echo(
        click.style("  tip: ", fg="yellow")
        + "unrecognized errors like this can get a real diagnosis if you run `ohnoo setup-ai` "
        "(off by default, opt-in, no network calls unless configured)."
    )


_SHELL_INSTALLERS = {
    "bash": bash_hook,
    "zsh": zsh_hook,
    "fish": fish_hook,
    "powershell": pwsh_hook,
}


@main.command()
@click.option(
    "--shell",
    type=click.Choice(["bash", "zsh", "fish", "powershell", "auto"]),
    default="auto",
    help="Which shell to patch. 'auto' detects bash/zsh/fish from $SHELL (PowerShell needs an explicit --shell).",
)
@click.option("--uninstall", is_flag=True, help="Remove the ohnoo hook instead of installing it.")
def init(shell: str, uninstall: bool) -> None:
    """Install the ohnoo shell hook into your rc file / profile (idempotent).

    fish support is partial: it can't auto-capture stderr (no process
    substitution for output), so it nudges toward manual pipe mode instead.
    PowerShell support uses Start-Transcript to capture session output.

    Pass --uninstall to remove a previously installed hook.
    """
    if shell == "auto":
        shell = _detect_shell()

    installer = _SHELL_INSTALLERS.get(shell)
    if installer is None:
        click.echo(
            f"ohnoo: unsupported or undetected shell '{shell}'. "
            "Pass --shell bash|zsh|fish|powershell explicitly."
        )
        sys.exit(1)

    if uninstall:
        for path, removed in installer.uninstall():
            if removed:
                click.echo(f"ohnoo hook removed from {path}. Restart your shell or re-source it.")
            else:
                click.echo(f"ohnoo hook not found in {path}. Nothing to do.")
        return

    for path, installed in installer.install():
        if installed:
            click.echo(f"ohnoo hook installed in {path}. Restart your shell or re-source it to activate.")
        else:
            click.echo(f"ohnoo hook already present in {path}. Nothing to do.")

    path_warning = _check_ohnoo_on_path()
    if path_warning:
        click.echo(click.style("ohnoo: warning: ", fg="yellow", bold=True) + path_warning)


def _check_ohnoo_on_path() -> str | None:
    """Warn if the hook just installed won't actually be able to find `ohnoo`.

    pip commonly installs console-script shims into a per-user scripts
    directory that isn't on PATH by default (most visibly on Windows with a
    non-venv `pip install`). The shell hooks wrap `ohnoo check` in a
    catch-everything guard specifically so a *missing agent CLI* (Layer 2)
    never breaks the user's prompt -- but that guard is indiscriminate, so
    it also silently swallows a missing `ohnoo` itself, with zero signal to
    the user that anything is wrong. Catching that here, once, at install
    time -- while the user is already looking at this terminal -- beats
    them discovering it days later by noticing nothing ever happens.

    Returns None if `ohnoo` resolves normally (the common case), or a
    ready-to-run fix if it doesn't and we can locate where it actually is.
    """
    if shutil.which("ohnoo") is not None:
        return None

    scripts_dir = Path(sysconfig.get_path("scripts"))
    exe_name = "ohnoo.exe" if os.name == "nt" else "ohnoo"
    if not (scripts_dir / exe_name).exists():
        return None  # can't point at a specific fix; don't guess

    if os.name == "nt":
        fix = f'[Environment]::SetEnvironmentVariable("PATH", $env:PATH + ";{scripts_dir}", "User")'
    else:
        fix = f"echo 'export PATH=\"{scripts_dir}:$PATH\"' >> ~/.profile"

    return (
        f"'ohnoo' isn't on your PATH right now ({scripts_dir} isn't in it), so the "
        "hook just installed won't be able to find it -- it'll silently do nothing "
        "on every crash. Fix with:\n"
        f"  {fix}\n"
        "then open a new terminal window. (Or reinstall with `pipx install ohnoo`, "
        "which manages PATH for you.)"
    )


def _detect_shell() -> str:
    shell_path = os.environ.get("SHELL", "")
    if "fish" in shell_path:
        return "fish"
    if "zsh" in shell_path:
        return "zsh"
    if "bash" in shell_path:
        return "bash"
    # PowerShell doesn't reliably set $SHELL, so it's never auto-detected --
    # require an explicit `--shell powershell` rather than guess wrong and
    # patch the wrong profile.
    return "unknown"


def _log_path() -> Path:
    """Resolve the captured stderr/transcript log path.

    Honors $OHNOO_LOG (set by the shell hook itself), falling back to the
    same default the hook uses. Deliberately not a CLI flag: an
    argv-controllable arbitrary path here would let anything invoking
    `ohnoo check` read and pattern-match (or, with Layer 4 configured,
    forward to a hosted LLM) any file it names.
    """
    return Path(os.environ.get("OHNOO_LOG", str(Path.home() / ".cache" / "ohnoo" / "stderr.log"))).expanduser()


@main.command()
@click.option("--exit-code", "exit_code", type=int, required=True)
@click.option(
    "--last-command",
    "last_command",
    default="",
    envvar="OHNOO_LAST_COMMAND",
    help="The command that just failed, for context only.",
)
@click.pass_context
def check(ctx: click.Context, exit_code: int, last_command: str) -> None:
    """Internal command invoked by the shell hook after a non-zero exit."""
    if exit_code == 0:
        return

    p = _log_path()
    if not p.exists():
        return

    tail = _tail(p, max_bytes=8000)
    if not tail.strip():
        return

    _diagnose_and_report(tail, vibe=ctx.obj.get("vibe", "default"), last_command=last_command)


def _tail(path, max_bytes: int) -> str:
    with path.open("rb") as f:
        f.seek(0, 2)
        size = f.tell()
        f.seek(max(0, size - max_bytes))
        data = f.read()
    return data.decode("utf-8", errors="replace")


def _capture_error_text() -> str:
    """Best-effort error text for --explain/--fix: piped stdin, else the stderr log tail."""
    if not sys.stdin.isatty():
        text = sys.stdin.read()
        if text.strip():
            return text

    log_path = _log_path()
    if log_path.exists():
        return _tail(log_path, max_bytes=8000)
    return ""


def _confirm_from_terminal(prompt: str, default: bool = False) -> bool:
    """Ask a y/n question, reading from the controlling terminal rather than stdin.

    `cmd 2>&1 | ohnoo fix` is ohnoo's own documented usage, and it means
    stdin has already been fully consumed by `_capture_error_text()` above
    by the time we need to ask for confirmation. Without this, click's
    normal `confirm()` (which reads from stdin) would hit EOF immediately
    and abort -- silently defeating the one safety check --fix depends on.
    """
    if sys.stdin.isatty():
        return click.confirm(prompt, default=default)

    tty_path = "CON" if os.name == "nt" else "/dev/tty"
    try:
        with open(tty_path) as tty:
            original_stdin = sys.stdin
            sys.stdin = tty
            try:
                return click.confirm(prompt, default=default)
            finally:
                sys.stdin = original_stdin
    except OSError:
        # No controlling terminal at all (fully non-interactive, e.g. CI) --
        # degrade to the safe default rather than crashing or hanging.
        click.echo(f"{prompt} [non-interactive: defaulting to {'yes' if default else 'no'}]")
        return default


_NO_ERROR_TEXT_MESSAGE = (
    "ohnoo: no error text to work with. Pipe a failing command in "
    "(`cmd 2>&1 | ohnoo {cmd}`) or run this right after a real crash with the shell hook active."
)


@main.command("explain")
def explain_cmd() -> None:
    """Read-only diagnosis of the last error via an installed AI coding agent."""
    text = _capture_error_text()
    if not text.strip():
        click.echo(_NO_ERROR_TEXT_MESSAGE.format(cmd="explain"))
        return

    from ohnoo.agents.handoff import explain

    click.echo(explain(text, cwd=os.getcwd()))


@main.command("fix")
def fix_cmd() -> None:
    """Agent-assisted fix for the last error. Always asks for confirmation first."""
    text = _capture_error_text()
    if not text.strip():
        click.echo(_NO_ERROR_TEXT_MESSAGE.format(cmd="fix"))
        return

    from ohnoo.agents.handoff import cost_warning_text, fix, should_warn_this_session

    if should_warn_this_session():
        click.echo(cost_warning_text())

    if not _confirm_from_terminal("Let an installed AI coding agent attempt a fix now?", default=False):
        click.echo("ohnoo: cancelled, nothing was run.")
        return

    cwd = os.getcwd()
    result = fix(text, cwd=cwd)
    if not result.success:
        click.echo(f"ohnoo: fix attempt failed: {result.error}")
        return

    click.echo(
        "ohnoo: the agent ran headlessly and may have already written changes "
        "(headless CLIs can't preview edits before applying them). Diff captured afterward:"
    )
    click.echo(result.diff or "(no diff detected - the agent may not have changed any tracked files)")

    if result.status_before is None or result.status_after is None:
        click.echo(
            "ohnoo: not a git repository (or git isn't available) -- changes can't be "
            "auto-reverted here. Review them manually."
        )
        return

    if result.status_before == result.status_after:
        return  # nothing changed on disk; no keep/revert decision needed

    if not _confirm_from_terminal("Keep these changes?", default=True):
        from ohnoo.agents._common import revert_changes

        reverted = revert_changes(cwd, result.status_before, result.status_after)
        click.echo("ohnoo: changes reverted." if reverted else "ohnoo: nothing to revert.")
    else:
        click.echo("ohnoo: changes kept.")


@main.command("share")
def share_cmd() -> None:
    """Render the last roast as a shareable terminal-style PNG."""
    cached = load_last()
    if cached is None:
        click.echo("ohnoo: no roast recorded yet. Trigger a crash first, then run `ohnoo share`.")
        return

    diagnosis, command = cached
    try:
        from ohnoo.share import render_share_card
    except ImportError:
        click.echo("ohnoo: --share needs Pillow. Install with `pip install ohnoo[share]`.")
        return

    path = render_share_card(diagnosis, command=command)
    click.echo(f"ohnoo: share card saved to {path}")


@main.command("vibe")
@click.argument("name", required=False)
def vibe_cmd(name: str | None) -> None:
    """Show or set the persistent default --vibe."""
    if name is None:
        current = get_default_vibe()
        choices = ", ".join(v for v in KNOWN_VIBES if v != current)
        click.echo(f"ohnoo: default vibe is '{current}'. Other choices: {choices}")
        return

    try:
        set_default_vibe(name)
    except ValueError as exc:
        click.echo(f"ohnoo: {exc}")
        sys.exit(1)

    click.echo(f"ohnoo: default vibe set to '{name}'.")


@main.command("stats")
def stats_cmd() -> None:
    """Show local roast statistics."""
    from ohnoo.stats import summary

    click.echo(summary())


@main.command("setup-ai")
@click.option("--disable", is_flag=True, help="Remove Layer 4 hosted-LLM configuration.")
def setup_ai_cmd(disable: bool) -> None:
    """Configure the opt-in hosted LLM fallback."""
    try:
        from ohnoo.llm_fallback.wizard import run_setup_wizard
    except ImportError:
        click.echo("ohnoo: setup-ai needs extra deps. Install with `pip install ohnoo[llm]`.")
        return

    click.echo(run_setup_wizard(disable=disable))


@main.command("mcp-server")
@click.option("--port", default=8420, type=int, help="Port to serve the MCP server on.")
@click.option("--host", default="127.0.0.1", help="Host to bind the MCP server to.")
def mcp_server_cmd(port: int, host: str) -> None:
    """Start the MCP server exposing ohnoo's tools to agents (blocking)."""
    try:
        from ohnoo.mcp_server import run_server
    except ImportError:
        click.echo("ohnoo: mcp-server needs extra deps. Install with `pip install ohnoo[mcp]`.")
        return

    if host not in ("127.0.0.1", "localhost", "::1"):
        click.echo(
            click.style("ohnoo: warning: ", fg="yellow", bold=True)
            + f"binding to '{host}' exposes this server to other hosts on the network. "
            "It has no authentication -- anyone who can reach it can call its tools."
        )

    click.echo(f"ohnoo: starting MCP server at http://{host}:{port}/mcp")
    run_server(port=port, host=host)


if __name__ == "__main__":
    main()
