# CLAUDE.md — `ohnoo`

> A terminal companion that catches your crash, roasts it in one funny line, and — if you have an AI coding agent nearby — actually fixes it for you.

This file is the working spec for building `ohnoo`. It documents what the project is, how it's structured, and the phase-by-phase task list. Read this before writing code for the project.

---

## 1. Project Summary

| | |
|---|---|
| **Name** | `ohnoo` |
| **Package name** | PyPI: `ohnoo` (or `ohnoo-cli` if taken) |
| **Binary** | `ohnoo` |
| **License** | MIT |
| **Core promise** | Zero-config install → instant funny diagnosis on any crash → optional real fix via an AI coding agent already on the machine |
| **Primary audience** | Individual developers working in a terminal (Python/Node first, expandable) |
| **Positioning** | Spiritual successor to `thefuck` (89k★) for the "post-crash" moment, not the "mistyped command" moment |

### Non-goals (explicitly out of scope for v1)
- Not an IDE extension (v1 does not ship VS Code/JetBrains plugins — MCP handles IDE integration instead, see Layer 3)
- Not a bundled local LLM — no shipped model weights, ever (see `/docs/decisions/no-bundled-llm.md`)
- Not a monitoring/observability product — this is a local, single-developer tool, not a team dashboard (that could be a v2 direction, not v1)
- Not language-exhaustive on day one — Python and Node.js first; other runtimes are additive later

---

## 2. Architecture — The Four Layers

`ohnoo` is a cascade. Each layer only runs if the one above it didn't fully resolve the error. Every layer must degrade gracefully to the one below it with zero user-visible errors.

```
 crash happens
      │
      ▼
┌─────────────────────────────┐
│ LAYER 1 — Pattern Engine    │  offline, instant, always runs
│ known error → funny line     │
│ + fix command                │
└──────────────┬───────────────┘
               │ unrecognized error
               ▼
┌─────────────────────────────┐
│ LAYER 2 — CLI Agent Handoff  │  requires claude / codex / agy installed
│ shell out with scoped tools  │
│ → real diagnosis + fix       │
└──────────────┬───────────────┘
               │ no CLI agent found
               ▼
┌─────────────────────────────┐
│ LAYER 3 — MCP Server Mode    │  passive: agent calls INTO ohnoo
│ ohnoo exposes tools to any    │
│ MCP-aware agent/IDE          │
└──────────────┬───────────────┘
               │ no MCP client active
               ▼
┌─────────────────────────────┐
│ LAYER 4 — Hosted LLM Fallback│  opt-in only, off by default
│ cheap API call for novel      │
│ errors, only if configured    │
└───────────────────────────────┘
```

### Layer 1 — Offline Pattern Engine
**Purpose:** instant, zero-dependency value on first install. This is the layer that makes or breaks the "magic" first-run experience — it must never feel slow or require setup.

- A local pattern database (`patterns/*.json`) covering ~150+ common errors across Python, Node.js, Git, Docker, npm, and pip.
- Each pattern has:
  - A **matcher** (regex or structured exception-type match)
  - **5–10 joke variants** with mad-libs style slot-filling (filename, port number, package name pulled from the actual error)
  - **One real fix command**, always present, never omitted for the sake of the joke
  - A **personality tag** so `--vibe` packs can reskin the same pattern without duplicating fix logic
- Runs via a shell hook (`precmd`/`PROMPT_COMMAND` for zsh/bash, equivalent for fish/PowerShell) that captures the last exit code + stderr scrollback.
- **Zero network calls.** This layer must work fully offline, on a plane, in an air-gapped CI box.

### Layer 2 — CLI Agent Handoff
**Purpose:** turn "funny explanation" into "actual fix," by using an AI coding agent the user already has installed, instead of building our own reasoning engine.

- Detects installed agentic CLIs in priority order (configurable): `claude` (Claude Code), `codex` (Codex CLI), `agy` (Antigravity CLI).
- Builds a **scoped prompt** from the traceback + the specific failing file/line — never the whole repo.
- Invokes headlessly, e.g.:
  ```bash
  claude -p "{prompt}" --allowedTools Read,Edit,Bash
  codex exec "{prompt}"
  agy exec "{prompt}"
  ```
- Two explicit modes, both opt-in, never silent:
  - `ohnoo --explain` → read-only diagnosis, no file edits allowed
  - `ohnoo --fix` → agent may edit, but the resulting diff is shown to the user for confirmation before it's written
- **Cost transparency is mandatory.** Headless/`-p` invocations can be billed separately from a user's interactive session in some setups — `--fix` must never fire automatically; it always requires an explicit flag per invocation until the user sets a persistent preference.

