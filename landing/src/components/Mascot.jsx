const BODY_PATH =
  "M20,85 L20,42 C20,20 33,8 50,8 C67,8 80,20 80,42 L80,85 L70,74 L60,85 L50,74 L40,85 L30,74 Z";

function Face({ pose }) {
  switch (pose) {
    case "shocked":
      return (
        <>
          <rect className="eye" x="33" y="37" width="13" height="16" rx="3" />
          <rect className="eye" x="54" y="37" width="13" height="16" rx="3" />
          <rect className="mouth-fill" x="42" y="58" width="16" height="18" rx="6" />
        </>
      );
    case "smirk":
      return (
        <>
          <rect className="eye" x="34" y="40" width="11" height="13" rx="3" />
          <rect className="eye" x="55" y="40" width="11" height="13" rx="3" />
          <path className="mouth-line" d="M38,61 Q50,76 64,57" />
        </>
      );
    case "deadpan":
      return (
        <>
          <rect className="eye" x="34" y="40" width="11" height="13" rx="3" />
          <rect className="eye" x="55" y="40" width="11" height="13" rx="3" />
          <rect
            className="mouth-fill"
            x="50"
            y="34"
            width="15"
            height="3"
            rx="1.5"
            transform="rotate(-9 57.5 35.5)"
          />
          <rect className="mouth-fill" x="41" y="64" width="18" height="4.5" rx="2.25" />
        </>
      );
    case "gordon":
      return (
        <>
          <path
            className="mouth-line"
            d="M28,35 L42,42"
            stroke="var(--phosphor)"
            strokeWidth="3"
            strokeLinecap="round"
            fill="none"
          />
          <path
            className="mouth-line"
            d="M72,35 L58,42"
            stroke="var(--phosphor)"
            strokeWidth="3"
            strokeLinecap="round"
            fill="none"
          />
          <rect className="eye" x="34" y="42" width="11" height="11" rx="2" />
          <rect className="eye" x="55" y="42" width="11" height="11" rx="2" />
          <rect className="mouth-fill" x="38" y="60" width="24" height="17" rx="5" />
        </>
      );
    case "zen":
      return (
        <>
          <circle
            cx="50"
            cy="46"
            r="44"
            fill="none"
            stroke="var(--phosphor-dim)"
            strokeWidth="1.5"
            opacity="0.5"
          />
          <rect className="mouth-fill" x="33" y="45" width="13" height="3" rx="1.5" />
          <rect className="mouth-fill" x="54" y="45" width="13" height="3" rx="1.5" />
          <path className="mouth-line" d="M41,64 Q50,69 59,64" />
        </>
      );
    case "senior":
      return (
        <>
          <rect x="30" y="44" width="18" height="12" rx="2" fill="none" stroke="var(--phosphor)" strokeWidth="2" />
          <rect x="52" y="44" width="18" height="12" rx="2" fill="none" stroke="var(--phosphor)" strokeWidth="2" />
          <line x1="48" y1="49" x2="52" y2="49" stroke="var(--phosphor)" strokeWidth="2" />
          <rect className="eye" x="35" y="48" width="6" height="4" rx="1" />
          <rect className="eye" x="57" y="48" width="6" height="4" rx="1" />
          <rect className="mouth-fill" x="41" y="64" width="18" height="3.5" rx="1.75" />
        </>
      );
    case "happy":
      return (
        <>
          <rect className="eye" x="34" y="40" width="11" height="13" rx="3" />
          <rect className="eye" x="55" y="40" width="11" height="13" rx="3" />
          <path className="mouth-line" d="M39,60 Q50,72 61,60" />
        </>
      );
    case "neutral":
    default:
      return (
        <>
          <rect className="eye" x="34" y="40" width="11" height="13" rx="3" />
          <rect className="eye" x="55" y="40" width="11" height="13" rx="3" />
          <rect className="mouth-fill" x="41" y="63" width="18" height="4.5" rx="2.25" />
        </>
      );
  }
}

/** The ohnoo pixel-ghost mascot. `pose` picks the expression; `filled` swaps
 * the outline-on-dark look for a solid phosphor-green fill (used for the
 * one big moment at the end of the page). */
export default function Mascot({ pose = "neutral", filled = false, size = 26, className = "", title }) {
  return (
    <svg
      className={`mascot ${filled ? "filled" : ""} ${className}`.trim()}
      width={size}
      height={size}
      viewBox="0 0 100 100"
      role={title ? "img" : "presentation"}
      aria-hidden={title ? undefined : true}
    >
      {title && <title>{title}</title>}
      <path className="body" d={BODY_PATH} />
      <Face pose={pose} />
    </svg>
  );
}
