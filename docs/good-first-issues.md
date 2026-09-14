# Good first issues — seed list

Draft tickets for a maintainer to copy into real GitHub issues at launch
(labelled `good first issue` + `pattern-request`, using the pattern request
template). Each is a concrete "add a pattern for X" task, checked against the
existing entries in `src/ohnoo/patterns/*.json` as of this writing so none of
these duplicate a pattern that already exists.

Existing pattern IDs for reference (do not duplicate these):
`py-module-not-found`, `py-indentation-error`, `py-syntax-error`,
`py-name-error`, `py-attribute-error`, `py-type-error-arg-count`,
`py-key-error`, `py-index-error`, `py-zero-division`,
`py-import-error-circular`, `py-file-not-found`, `py-recursion-error`,
`py-value-error-int`, `py-permission-error`, `node-eaddrinuse`,
`node-cannot-find-module`, `node-undefined-not-a-function`,
`node-cannot-read-property-of-undefined`, `node-unhandled-promise-rejection`,
`node-syntax-error-unexpected-token`, `node-enoent`, `node-npm-err-peer-dep`,
`node-max-call-stack`, `node-cors-error`, `node-jest-no-tests`,
`node-heap-out-of-memory`, `node-econnrefused`, `node-typescript-type-error`,
`git-not-a-repository`, `git-merge-conflict`, `git-detached-head`,
`git-non-fast-forward`, `git-nothing-to-commit`,
`git-permission-denied-publickey`, `git-remote-already-exists`,
`git-large-file-rejected`, `git-uncommitted-changes-checkout`,
`git-branch-not-found`, `git-cannot-lock-ref`, `git-diverged-branches`,
`docker-daemon-not-running`, `docker-port-already-allocated`,
`docker-image-not-found`, `docker-no-space-left`,
`docker-container-exited-nonzero`, `npm-eresolve`,
`npm-enoent-package-json`, `npm-permission-denied-global`,
`pip-could-not-find-version`, `pip-externally-managed-environment`.

---

## Python

1. **Add a pattern for `ImportError: cannot import name X from Y`** (non-circular)
   Covers the plain "the name doesn't exist in that module" case — distinct
   from the existing `py-import-error-circular`, which only covers the
   partially-initialized-module variant.

2. **Add a pattern for `UnicodeDecodeError`**
   Covers reading a file with the wrong encoding (e.g. `'utf-8' codec can't
   decode byte...`), a very common file-I/O crash not yet in `python.json`.

3. **Add a pattern for `TabError: inconsistent use of tabs and spaces`**
   Distinct from `py-indentation-error` (which matches generic
   `IndentationError`) — `TabError` is its own exception type in Python 3.

4. **Add a pattern for `venv`/`ModuleNotFoundError` on `pip` itself**
   Covers `No module named pip` inside a broken or incomplete virtualenv —
   a different failure mode than a missing third-party package.

## Node.js

5. **Add a pattern for `Error [ERR_MODULE_NOT_FOUND]` (ESM import errors)**
   Covers Node's ESM-specific "Cannot find module" phrasing, which differs
   from the CommonJS `Error: Cannot find module` already covered by
   `node-cannot-find-module`.

6. **Add a pattern for `SyntaxError: Cannot use import statement outside a module`**
   The classic "you're mixing ESM and CommonJS" crash — extremely common for
   first-time ESM users and not yet covered.

7. **Add a pattern for npm's `EEXIST` on `npm install` / global bin conflicts**
   Covers `npm ERR! EEXIST: file already exists` during install, distinct
   from the existing `npm-permission-denied-global` (`EACCES`).

8. **Add a pattern for `Error: listen EACCES` (privileged port binding)**
   Covers trying to bind to a port under 1024 without privileges — distinct
   from `node-eaddrinuse`, which is about the port already being taken.

## Git

9. **Add a pattern for `fatal: refusing to merge unrelated histories`**
   A common early-project gotcha when combining two repos or re-initializing
   history, not yet covered by any `git.json` entry.

10. **Add a pattern for `error: failed to push some refs` (generic, non-diverged)**
    Covers the generic rejected-push message shown before the more specific
    non-fast-forward or diverged-branches text — useful as a catch-all.

11. **Add a pattern for `fatal: The current branch has no upstream branch`**
    The "you forgot `--set-upstream`" crash on a fresh branch's first push —
    very common for new contributors, not yet in `git.json`.

## Docker / npm / pip

12. **Add a pattern for `docker-compose`'s `Version in "./docker-compose.yml" is unsupported`**
    Covers the Compose schema-version mismatch error, a distinct failure mode
    from the existing `docker.json` entries (daemon, ports, images, disk,
    exit codes).

13. **Add a pattern for pip's `error: Microsoft Visual C++ 14.0 or greater is required`**
    The extremely common Windows build-toolchain error when installing a
    package with native extensions — not yet covered by `pip-*` entries.

14. **Add a pattern for npm's `npm warn deprecated` escalating into a hard failure via `--strict-peer-deps`**
    Or alternatively, `npm ERR! code ENOTFOUND` (registry unreachable /
    offline install attempt) — either is a distinct, uncovered npm failure
    mode.

## Stretch — new language categories (optional, forward-looking)

Per `CLAUDE.md` section 1, Python and Node are the v1 focus and "other
runtimes are additive later" — these are good stretch issues for a
contributor who wants to bootstrap a whole new category, not blockers for
launch.

15. **Create `src/ohnoo/patterns/rust.json` and seed it with `cargo` errors**
    Start with 3-5 patterns: `error[E0382]: borrow of moved value`,
    `error: linking with 'cc' failed`, and `cargo: command not found`.
    Requires adding `rust` as a `language` value and confirming the pattern
    loader in `src/ohnoo/` picks up the new file via its
    `PATTERNS_DIR.glob("*.json")` scan (see `docs/pattern-contribution.md`).

16. **Create `src/ohnoo/patterns/go.json` and seed it with `go build`/`go run` errors**
    Start with 3-5 patterns: `undefined: X`, `package X is not in GOROOT`,
    and `go: cannot find main module`. Same loader/schema notes as above.
