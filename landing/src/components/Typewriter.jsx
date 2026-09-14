import { useEffect, useState } from "react";

function prefersReducedMotion() {
  return typeof window !== "undefined" && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

/**
 * Types out `lines` (array of {text, className}) once, then holds the
 * finished state for a long pause before looping. The hold is deliberately
 * much longer than the typing itself, so the page spends most of its time
 * showing the COMPLETE message rather than a mid-word fragment — a static
 * screenshot or a distracted glance should almost always land on finished
 * text, not "ohnoo: have you trie".
 */
export default function Typewriter({ lines, typingMs = 16, holdMs = 5000 }) {
  const [progress, setProgress] = useState(() =>
    prefersReducedMotion() ? { lineIndex: lines.length, charIndex: 0 } : { lineIndex: 0, charIndex: 0 }
  );

  useEffect(() => {
    if (prefersReducedMotion()) return;

    // Plain local variable drives the loop (not React state) so the timer
    // logic stays a simple, pure step function — setProgress is only ever
    // called with a concrete value, never a functional updater that itself
    // schedules a timeout (which StrictMode's double-invoke would duplicate).
    let current = { lineIndex: 0, charIndex: 0 };
    let timer;

    function step() {
      if (current.lineIndex >= lines.length) {
        timer = setTimeout(() => {
          current = { lineIndex: 0, charIndex: 0 };
          setProgress(current);
          timer = setTimeout(step, typingMs);
        }, holdMs);
        return;
      }

      const line = lines[current.lineIndex];
      if (current.charIndex <= line.text.length) {
        current = { ...current, charIndex: current.charIndex + 1 };
        setProgress(current);
        timer = setTimeout(step, typingMs + Math.random() * 18);
      } else {
        current = { lineIndex: current.lineIndex + 1, charIndex: 0 };
        setProgress(current);
        timer = setTimeout(step, 220);
      }
    }

    timer = setTimeout(step, typingMs);
    return () => clearTimeout(timer);
  }, [lines, typingMs, holdMs]);

  const { lineIndex, charIndex } = progress;
  const done = lineIndex >= lines.length;

  return (
    <>
      {lines.slice(0, done ? lines.length : lineIndex).map((line, i) => (
        <div key={i} className={line.className}>
          {line.text}
        </div>
      ))}
      {!done && (
        <div className={lines[lineIndex].className}>
          {lines[lineIndex].text.slice(0, charIndex)}
          <span className="t-caret" />
        </div>
      )}
      {done && <span className="t-caret" />}
    </>
  );
}
