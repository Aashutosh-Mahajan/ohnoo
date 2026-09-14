# Show HN draft

Fill in the bracketed parts once the repo is public and the demo GIF is
recorded (see [../recording-the-demo-gif.md](../recording-the-demo-gif.md)).
Don't post until both exist — a Show HN with a broken/missing demo link
underperforms badly and rarely gets a second chance.

## Title

```
Show HN: ohnoo – catches your shell crash, roasts it, then actually fixes it
```

Keep it under 80 characters. Don't editorialize further than that; HN's own
crowd will do the "is this actually useful" debate in the comments.

## Post body

```
Hi HN,

ohnoo is a terminal companion for the moment right after a command crashes.
It's a spiritual successor to `thefuck` for that moment, not the "I mistyped
a command" moment `thefuck` was built for.

pip install ohnoo && ohnoo init

The next time a command exits non-zero, it matches the error against a local
pattern database (100+ patterns across Python/Node/Git/Docker/npm/pip right
now), prints a one-line joke, and — critically — always includes a real fix
command, never just the joke. Everything in this first layer is fully
offline: no network calls, no API key, works on a plane.

If the error isn't recognized, ohnoo can hand off to an AI coding agent you
already have installed (Claude Code, Codex CLI, Antigravity) via `ohnoo
--explain` (read-only) or `ohnoo --fix` (edits require confirmation, plus a
one-time cost-transparency warning since headless agent calls can bill
differently than interactive sessions). There's also a passive MCP server
mode (`ohnoo mcp-server`) so any MCP-aware IDE/agent can call the same
pattern engine directly, and an entirely opt-in hosted-LLM fallback
(`ohnoo setup-ai`, off by default, stores only the *name* of the env var
holding your key, never the key itself) for the small percentage of errors
nothing else recognizes.

[demo GIF / asciinema link here]

Repo: [github link]
Would love feedback, especially on which error patterns are missing — the
pattern DB is just JSON and PRs are very welcome
(docs/pattern-contribution.md).
```

## Timing notes

- Post Tuesday-Thursday, roughly 8-10am US Eastern, per general HN Show HN
  timing folklore (not a guarantee, just historically less noisy).
- Have 2-3 people ready to comment with genuine questions/feedback in the
  first 20 minutes — early engagement matters more than post quality for
  whether HN's ranking algorithm gives it a chance to be seen at all.
- Be present to respond to every comment for at least the first 3-4 hours.
