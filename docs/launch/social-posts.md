# Cross-post drafts

Per CLAUDE.md Phase 7: r/programming, r/Python, r/node, r/commandline. Each
subreddit has a different tolerance for "look what I built" posts — adjust
tone accordingly, and check each subreddit's current self-promotion rules
before posting (they change and are strictly enforced). Don't post to all
four on the same day; space them out so it doesn't read as a coordinated
blast, and so you have bandwidth to answer comments on each.

## r/commandline

Most receptive audience for a pure terminal tool. Lead with the demo.

```
Title: ohnoo – a terminal tool that roasts your crash and gives you the real fix

Built this after one too many silent `ModuleNotFoundError`s. `ohnoo init`
hooks your shell; the next non-zero exit gets matched against a local
pattern DB (100+ patterns, Python/Node/Git/Docker/npm/pip so far) and you
get a one-line joke plus the actual fix command. Fully offline for that
layer — no network calls.

If you've got Claude Code / Codex CLI / an Antigravity install, `ohnoo
--explain` or `ohnoo --fix` can hand off unrecognized errors to it. There's
also an MCP server mode and an opt-in hosted-LLM fallback if you want one.

[demo gif]
[repo link]

Patterns are just JSON — PRs for missing errors very welcome.
```

## r/Python

Lead with the Python-specific pain point and the pip install, since that's
the entry point for this audience.

```
Title: ohnoo: pip install a shell companion that explains + fixes your Python crashes

`pip install ohnoo && ohnoo init` — next time a Python script exits
non-zero, it matches the traceback against a local pattern database (30+
Python-specific patterns right now: ModuleNotFoundError, IndentationError,
circular imports, asyncio errors, etc.) and prints a one-line joke plus the
actual fix command (e.g. `pip install <package>` for a missing module, with
the package name pulled straight from your traceback).

Everything in this base layer is offline, no telemetry, no API key needed.
If you want more, it can optionally hand off to an AI coding agent already
on your machine, or an opt-in hosted LLM fallback for anything the pattern
DB doesn't recognize yet.

[repo link] — patterns are just JSON entries, contributions welcome
```

## r/node

Same shape, Node-flavored pain points.

```
Title: ohnoo: catches EADDRINUSE/Cannot find module/etc, roasts it, gives you the fix

Shell hook + local pattern DB (30 Node-specific patterns so far — EADDRINUSE,
Cannot find module, unhandled promise rejections, ESM/CommonJS interop
errors, webpack resolution failures, etc.). No network calls for this layer.
Optional handoff to an installed AI coding agent, optional MCP server mode
for IDE-embedded agents, optional opt-in hosted-LLM fallback.

pip install ohnoo && ohnoo init (yes, it's a Python CLI even though it's
aimed at Node devs too — npm wrapper also available: npm i -g ohnoo, which
just shells out to the same binary)

[repo link]
```

## r/programming

Broadest, most skeptical audience — lead with the interesting design
decision (four-layer cascade, not just "haha error message") rather than
the joke gimmick, since r/programming tends to reward substance over humor
in the title.

```
Title: ohnoo: a four-layer fallback cascade for diagnosing shell crashes (offline pattern match -> AI agent handoff -> MCP -> hosted LLM)

The interesting part isn't really the jokes (though there are jokes) — it's
the fallback design: an offline pattern-matching layer that's instant and
needs zero setup, falling back to whatever AI coding agent you already have
installed via a scoped, cost-transparent handoff, falling back to a passive
MCP server any IDE-embedded agent can call into directly, falling back to
an entirely opt-in hosted LLM call as a last resort — each layer degrading
gracefully to the next with zero silent network calls unless you've
explicitly opted in.

[repo link] [demo gif]
```

## General posting notes

- Check current self-promotion rules on each subreddit before posting — several require a minimum account age/karma or a specific self-promo day/thread.
- Don't crosspost identical text to all four; the wording above is intentionally different per audience.
- Respond to every top-level comment for at least the first few hours.
