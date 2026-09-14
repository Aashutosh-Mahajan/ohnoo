"""Layer 3 — MCP server mode (Phase 4).

Starts a local MCP server exposing diagnose_error, suggest_fix, and
roast_error tools for any MCP-aware agent or IDE to call into. See
``ohnoo.mcp_server.server.run_server`` for the entrypoint.
"""

from ohnoo.mcp_server.server import run_server

__all__ = ["run_server"]
