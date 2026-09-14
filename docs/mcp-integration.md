# MCP Integration Guide

`ohnoo` Layer 3 (see `CLAUDE.md` Section 2) runs a local MCP server that
exposes ohnoo's Layer 1 pattern-matching engine as tools any MCP-aware agent
or IDE can call into. This layer is passive: `ohnoo` never calls out, the
host agent calls in.

## 1. Start the server

```bash
ohnoo mcp-server
```

By default this starts a streamable-HTTP MCP server on
`http://127.0.0.1:8420/mcp`. (Port `8420` is arbitrary — pick any free port
and update the config snippet below to match.)

## 2. Tools exposed

| Tool | Purpose |
|---|---|
| `diagnose_error(traceback, file_context="")` | Plain diagnostic summary + suggested fix for a traceback |
| `suggest_fix(error_type, context="")` | Targeted fix lookup for a known error type/description |
| `roast_error(traceback)` | Same matching, but returns ohnoo's joke — keeps the personality accessible to agents too |

## 3. Config snippet

Every tool listed below uses the same config shape:

```json
{ "mcpServers": { "ohnoo": { "serverUrl": "http://localhost:8420/mcp" } } }
```

### Claude Code

Add this to a `.mcp.json` file in your project root (Claude Code picks up
project-scoped MCP servers from there automatically), or register it directly
with the CLI:

```bash
claude mcp add --transport http ohnoo http://localhost:8420/mcp
```

### Cursor

Add the snippet to `.cursor/mcp.json` in your project root (or to Cursor's
global MCP config if you want ohnoo available across all projects — Cursor
supports both a project-level and a user-level `mcp.json`).

### Windsurf

Add the snippet to Windsurf's MCP config file, `~/.codeium/windsurf/mcp_config.json`.
Windsurf reads this on startup and after you hit "Refresh" in the MCP panel
of its settings UI.

### Antigravity

Antigravity is a newer CLI/IDE agent, and we have not independently confirmed
the exact path or file name of its MCP config at the time of writing. Based
on it following the same general MCP config conventions as the tools above,
it most likely expects an equivalent `mcpServers` entry in a project- or
user-level JSON config file. **Treat this one as best-effort** — if
Antigravity's actual config location differs, please open an issue or send a
PR updating this doc with the confirmed path.

## 4. What "passive" means here

`ohnoo mcp-server` does not shell out to any AI agent (that's Layer 2). It
only answers tool calls made *to* it. If no MCP client ever calls in, the
server just sits idle — there's no background behavior, no scheduled calls,
and no network activity beyond serving requests made to it.
