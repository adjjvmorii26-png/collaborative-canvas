import experiments from "../data/experiments.json";
import catalog from "../data/catalog.json";
import reports from "../data/reports.json";
import { Badge, Panel, Stat } from "./ui.jsx";

const PHASE_COLORS = { 1: "blue", 2: "", 3: "" };
const STATUS = {
  done: { label: "DONE", tone: "done", pct: 100 },
  in_progress: { label: "WIP", tone: "wip", pct: 55 },
  todo: { label: "TODO", tone: "todo", pct: 0 },
};

export default function OverviewTab() {
  const done = experiments.filter((e) => e.status === "done").length;
  const wip = experiments.filter((e) => e.status === "in_progress").length;
  const totalSteps = catalog.reduce((s, r) => s + r.step_count, 0);

  return (
    <>
      <div className="stats">
        <Stat k="Experiments" v={experiments.length} />
        <Stat k="Completed" v={done} hint={`/ ${experiments.length}`} />
        <Stat k="Recipes" v={catalog.length} hint="catalog" />
        <Stat k="Reports" v={reports.length} hint="sample" />
      </div>
      <Panel title="Experiment backlog" hint="docs/experiments.md · phase 1 → 3">
        <div className="experiments">
          {experiments.map((e) => {
            const st = STATUS[e.status];
            return (
              <div className="exp" key={e.id}>
                <div className="id">{e.id}</div>
                <div>
                  <div className="name">{e.name}</div>
                  <div className="note">{e.note}</div>
                  <div className="progress" title={`${st.pct}%`}>
                    <i style={{ width: `${st.pct}%` }} />
                  </div>
                </div>
                <div style={{ textAlign: "right" }}>
                  <Badge tone={st.tone}>{st.label}</Badge>
                  <div className="phase" style={{ marginTop: 6 }}>PHASE {e.phase}</div>
                </div>
              </div>
            );
          })}
        </div>
      </Panel>
    </>
  );
}
