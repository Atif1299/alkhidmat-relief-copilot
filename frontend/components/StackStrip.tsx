const STACK = ["Qwen", "DashScope", "LangGraph", "FastAPI", "Cloud Run"] as const;

export function StackStrip() {
  return (
    <p className="stack-strip" aria-label="Platform stack">
      {STACK.map((item, i) => (
        <span key={item}>
          {i > 0 ? <span className="stack-dot" aria-hidden="true"> · </span> : null}
          {item}
        </span>
      ))}
    </p>
  );
}
