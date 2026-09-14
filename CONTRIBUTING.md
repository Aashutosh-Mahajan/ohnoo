# Contributing to ohnoo

Thanks for considering it. `ohnoo` is small on purpose, and the easiest way
to contribute is usually the one that doesn't touch Python at all: adding a
pattern.

## Ways to contribute

| I want to... | Do this |
|---|---|
| Report a bug | Open a [bug report](../../issues/new?template=bug_report.md) |
| Request an error pattern | Open a [pattern request](../../issues/new?template=pattern_request.md) |
| Add a pattern myself | Skip the issue, go straight to a PR — see below |
| Suggest a feature | Open a [feature request](../../issues/new?template=feature_request.md) |
| Ask a question | Open a [question](../../issues/new?template=question.md) |
| Fix a bug / add a feature | Fork, branch, PR — see below |

## Adding a pattern (the fast path)

This is the single most valuable contribution and doesn't require reading
any of the code below. Patterns live in `src/ohnoo/patterns/*.json`. Full
schema and guidelines: [docs/pattern-contribution.md](docs/pattern-contribution.md).

```bash
git clone https://github.com/Aashutosh-Mahajan/ohnoo.git
cd ohnoo
python -m venv .venv && source .venv/bin/activate  # .venv\Scripts\activate on Windows
pip install -e ".[dev]"
# edit src/ohnoo/patterns/*.json
pytest tests/test_pattern_schema.py -q
```

If that passes, open a PR. That's the whole loop.

## Dev setup (for code changes)

### Python CLI (`src/ohnoo/`)

```bash
python -m venv .venv
source .venv/bin/activate      # .venv\Scripts\activate on Windows
pip install -e ".[dev,share,mcp,llm]"
pytest -q
ruff check src tests
```

All 100+ tests should pass and `ruff` should report no issues before you
open a PR. Tests that touch the filesystem (shell hook install, stats,
config) all use `tmp_path`/env-var overrides — never real dotfiles or the
real home directory. If you add a test that writes to disk, follow that
pattern.

### Landing page (`landing/`)

```bash
cd landing
npm install
npm run dev     # local preview
npm run lint    # oxlint
npm run build   # production build check
```

## Code style

- Python: `ruff` is the source of truth; run it before pushing.
- No comments explaining *what* code does — names should do that. A comment
  is for a non-obvious *why* (a workaround, a subtle invariant).
- Don't add abstractions, config flags, or error handling for cases that
  can't happen. Keep changes scoped to what the PR is actually about.
- React components in `landing/src/components/`: one component, one job.
  Follow the existing pattern (plain functions, no class components, no
  unnecessary state).

## Pull requests

1. One logical change per PR — a pattern addition and a CLI refactor don't
   belong in the same PR.
2. Fill in the PR template; it's short on purpose.
3. CI runs lint + tests automatically. A red CI check needs to be fixed
   before review, not explained away.
4. Be ready to iterate — review feedback here is about the code, not you.

## Reporting a security issue

Please don't open a public issue for a security vulnerability. Open a
[private security advisory](../../security/advisories/new) instead.

## Code of conduct

This project follows the [Code of Conduct](CODE_OF_CONDUCT.md). Short
version: be respectful, assume good faith, no harassment.

## Questions

If something here is unclear, that's a bug in this document — open a
[question](../../issues/new?template=question.md) rather than guessing.
