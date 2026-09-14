export default function TerminalWindow({ title, children, dense = false, className = "" }) {
  return (
    <div className={`terminal ${className}`.trim()}>
      <div className="terminal-bar">
        <span className="dot" />
        <span className="dot" />
        <span className="dot" />
        <span className="title">{title}</span>
      </div>
      <div className={`terminal-body ${dense ? "dense" : ""}`.trim()}>{children}</div>
    </div>
  );
}
