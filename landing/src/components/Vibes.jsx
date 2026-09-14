import Mascot from "./Mascot";
import Reveal from "./Reveal";

const VIBES = [
  {
    pose: "neutral",
    name: "default",
    tagline: "dry, a little tired",
    quote: "\"Python looked everywhere for 'requests' and found nothing, much like your test coverage.\"",
  },
  {
    pose: "gordon",
    name: "gordon-ramsay",
    tagline: "it's RAW",
    quote: "\"IT'S NOT INSTALLED! 'requests' IS RAW! You forgot to pip install it, you donut!\"",
  },
  {
    pose: "zen",
    name: "zen",
    tagline: "breathe. it's fine.",
    quote: "\"The module 'requests' does not yet exist in your environment. This too can be resolved.\"",
  },
  {
    pose: "senior",
    name: "sarcastic-senior-dev",
    tagline: "seen this one before",
    quote: "\"'requests' isn't installed. Yes, again. pip install exists for a reason.\"",
  },
];

export default function Vibes() {
  return (
    <section className="section" id="vibes">
      <div className="wrap">
        <Reveal style={{ marginBottom: 36 }}>
          <p className="eyebrow">same crash, four personalities</p>
          <h2 style={{ fontSize: "clamp(24px,3vw,32px)" }}>Pick your vibe.</h2>
          <p className="section-lede">
            <code className="inline">ohnoo vibe &lt;name&gt;</code> swaps the joke, never the fix.
            Here's the exact same <code className="inline">ModuleNotFoundError</code> in each one.
          </p>
        </Reveal>

        <Reveal className="vibe-grid" as="div">
          {VIBES.map((v) => (
            <div className="vibe-card" key={v.name}>
              <div className="vibe-head">
                <Mascot pose={v.pose} size={40} />
                <div>
                  <div className="vibe-name">{v.name}</div>
                  <div className="vibe-tagline">{v.tagline}</div>
                </div>
              </div>
              <div className="vibe-quote">{v.quote}</div>
            </div>
          ))}
        </Reveal>
      </div>
    </section>
  );
}
