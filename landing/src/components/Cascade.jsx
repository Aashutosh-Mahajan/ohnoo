import Reveal from "./Reveal";

const FRAMES = [
  {
    idx: "01",
    fn: "at pattern_engine.match()",
    sub: "[offline]",
    body: "102 known errors matched locally against your error text. Instant, zero network calls, works on a plane.",
    tag: "always runs",
    tagClass: "on",
  },
  {
    idx: "02",
    fn: "at agent_handoff.explain_or_fix()",
    sub: "[opt-in]",
    body: (
      <>
        Only on <code className="inline">ohnoo explain</code> or <code className="inline">ohnoo fix</code>. Hands
        the traceback to claude, codex, or agy — whichever's on your $PATH. Fix always asks first.
      </>
    ),
    tag: "explicit only",
    tagClass: "opt",
  },
  {
    idx: "03",
    fn: "at mcp_server.listen()",
    sub: "[passive]",
    body: (
      <>
        Run <code className="inline">ohnoo mcp-server</code> and any MCP-aware IDE or agent can call ohnoo's
        diagnosis tools directly. ohnoo never calls out — it only answers.
      </>
    ),
    tag: "passive",
    tagClass: "opt",
  },
  {
    idx: "04",
    fn: "at llm_fallback.try()",
    sub: "[off by default]",
    body: (
      <>
        The last resort for errors nothing above recognized. Requires <code className="inline">ohnoo setup-ai</code>.
        Stores only the name of your API key's env var — never the key.
      </>
    ),
    tag: "off by default",
    tagClass: "opt",
  },
];

export default function Cascade() {
  return (
    <section className="section" id="cascade">
      <div className="wrap">
        <Reveal style={{ marginBottom: 44 }}>
          <p className="eyebrow">what actually happens, in order</p>
          <h2 style={{ fontSize: "clamp(24px,3vw,32px)" }}>The cascade, read like a stack trace.</h2>
          <p className="section-lede">
            Each layer only runs if the one above it didn't resolve the error — so here it is,
            bottom-up, the way a real trace reads.
          </p>
        </Reveal>

        <Reveal className="trace">
          <div className="trace-head">$ ohnoo --trace-cascade</div>
          {FRAMES.map((f) => (
            <div className="frame" key={f.idx}>
              <span className="idx">{f.idx}</span>
              <div>
                <h3>
                  {f.fn} <span className="sub">{f.sub}</span>
                </h3>
                <p>{f.body}</p>
              </div>
              <span className={`tag ${f.tagClass}`}>{f.tag}</span>
            </div>
          ))}
        </Reveal>
      </div>
    </section>
  );
}
