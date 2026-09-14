import CopyLine from "./CopyLine";
import TerminalWindow from "./TerminalWindow";
import Typewriter from "./Typewriter";

const HERO_LINES = [
  { text: "$ python deploy.py", className: "t-prompt" },
  { text: "Traceback (most recent call last):", className: "t-err" },
  { text: "ConnectionError: Failed to establish a new connection", className: "t-err" },
  { text: "ohnoo: The server isn't listening. Have you tried starting it?", className: "t-roast" },
  { text: "  fix: check the target host/port is actually running", className: "t-fix" },
];

export default function Hero() {
  return (
    <section className="section hero" id="top">
      <div className="wrap hero-grid">
        <TerminalWindow title="zsh — 80×12">
          <Typewriter lines={HERO_LINES} />
        </TerminalWindow>

        <div className="hero-copy">
          <p className="eyebrow">a terminal companion, not a chat window</p>
          <h1>
            ohnoo roasts your crash,
            <br />
            then <span className="accent">actually fixes it.</span>
          </h1>
          <p className="lede">
            The next time a command exits non-zero, ohnoo matches it against a local database of
            102 known ways your code embarrasses you, prints a one-line joke, and hands you the
            real fix — like <code className="inline">pip install requests</code>, not a shrug.
          </p>
          <div className="install-row">
            <CopyLine command="pip install ohnoo && ohnoo init" />
            <a className="scroll-cue" href="#crashes">
              see it roast something ↓
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}
