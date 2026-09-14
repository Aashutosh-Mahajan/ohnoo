import Reveal from "./Reveal";

const COMMANDS = [
  { cmd: "init [--shell <s>]", desc: "Install the shell hook. bash, zsh, fish, or powershell. Idempotent." },
  { cmd: "explain", desc: "Layer 2, read-only: ask an installed agent to diagnose the last error." },
  { cmd: "fix", desc: "Layer 2, edit-allowed: same, but confirms before anything runs." },
  { cmd: "share", desc: "Render the last roast as a shareable terminal PNG." },
  { cmd: "vibe [name]", desc: "Show or persist a default personality pack." },
  { cmd: "stats", desc: "Local-only roast counts. Nothing leaves your machine." },
  { cmd: "setup-ai [--disable]", desc: "Configure the opt-in hosted fallback, or turn it back off." },
  { cmd: "mcp-server [--port]", desc: "Start the Layer 3 server. Defaults to 127.0.0.1:8420." },
];

export default function Reference() {
  return (
    <section className="section" id="reference">
      <div className="wrap">
        <Reveal style={{ marginBottom: 32 }}>
          <p className="eyebrow">the actual docs, not a marketing page</p>
          <h2 style={{ fontSize: "clamp(24px,3vw,32px)" }}>man ohnoo</h2>
        </Reveal>

        <Reveal className="manpage">
          <div className="manpage-bar">
            <span>OHNOO(1)</span>
            <span>User Commands</span>
            <span>OHNOO(1)</span>
          </div>
          <div className="manpage-body">
            <div className="man-section-title">Name</div>
            <div>ohnoo — catches your crash, roasts it, and points you at the fix.</div>

            <div className="man-section-title">Synopsis</div>
            <div>
              <code className="inline">cmd 2&gt;&amp;1 | ohnoo</code> &nbsp;or&nbsp;{" "}
              <code className="inline">ohnoo [command] [options]</code>
            </div>

            <div className="man-section-title">Commands</div>
            {COMMANDS.map((c) => (
              <div className="man-row" key={c.cmd}>
                <span className="cmd">{c.cmd}</span>
                <span className="desc">{c.desc}</span>
              </div>
            ))}

            <div className="man-section-title">Options</div>
            <div className="man-row">
              <span className="cmd">--vibe &lt;name&gt;</span>
              <span className="desc">default, gordon-ramsay, zen, or sarcastic-senior-dev. This run only.</span>
            </div>

            <div className="man-section-title">See also</div>
            <div className="man-row">
              <span className="cmd">docs/pattern-contribution.md</span>
              <span className="desc">How to add the 103rd way your code can humiliate you.</span>
            </div>
          </div>
        </Reveal>
      </div>
    </section>
  );
}
