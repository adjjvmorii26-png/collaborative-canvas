// Mirror of ixpansion/core/router.py (X-04): keyword-tag scoring, no LLM.

export function tokens(text) {
  return new Set((text.toLowerCase().match(/[a-z0-9]+/g) || []));
}

export function score(recipe, tokenSet) {
  const haystack = recipe.tags.join(" ").toLowerCase();
  let total = 0;
  for (const t of tokenSet) {
    if (haystack.includes(t)) total += 1;
  }
  return total;
}

export function route(inputText, catalog) {
  const tokenSet = tokens(inputText);
  const scores = Object.fromEntries(catalog.map((r) => [r.name, score(r, tokenSet)]));
  let best = catalog[0];
  for (const r of catalog) {
    if (scores[r.name] > scores[best.name]) best = r;
  }
  const ranked = catalog.map((r) => [r.name, scores[r.name]]).sort((a, b) => b[1] - a[1]);
  const label = ranked.slice(0, 3).map(([name, s]) => `${name}=${s}`).join(" | ");
  return { recipe: best, scores, label };
}