### Layer 3 — MCP Server Mode
**Purpose:** cover IDE-embedded agents (Antigravity IDE, Cursor, Windsurf, VS Code Copilot, JetBrains AI) without building a bespoke integration per vendor, and stay compatible with tools that don't exist yet.

- `ohnoo mcp-server` starts a local MCP server exposing:
  - `diagnose_error(traceback, file_context)`
  - `suggest_fix(error_type, context)`
  - `roast_error(traceback)` — keeps the personality accessible to agents too
- Setup is one config entry, same shape across tools:
  ```json
  { "mcpServers": { "ohnoo": { "serverUrl": "http://localhost:PORT/mcp" } } }
  ```
- This is a **passive** layer — `ohnoo` does not call out; the host agent calls in. No agent behavior is assumed or required beyond "supports MCP."
- This layer is what lets `ohnoo` claim "works with every agentic IDE" without maintaining N separate plugins.

### Layer 4 — Hosted LLM Fallback
**Purpose:** the safety net for the small % of errors nothing else recognizes, so `ohnoo` never says "I have no idea" — without ever costing the user money or making a network call by default.

- **Off by default.** Requires `ohnoo setup-ai` or explicit env vars (`OHNOO_LLM_PROVIDER`, `OHNOO_LLM_KEY`).
- Supported providers: Groq (default recommendation — cheapest/fastest), Anthropic, OpenAI, or auto-detected local Ollama.
- Single-sentence diagnosis + fix, not a chat session. No conversation history retained.
- Config lives at `~/.config/ohnoo/config.toml`; the file stores the **env var name**, never the raw key in plaintext, to avoid dotfiles-repo leaks.

---

## 3. Feature Surface (beyond the core loop)

| Feature | Command | Purpose |
|---|---|---|
| Shareable roast card | `ohnoo --share` | Generates a terminal-screenshot-style image of the last roast — primary organic distribution mechanism |
| Personality packs | `ohnoo --vibe <name>` | `gordon-ramsay`, `zen`, `sarcastic-senior-dev`, default. Swaps phrasing templates only — fix logic is shared |
| Usage stats | `ohnoo --stats` | "Roasted 340 times this month, mostly for forgetting semicolons" — screenshot bait |
| Manual pipe mode | `cmd 2>&1 \| ohnoo` | For users who don't want a persistent shell hook, or for CI log post-processing |
| AI setup wizard | `ohnoo setup-ai` | Configures Layer 4, tests with a dummy traceback before trusting it |
| Disable AI | `ohnoo setup-ai --disable` | Non-destructive removal of Layer 4 config only |
| Community patterns | PR to `patterns/*.json` | Growth loop — contributors add patterns, which is both product value and free promotion |

---

## 4. Tech Stack

- **Core CLI:** Python only, distributed via PyPI — `click` for the CLI surface
- **Shell hooks:** native zsh/bash/fish/PowerShell scripts, generated by `ohnoo init` and appended to the user's rc file
- **MCP server:** official MCP Python SDK
- **Pattern DB:** plain JSON, versioned, schema-validated in CI
- **Share-card renderer:** headless image generation (Pillow for a terminal-style PNG) — no browser dependency
- **Packaging:** `pyproject.toml` only. No npm wrapper (see Section 9, Key Decisions) — `pip install ohnoo` / `pipx install ohnoo` is the only supported install path.

---

## 5. Repository Structure

```
ohnoo/
├── CLAUDE.md                  # this file
├── README.md                  # public-facing, leads with the GIF
├── pyproject.toml
├── src/ohnoo/
│   ├── __init__.py
│   ├── cli.py                  # entrypoint, arg parsing
│   ├── hook/                   # shell hook generators (bash/zsh/fish/pwsh)
│   ├── patterns/                # Layer 1
│   │   ├── python.json
│   │   ├── node.json
│   │   ├── git.json
│   │   ├── docker.json
│   │   └── schema.json
│   ├── agents/                  # Layer 2 — CLI agent handoff
│   │   ├── claude_code.py
│   │   ├── codex.py
│   │   └── antigravity.py
│   ├── mcp_server/               # Layer 3
│   │   └── server.py
│   ├── llm_fallback/             # Layer 4
│   │   ├── providers/
│   │   └── config.py
│   ├── vibes/                    # personality packs
│   ├── share/                    # --share card renderer
│   └── stats/                    # --stats tracking (local only, no telemetry)
├── tests/
├── docs/                          # source for the website's /docs section
└── .github/workflows/             # CI: pattern schema validation, tests, dual publish
```

---

## 6. Build Phases & Tasks

### Phase 0 — Foundation
- [ ] Repo scaffold, license, `pyproject.toml` + `package.json` skeletons
- [x] Decide final PyPI name availability (confirmed `ohnoo` is free via a direct PyPI JSON API query, not just search)
- [ ] CI pipeline skeleton: lint, test, pattern-schema validation
- [ ] Write the pattern JSON schema (matcher type, joke variants, fix command, personality tag fields)

