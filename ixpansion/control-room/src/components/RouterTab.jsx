import { useMemo, useState } from "react";
import { Wand2, Cpu } from "lucide-react";
import catalog from "../data/catalog.json";
import { route } from "../lib/router.js";
import { Badge, Panel } from "./ui.jsx";

const SEED = "release note for the new router api and cold start fix";

export default function RouterTab() {
  const [input, setInput] = useState(SEED);
  const result = useMemo(() => route(input, catalog), [input]);
  const max = Math.max(1, ...Object.values(result.scores));
  const ranked = catalog
    .map((r) => [r, result.scores[r.name]])
    .sort((a, b) => b[1] - a[1]);

  return (
    <div className="router-grid">
      <Panel title="Route an input" hint="X-04 · keyword-tag scoring">
        <textarea
          className="input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Describe what you want to produce, e.g. 'summarize this dataset'..."
        />
        <p style={{ color: "var(--text-faint)", fontSize: 12, margin: "10px 2px 0", lineHeight: 1.5 }}>
          Mirrors <b style={{ fontFamily: "var(--mono)" }}>core/router.py</b>: tokenizes the input and scores every
          recipe against its tag vocabulary. No LLM call — cheap first, correct later.
        </p>
      </Panel>

      <Panel title="Recommendation" hint="live">
        {input.trim() ? (
          <>
            <div className="reco">
              <div className="reco-name">{result.recipe.name}</div>
              <div className="reco-label">route: {result.label}</div>
              <div className="reco-steps">
                {result.recipe.steps.map((s, i) => (
                  <div key={s.name}>
                    <b>{i + 1}. {s.name}</b> — {s.prompt.slice(0, 90)}
                  </div>
                ))}
              </div>
            </div>
            <div style={{ marginTop: 20 }}>
              {ranked.map(([r, s]) => (
                <div className={`score-row ${r.name === result.recipe.name ? "best" : ""}`} key={r.name}>
                  <div className="top">
                    <b>{r.name}</b>
                    <span>{s}</span>
                  </div>
                  <div className="score-bar">
                    <i style={{ width: `${(s / max) * 100}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </>
        ) : (
          <div className="empty">Enter some input text to see live routing.</div>
        )}
        <div style={{ display: "flex", gap: 10, marginTop: 18, color: "var(--text-faint)", fontSize: 12 }}>
          <span style={{ display: "inline-flex", alignItems: "center", gap: 6 }}><Wand2 size={14} /> deterministic</span>
          <span style={{ display: "inline-flex", alignItems: "center", gap: 6 }}><Cpu size={14} /> 0 tokens used</span>
          <Badge tone="done">router.py</Badge>
        </div>
      </Panel>
    </div>
  );
}
