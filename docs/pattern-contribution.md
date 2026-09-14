# Adding a pattern to `ohnoo`

Patterns live in `src/ohnoo/patterns/*.json`, one array per language/tool
(`python.json`, `node.json`, `git.json`, `docker.json`). Every entry is
validated in CI against `src/ohnoo/patterns/schema.json`.

## Fields

| Field | Required | Notes |
|---|---|---|
| `id` | yes | Globally unique, kebab-case, never reused |
| `language` | yes | `python`, `node`, `git`, `docker`, `npm`, `pip`, or `generic` |
| `title` | no | Short human name, e.g. `ModuleNotFoundError` |
| `matcher` | yes | `{ "type": "regex" \| "exception_type" \| "substring", "pattern": "..." }` |
| `slots` | no | Maps numbered regex groups to names, e.g. `{"1": "module_name"}` |
| `jokes` | yes | 5-10 strings, may reference `{slot_name}` |
| `vibes` | no | Per-personality joke overrides, same shape as `jokes` |
| `fix` | yes | `{ "summary": "...", "command": "..." }` — always a real fix, never omitted |
| `personality_tag` | no | Groups patterns for `--vibe` reskinning |
| `tags` | no | Free-form tags |

## Writing a good matcher

- Prefer `regex` with named or numbered capture groups so the joke and fix
  can reference the actual filename/port/package from the error.
- Use `exception_type` for exceptions where the message text is too variable
  to regex reliably (e.g. `IndentationError`).
- Use `substring` only as a last resort — it's the least precise.

## Writing jokes

- 5-10 variants, so repeat crashes don't feel repetitive.
- Every joke variant must still make sense with any slot value filled in.
- Keep the real fix in the `fix` field, never buried only in a joke.

## Submitting

1. Add your entry to the appropriate file (or create a new one for a new
   language — update `PATTERNS_DIR.glob("*.json")` consumers accordingly).
2. Run `pytest -q` locally — this validates your entry against the schema,
   checks for duplicate IDs, and confirms your regex compiles.
3. Open a PR. CI runs the same checks.