### Phase 1 — Layer 1 (Offline Pattern Engine)
- [ ] Shell hook generator for bash and zsh (fish/PowerShell can follow after)
- [ ] `ohnoo init` command — appends hook, idempotent, no prompts
- [ ] Exit-code + stderr capture mechanism
- [ ] Seed pattern DB: 30 Python errors, 30 Node errors, 20 Git errors, 10 Docker/npm/pip errors (~90 to start, expand toward 150+)
- [ ] Mad-libs slot-filling engine (extract filename/port/package name from raw error text)
- [ ] Manual pipe mode (`cmd 2>&1 | ohnoo`)
- [ ] **Exit criteria:** a fresh `pip install ohnoo && ohnoo init` produces a correct, funny, fix-including response to a real crash with zero network calls

### Phase 2 — Personality & Shareability
- [ ] `--vibe` system: template swapping, at least 3 packs + default
- [ ] `--share`: render a terminal-style PNG of the last roast
- [ ] `--stats`: local SQLite or flat-file log of roast counts, categories
- [ ] **Exit criteria:** a roast can go from terminal → shareable image in one command, and looks good posted on Twitter/X at native size

### Phase 3 — Layer 2 (CLI Agent Handoff)
- [ ] Detection logic for `claude`, `codex`, `agy` on `$PATH`
- [ ] Scoped prompt builder (traceback + failing file/line only, never full repo)
- [ ] `--explain` mode (read-only)
- [ ] `--fix` mode (edit allowed, diff shown, confirmation required before write)
- [ ] Cost-transparency warning shown once per session before first `--fix` call
- [ ] **Exit criteria:** on a machine with Claude Code installed, `ohnoo --fix` on a real one-line bug produces a correct, confirmed patch

### Phase 4 — Layer 3 (MCP Server Mode)
- [ ] Implement `ohnoo mcp-server` using the standard MCP SDK
- [ ] Expose `diagnose_error`, `suggest_fix`, `roast_error` tools
- [ ] Document the one-line config entry for Claude Code, Antigravity, Cursor, Windsurf
- [ ] **Exit criteria:** an MCP-aware agent (test with at least one real one, e.g. Claude Code) can call `ohnoo`'s tools mid-task without any shell-hook involvement

### Phase 5 — Layer 4 (Hosted LLM Fallback)
- [ ] `ohnoo setup-ai` interactive wizard (provider choice, key entry, dummy test call)
- [ ] Env-var-only path for CI/power users (`OHNOO_LLM_PROVIDER`, `OHNOO_LLM_KEY`)
- [ ] Config stored at `~/.config/ohnoo/config.toml`, storing env var name not raw key
- [ ] `ohnoo setup-ai --disable`
- [ ] Soft one-time nudge when an unrecognized error occurs and Layer 4 isn't configured
- [ ] **Exit criteria:** with no config, an unknown error degrades gracefully with no network call and no crash; with config, it returns a correct one-sentence diagnosis

### Phase 6 — Community & Distribution Infra
- [ ] `patterns/*.json` contribution guide + PR template
- [ ] `good first issue` seeded with 10–15 "add a pattern for X" tickets
- [x] PyPI publish pipeline via CI (GitHub Actions, PyPI Trusted Publishing / OIDC — no npm distribution, see Section 9)
- [ ] README with the launch GIF (`asciinema`/`vhs` recording) as the very first thing visible

### Phase 7 — Launch
- [ ] Finalize README, docs site (see Section 7), and `--share` visual polish
- [ ] Show HN post drafted and scheduled
- [ ] Cross-post to r/programming, r/Python, r/node, r/commandline
- [ ] Submit to `awesome-cli-apps` / `awesome-devtools` lists
- [ ] Monitor and respond to all issues/PRs within 24h for the first 2 weeks

---

## 7. Website Specification

The site is a single marketing + documentation site with four sections: **Home**, **Docs**, **Setup**, **Support**. This section is the content/structure spec to build from later — no implementation yet.

### 7.1 Design direction
- **Concept:** treat the whole site as an incident case-file / flight-recorder report, not a generic SaaS landing page — a "black box for your crashes." (Real flight recorders are painted international orange, not black — that fact anchors the palette.)
- **Palette:** charcoal base (`#16171A`), international-orange accent (`#FF5A1F`), hazard yellow used only at layer-transition dividers (`#F4C430`), terminal green for "resolved" states (`#43D17A`), off-white text (`#E8E6E1`), muted grey for secondary text (`#6B6D72`).
- **Type:** one family, two roles — IBM Plex Sans for body copy, IBM Plex Mono for terminal chrome, labels, and code.
- **Navigation:** folder-tab style (Home / Docs / Setup / Support), not a generic top nav bar.
- **Avoid:** rounded SaaS cards with soft drop shadows, gradient washes, decorative ALL-CAPS eyebrows above every heading, em-dash label chrome, arrow-suffixed buttons. Reserve uppercase/monospace stamps ("STATUS: RESOLVED", "CASE NO. 0417") for genuine case-file content, not decoration.

