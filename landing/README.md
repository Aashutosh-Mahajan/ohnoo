# ohnoo landing page (React)

A componentized React (Vite) rewrite of the ohnoo landing page. Separate from `website/` (the app implementing `CLAUDE.md` Section 7's Home/Docs/Setup/Support site) — this is a more characterful, one-off take, not wired into that site's navigation.

## Concept

The whole page is styled as an old CRT terminal: scanlines, a boot-flicker on load, and a small pixel-ghost mascot (`src/components/Mascot.jsx`) that reacts differently in each section — shocked at a crash, smirking at the roast, deadpan at the git error, and rendered in four distinct personalities (default, gordon-ramsay, zen, sarcastic-senior-dev) in the "Pick your vibe" section, using the real per-vibe joke variants from `src/ohnoo/patterns/python.json`. The four-layer cascade is shown as an actual stack trace (numbered, since the order is real fallback information), and the command reference is styled as a real `man ohnoo` page using the project's actual CLI commands.

## Components

| Component | Responsibility |
|---|---|
| `Mascot` | The pixel-ghost, parameterized by `pose` (neutral/shocked/smirk/deadpan/gordon/zen/senior/happy) |
| `TerminalWindow` | Terminal chrome (traffic-light dots, title bar) wrapping any content |
| `Typewriter` | Types out a crash→roast→fix sequence once, then holds the *complete* state far longer than the typing itself |
| `CopyLine` | An install command with a working copy-to-clipboard button |
| `Reveal` | Scroll-triggered fade-in via `IntersectionObserver`, one instance per element |
| `CrtOverlay` | Fixed scanlines/vignette/boot-flicker, decorative only |
| `Nav`, `Hero`, `CrashGallery`, `Cascade`, `Vibes`, `Reference`, `FooterCta`, `SiteFooter` | The page sections |

## Develop

```bash
npm install
npm run dev
```

## Build

```bash
npm run build   # outputs to dist/
npm run preview
```

## Content accuracy

The command list, pattern count (102), per-vibe joke text, and four-layer descriptions were verified against `src/ohnoo/cli.py` and the pattern JSON files. The "1,000+ developers roasted" stat is intentionally playful/aspirational copy, not a real measured number — everything else is real.
