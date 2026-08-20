import catalog from "../data/catalog.json";
import { Badge, Panel } from "./ui.jsx";

export default function RecipesTab() {
  return (
    <Panel title="Recipe catalog" hint={`${catalog.length} recipes · content_output/recipes`}>
      <div className="recipe-grid">
        {catalog.map((r) => (
          <article className="recipe-card" key={r.name}>
            <div>
              <div className="r-name">{r.name}</div>
              <div className="tags" style={{ marginTop: 8 }}>
                {r.tags.map((t) => (
                  <Badge key={t}>{t}</Badge>
                ))}
              </div>
            </div>
            <p className="r-desc">{r.description || "No description yet."}</p>
            <div className="step-list">
              {r.steps.map((s, i) => (
                <div className="step" key={s.name}>
                  <b>STEP {i + 1} · {s.name.toUpperCase()}</b>
                  <span title={s.prompt}>{s.prompt}</span>
                </div>
              ))}
            </div>
          </article>
        ))}
      </div>
    </Panel>
  );
}