### 7.2 Home page
- **Hero:** a live terminal demo *is* the hero — not an illustration of one. Show the actual crash → roast → fix sequence from the README GIF, framed as case-file evidence. Install command (`pip install ohnoo`) sits directly under it, one click to copy.
- **What it does:** three short blocks, one per real example (Python `ModuleNotFoundError`, Node `EADDRINUSE`, Git `not a git repository`), each shown as an actual terminal card, not a text description.
- **The four layers, at a glance:** a compact visual cascade (not the full technical breakdown — that lives in Docs), framed as an evidence chain: pattern match → agent handoff → MCP → hosted fallback.
- **Shareability strip:** a few example `--share` cards, to model the feature and hint at the meme/social loop.
- **Footer CTA:** link to GitHub repo, Docs, and the "good first issue" pattern-contribution list.

### 7.3 Docs page
- **Architecture:** the four layers, explained in full (mirrors Section 2 of this file, written for an end user rather than a contributor).
- **Command reference:** a table of every command — `ohnoo init`, `--explain`, `--fix`, `--share`, `--vibe`, `--stats`, `setup-ai`, `mcp-server` — with a one-line description and an example.
- **Pattern contribution guide:** how to add a new entry to `patterns/*.json`, the schema, and how to submit a PR. This doubles as the doc that turns readers into contributors.
- **MCP integration guide:** the exact config snippet for Claude Code, Antigravity, Cursor, and Windsurf, since the config shape is nearly identical across tools (see Section 2, Layer 3).

### 7.4 Setup page
Structured as a linear checklist, not prose:
1. Install (`pip install ohnoo`, or `pipx install ohnoo` to keep it isolated)
2. Run `ohnoo init` — what it does to the shell rc file, and how to undo it
3. (Optional) Layer 2 — confirm an agentic CLI is detected (`claude` / `codex` / `agy`)
4. (Optional) Layer 3 — add the MCP config snippet for your IDE/agent of choice
5. (Optional) Layer 4 — run `ohnoo setup-ai`, pick a provider, confirm the test call
- Each optional step should visibly state what happens if skipped (graceful degradation to the layer below), so setup never feels like it's blocking basic use.

### 7.5 Support page
- **FAQ:** written from real anticipated questions, e.g. "Does this send my code anywhere?" (no, unless Layer 4 is configured), "Will `--fix` edit files without asking?" (never, confirmation is always required), "Does it work on Windows?" (current shell hook support status).
- **Troubleshooting table:** symptom → likely cause → fix, covering: hook not firing after `ohnoo init`, no agentic CLI detected on Layer 2, MCP config not picked up by the IDE, Layer 4 test call failing.
- **Links:** GitHub Issues (primary support channel), the pattern-contribution guide (for "my error isn't recognized"), and a link back to Setup for reinstall instructions.

---

## 8. Success Metrics (honest, not vanity)

| Metric | Target (Year 1) |
|---|---|
| GitHub stars | 2,000–15,000 realistic range; treat launch week as 80% of trajectory |
| Pattern DB coverage | 150+ patterns by end of Phase 1, 300+ by end of Year 1 via community PRs |
| Layer 2/3 reliability | `--fix` produces a correct, non-destructive patch on >90% of single-file bugs in test suite |
| Issue response time | <24h for first 2 weeks post-launch |

## 9. Key Decisions Log

- **No bundled local LLM.** Kills install-time friction, small models are weak at comedy, cross-platform packaging pain. See discussion in project chat history.
- **MCP over per-IDE plugins.** One implementation, works with tools that don't exist yet, matches where the ecosystem is heading.
- **`--fix` never runs silently.** Cost and safety both require explicit user action every time until a persistent opt-in is set.
- **Name:** `ohnoo` — chosen after `yikes`, `oof`, `splat`, and `ohno` were all found taken or too close conceptually to existing packages.
- **PyPI only, no npm distribution.** The npm wrapper (`bin/ohnoo.js`, `package.json`) was removed: it added a second, thinner install path that just shelled out to the same Python binary anyway (so it saved a user nothing they couldn't get from `pip install ohnoo` / `pipx install ohnoo`), and it had its own command-injection surface on Windows (`spawnSync(..., { shell: true })` forwarding raw argv into a shell). Not worth maintaining two packaging pipelines for.
