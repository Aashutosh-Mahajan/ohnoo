import { useState } from "react";

export default function CopyLine({ command }) {
  const [copied, setCopied] = useState(false);

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(command);
      setCopied(true);
      setTimeout(() => setCopied(false), 1400);
    } catch {
      // Clipboard API can be unavailable; the command text is still visible.
    }
  }

  return (
    <div className="install-line">
      <span className="p1">$</span>
      <span className="cmd">{command}</span>
      <button type="button" onClick={handleCopy}>
        {copied ? "copied" : "copy"}
      </button>
    </div>
  );
}
