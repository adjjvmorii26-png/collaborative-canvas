import reports from "../data/reports.json";
import { Badge, Panel } from "./ui.jsx";

export default function ReportsTab() {
  return (
    <Panel
      title="Report gallery"
      hint={`${reports.length} mock runs · content_output/reports/control-room-demo`}
    >
      <div className="report-grid">
        {reports.map((r) => (
          <article className="report-card recipe-card" key={r.path}>
            <div className="r-head">
              <Badge tone="done">{r.recipe}</Badge>
              <span style={{ color: "var(--text-faint)", fontSize: 11, fontFamily: "var(--mono)" }}>
                {r.steps} steps · {r.provider}
              </span>
            </div>
            <div className="r-input">{r.input}</div>
            <div className="r-body">{r.text}</div>
            <div className="r-meta">{r.path}</div>
          </article>
        ))}
      </div>
    </Panel>
  );
}
