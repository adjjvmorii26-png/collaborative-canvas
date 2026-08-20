export function Badge({ tone = "", children }) {
  return <span className={`badge ${tone}`}>{children}</span>;
}

export function Stat({ k, v, hint }) {
  return (
    <div className="stat">
      <div className="k">{k}</div>
      <div className="v">
        {v}
        {hint ? <em>{hint}</em> : null}
      </div>
    </div>
  );
}

export function Panel({ title, hint, children }) {
  return (
    <section className="panel">
      <h2 className="panel-title">
        {title}
        {hint ? <span className="hint">{hint}</span> : null}
      </h2>
      {children}
    </section>
  );
}
