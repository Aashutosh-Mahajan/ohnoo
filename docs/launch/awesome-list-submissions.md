# awesome-list submission drafts

Per CLAUDE.md Phase 7: submit to `awesome-cli-apps` and `awesome-devtools`
style lists. Each list has its own contribution format and alphabetical
ordering convention — check the specific list's CONTRIBUTING.md before
opening a PR, since these are community-maintained and picky about format.
Do not open these PRs until the repo is public, has a real README with the
demo GIF, and has at least a few stars/some activity — a submission to a
brand-new, empty-looking repo gets rejected far more often than one that
already looks alive.

## Candidate lists (verify these still exist and are actively maintained before submitting)

- `sindresorhus/awesome` (or one of its more specific children — check for an
  existing "CLI tools" or "developer tools" awesome-list first, since
  submitting to the right specific list matters more than the biggest one)
- Any `awesome-cli-apps`-named list with recent commit activity
- Any `awesome-devtools`-named list with recent commit activity
- Consider a Python-specific list too, since ohnoo installs via pip
  (something like `vinta/awesome-python`'s "Downloader"/"CLI" adjacent
  sections, if a fitting category exists)

## Suggested one-line entry format

Most awesome-lists use: `- [name](repo-url) - one-sentence description.`

```
- [ohnoo](https://github.com/Aashutosh-Mahajan/ohnoo) - Catches your shell crash, roasts it in one line, and hands off to an AI coding agent (or an offline pattern DB) for the real fix.
```

Adjust wording to match the surrounding entries' tone/length in whichever
specific list you're submitting to — a wildly different style than its
neighbors reads as an obviously mass-submitted PR and gets rejected more
often.

## PR checklist for each submission

1. Read that list's CONTRIBUTING.md in full.
2. Confirm alphabetical placement in the correct category.
3. One entry per PR, not a batch — most awesome-list maintainers explicitly
   ask for this.
4. Double-check the list doesn't already have a very similar tool listed
   (e.g. `thefuck`) right next to where yours would go, and consider
   referencing the differentiation in the PR description (not the list
   entry itself) if a maintainer asks.
