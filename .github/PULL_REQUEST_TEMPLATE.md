## What does this PR do?

<!-- Short description of the change and why it's needed. -->

## Type of change

- [ ] New pattern (adds/edits an entry in `src/ohnoo/patterns/*.json`)
- [ ] Bugfix
- [ ] Feature
- [ ] Docs
- [ ] Other

## If this PR adds or edits a pattern

See [docs/pattern-contribution.md](../docs/pattern-contribution.md) for the
full schema and guidelines. Before opening this PR, please confirm:

- [ ] I ran `pytest tests/test_pattern_schema.py` locally and it passes
- [ ] My pattern's `id` is unique (not reused from any existing entry)
- [ ] My `matcher.pattern` regex compiles and matches a real example of the error
- [ ] The `fix` field contains a real, working fix command (or a clear summary if no single command applies), never just a joke
- [ ] I included 5-10 joke variants

## Notes for reviewers

<!-- Anything else worth flagging: edge cases, alternatives considered, etc. -->
