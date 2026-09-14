import Mascot from "./Mascot";
import Reveal from "./Reveal";
import TerminalWindow from "./TerminalWindow";

const CRASHES = [
  {
    file: "app.py",
    pose: "shocked",
    caption: "Python — a classic",
    lines: [
      { t: "$ python app.py", cls: "t-prompt" },
      { t: "Traceback (most recent call last):", cls: "t-err" },
      { t: "ModuleNotFoundError: No module named 'requests'", cls: "t-err" },
      { t: "ohnoo: 'requests' is currently on a coffee break. Also it's not installed.", cls: "t-roast" },
      { t: "  fix: pip install requests", cls: "t-fix" },
    ],
  },
  {
    file: "server.js",
    pose: "smirk",
    caption: "Node — you know why",
    lines: [
      { t: "$ node server.js", cls: "t-prompt" },
      { t: "Error: listen EADDRINUSE :::3000", cls: "t-err" },
      { t: "ohnoo: Port 3000 is already taken. By you. Twenty minutes ago.", cls: "t-roast" },
      { t: "  fix: lsof -ti :3000 | xargs kill -9", cls: "t-fix" },
    ],
  },
  {
    file: "~/project",
    pose: "deadpan",
    caption: "Git — deadpan, every time",
    lines: [
      { t: "$ git status", cls: "t-prompt" },
      { t: "fatal: not a git repository", cls: "t-err" },
      { t: "ohnoo: This isn't a git repo. It's just a folder with dreams.", cls: "t-roast" },
      { t: "  fix: git init", cls: "t-fix" },
    ],
  },
];

export default function CrashGallery() {
  return (
    <section className="section" id="crashes">
      <div className="wrap">
        <Reveal className="gallery-head">
          <div>
            <p className="eyebrow">a day in your terminal</p>
            <h2>
              Three crashes ohnoo has seen before.
              <br />
              (and yours, probably.)
            </h2>
          </div>
          <p>
            Real patterns, real jokes, real fix commands — pulled straight from the pattern
            database, not made up for this page.
          </p>
        </Reveal>

        <div className="gallery">
          {CRASHES.map((c) => (
            <Reveal as="div" className="card" key={c.file}>
              <TerminalWindow title={c.file} dense>
                {c.lines.map((line, i) => (
                  <div key={i} className={line.cls}>
                    {line.t}
                  </div>
                ))}
              </TerminalWindow>
              <div className="card-caption">
                <Mascot pose={c.pose} size={22} />
                {c.caption}
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}
