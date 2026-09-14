"""Layer 3 — local MCP server exposing ohnoo's Layer 1 pattern engine to any
MCP-aware agent or IDE (Claude Code, Antigravity, Cursor, Windsurf, ...).

This is a *passive* layer per CLAUDE.md Section 2: ohnoo never calls out here,
the host agent calls in. All three tools are thin wrappers around
``ohnoo.engine.diagnose()`` — no matching logic is reimplemented here.

The actual tool logic lives in plain, importable functions (``_diagnose_error``,
``_suggest_fix``, ``_roast_error``) so tests can exercise them directly without
going through the MCP protocol layer. The ``@server.tool()``-decorated
functions below are thin wrappers that register those same functions with the
MCP server.
"""

from __future__ import annotations

from typing import Any

from ohnoo.engine import diagnose

FALLBACK_JOKE = "Even I don't know what this is. That's either impressive or concerning."


def _safe_diagnose(text: str):
    """Run ohnoo's pattern engine on ``text``, never raising on bad input."""
    try:
        if not text or not isinstance(text, str):
            return diagnose("")
        return diagnose(text)
    except Exception:  # noqa: BLE001 - Layer 3 tools must never raise on bad input;
        # an agent calling a broken tool is worse than one getting a "no match" reply.
        from ohnoo.engine import Diagnosis

        return Diagnosis(matched=False)


def _diagnose_error(traceback: str, file_context: str = "") -> dict[str, Any]:
    """Diagnose a traceback/error, returning a structured (non-joke) summary."""
    text = f"{traceback or ''}\n{file_context or ''}".strip()
    result = _safe_diagnose(text)

    if not result.matched:
        return {
            "matched": False,
            "pattern_id": None,
            "diagnosis": "No known pattern matched this error.",
            "suggested_fix": "",
        }

    diagnosis_bits = [f"Matched pattern '{result.pattern_id}'."]
    if result.fix_summary:
        diagnosis_bits.append(result.fix_summary)
    return {
        "matched": True,
        "pattern_id": result.pattern_id,
        "diagnosis": " ".join(diagnosis_bits),
        "suggested_fix": result.fix_command or result.fix_summary,
    }


def _suggest_fix(error_type: str, context: str = "") -> dict[str, Any]:
    """Suggest a fix for a targeted error type (e.g. an exception class name)."""
    text = f"{error_type or ''} {context or ''}".strip()
    result = _safe_diagnose(text)

    if not result.matched:
        return {"matched": False, "fix_summary": "", "fix_command": ""}

    return {
        "matched": True,
        "fix_summary": result.fix_summary,
        "fix_command": result.fix_command,
    }


def _roast_error(traceback: str) -> dict[str, Any]:
    """Return the joke for a traceback, keeping ohnoo's personality accessible
    to agents too (CLAUDE.md Section 2, Layer 3)."""
    result = _safe_diagnose(traceback or "")

    if not result.matched:
        return {"matched": False, "joke": FALLBACK_JOKE}

    return {"matched": True, "joke": result.joke or FALLBACK_JOKE}


def run_server(port: int = 8420, host: str = "127.0.0.1") -> None:
    """Start the ohnoo MCP server (blocking).

    Exposes ``diagnose_error``, ``suggest_fix``, and ``roast_error`` over the
    streamable-http transport at ``http://{host}:{port}/mcp``, matching the
    config shape documented in CLAUDE.md Section 2 (Layer 3) and
    docs/mcp-integration.md.
    """
    # Imported lazily so importing this module (e.g. for tests) never requires
    # the optional `mcp` dependency unless the server is actually started.
    from mcp.server.mcpserver import MCPServer

    server: MCPServer = MCPServer(
        name="ohnoo",
        instructions=(
            "ohnoo catches shell crashes and matches them against a local pattern "
            "database of common Python/Node/Git/Docker errors. Use diagnose_error "
            "for a plain diagnostic summary, suggest_fix for a targeted fix lookup, "
            "and roast_error if you want the joke too."
        ),
    )

    @server.tool()
    def diagnose_error(traceback: str, file_context: str = "") -> dict[str, Any]:
        """Diagnose an error traceback using ohnoo's local pattern database.

        Args:
            traceback: The raw error/traceback text to diagnose.
            file_context: Optional extra context (failing file/line, snippet).
        """
        return _diagnose_error(traceback, file_context)

    @server.tool()
    def suggest_fix(error_type: str, context: str = "") -> dict[str, Any]:
        """Suggest a fix command for a given error type.

        Args:
            error_type: Short error type or description (e.g. "ModuleNotFoundError").
            context: Optional extra context to help matching (package name, port, etc).
        """
        return _suggest_fix(error_type, context)

    @server.tool()
    def roast_error(traceback: str) -> dict[str, Any]:
        """Roast an error traceback in ohnoo's default voice.

        Args:
            traceback: The raw error/traceback text to roast.
        """
        return _roast_error(traceback)

    server.run(transport="streamable-http", host=host, port=port)
