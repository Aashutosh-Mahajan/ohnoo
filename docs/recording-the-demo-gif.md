# Recording the launch GIF

The README (and the website's Home hero, see `CLAUDE.md` section 7.2) both
lead with a recording of the actual crash → roast → fix sequence. This doc
is a step-by-step guide for a human to record that GIF with
[`vhs`](https://github.com/charmbracelet/vhs) — no image/GIF file is
generated as part of this task, this is just the recipe.

## 1. Install vhs

```bash
brew install vhs
# or: go install github.com/charmbracelet/vhs@latest
```

`vhs` needs `ttyd` and `ffmpeg` on `$PATH` as well — see the vhs README for
platform-specific install instructions if `vhs` complains about missing
dependencies.

## 2. Prepare a clean demo environment

Record in a throwaway directory so the terminal history and prompt are
uncluttered, and make sure `ohnoo` is installed and `ohnoo init` has already
been run in that shell so the hook is live:

```bash
mkdir /tmp/ohnoo-demo && cd /tmp/ohnoo-demo
pip install ohnoo
ohnoo init
# open a new shell so the hook is loaded, then cd back into /tmp/ohnoo-demo
```

Create the one file the demo will crash on:

```bash
cat > app.py <<'EOF'
import requests

print("fetching...")
EOF
```

(`requests` is intentionally not installed, so running this raises a real
`ModuleNotFoundError` for `ohnoo` to catch.)

## 3. Write the `.tape` script

Save this as `demo.tape` in the same directory:

```tape
# demo.tape — ohnoo launch GIF
Output demo.gif

Set Shell "bash"
Set FontSize 20
Set Width 1200
Set Height 600
Set Padding 20
Set Theme "Dracula"
Set TypingSpeed 60ms

# Let the terminal settle before typing anything
Sleep 500ms

Type "python app.py"
Sleep 500ms
Enter

# Give ohnoo time to catch the crash, match the pattern, and print the roast
Sleep 2s

# Show the fix actually working
Type "pip install requests"
Sleep 500ms
Enter
Sleep 2s

Type "python app.py"
Sleep 500ms
Enter
Sleep 1500ms
```

Notes on the settings:
- `1200x600` matches a typical README-width GIF without looking stretched.
- `FontSize 20` stays legible at that size without cramming too many columns.
- `TypingSpeed 60ms` makes the typed commands readable instead of an
  instant paste-in, which reads as more "real."
- Swap `Set Theme "Dracula"` for whatever terminal theme best matches the
  site's charcoal/international-orange palette (see `CLAUDE.md` section
  7.1) if a closer visual match to the docs site is wanted.

## 4. Record

```bash
vhs demo.tape
```

This produces `demo.gif` in the same directory.

## 5. Review and place the file

- Watch the GIF at actual size — confirm the roast line and fix command are
  both fully readable, and that the total runtime is short (aim for
  6-10 seconds; trim `Sleep` durations in the tape if it drags).
- Once approved, save it as `docs/assets/demo.gif` (create the `assets/`
  directory if it doesn't exist) and replace the placeholder HTML comment
  at the top of `README.md`:

  ```diff
  - <!-- TODO: launch GIF here, recorded via vhs (https://github.com/charmbracelet/vhs) showing crash -> roast -> fix -->
  + ![ohnoo catching a crash, roasting it, and fixing it](docs/assets/demo.gif)
  ```

- The same GIF (or a variant re-recorded at a different aspect ratio) is
  also what the website's Home page hero uses per `CLAUDE.md` section 7.2.
