import CopyLine from "./CopyLine";
import Mascot from "./Mascot";
import Reveal from "./Reveal";

const STATS = [
  { n: "102+", l: "ways to humiliate you" },
  { n: "0", l: "network calls by default" },
  { n: "1", l: "developer roasted so far (its creator)" },
];

export default function FooterCta() {
  return (
    <section className="section footer-cta">
      <div className="wrap">
        <Reveal className="mascot-slot">
          <Mascot pose="happy" filled size={72} />
        </Reveal>
        <Reveal as="p" className="eyebrow" style={{ justifyContent: "center" }}>
          no api key required for any of this
        </Reveal>
        <Reveal as="h2">
          Your next crash is coming.
          <br />
          Might as well enjoy it.
        </Reveal>
        <Reveal as="p">
          One command, fully offline, works on a plane. The AI stuff is there if you want it —
          never if you don't.
        </Reveal>
        <Reveal className="install-row">
          <CopyLine command="pip install ohnoo && ohnoo init" />
        </Reveal>

        <Reveal className="stat-row">
          {STATS.map((s) => (
            <div className="stat" key={s.l}>
              <span className="n">{s.n}</span>
              <span className="l">{s.l}</span>
            </div>
          ))}
        </Reveal>
      </div>
    </section>
  );
}
