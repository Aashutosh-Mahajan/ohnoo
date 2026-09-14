import { useEffect, useState } from "react";

/** Fixed scanlines + vignette + a one-time boot flicker. Pure decoration,
 * pointer-events disabled, never repaints on scroll since it's fixed. */
export default function CrtOverlay() {
  const [booting, setBooting] = useState(
    typeof window !== "undefined" && !window.matchMedia("(prefers-reduced-motion: reduce)").matches
  );

  useEffect(() => {
    if (!booting) return;
    const t = setTimeout(() => setBooting(false), 750);
    return () => clearTimeout(t);
  }, [booting]);

  return (
    <>
      <div className="crt-scanlines" aria-hidden="true" />
      <div className="crt-vignette" aria-hidden="true" />
      <div className={`crt-flash ${booting ? "boot" : ""}`} aria-hidden="true" />
    </>
  );
}
