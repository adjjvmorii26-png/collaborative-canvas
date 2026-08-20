import express from "express";
import Stripe from "stripe";
import { randomUUID } from "node:crypto";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const DATA_FILE = join(__dirname, "data", "funding.json");
const PORT = process.env.PORT || 8787;
const APP_URL = process.env.APP_URL || "http://127.0.0.1:5173";

const stripeKey = process.env.STRIPE_SECRET_KEY || "";
const stripe = stripeKey ? new Stripe(stripeKey) : null;
const mode = stripe ? "live" : "demo";

/* ── Tiers (USD pricing) ─────────────────────────────────────────────── */

const TIERS = [
  {
    id: "ration",
    name: "API Key Ration",
    goal: "api-keys",
    amount: 25,
    per: "Refills the LLM key budget — roughly 1000 more experiment pulses.",
    accent: "#22d3a8",
  },
  {
    id: "compute",
    name: "Compute Boost",
    goal: "specs",
    amount: 100,
    per: "Funds a bigger GPU + RAM tier so heavy recipes run faster.",
    accent: "#60a5fa",
  },
  {
    id: "patron",
    name: "Patron Pulse",
    goal: "both",
    amount: 250,
    per: "Split evenly across API keys and specs, plus priority experiments.",
    accent: "#a78bfa",
  },
];

/* ── Goals ───────────────────────────────────────────────────────────── */

const GOALS = [
  { id: "api-keys", label: "More API keys", target: 100 },
  { id: "specs", label: "Better specs", target: 500 },
];

/* ── Crypto wallets ──────────────────────────────────────────────────── */

const WALLETS = [
  {
    chain: "ethereum",
    label: "ETH (Mainnet)",
    address: "0x1XpAn…DEMO",
    tier_pricing: { ration: 0.007, compute: 0.028, patron: 0.07 },
  },
  {
    chain: "base",
    label: "ETH (Base L2)",
    address: "0xB4s3…DEMO",
    tier_pricing: { ration: 0.007, compute: 0.028, patron: 0.07 },
  },
  {
    chain: "ethereum",
    label: "USDC (ERC-20)",
    address: "0xUsDc…DEMO",
    tier_pricing: { ration: 25, compute: 100, patron: 250 },
  },
];

/* ── NFT Collection ──────────────────────────────────────────────────── */

const NFT_PASSES = [
  { id: "pulse-01", name: "Virtual Pulse", rarity: "common", price: 25, goal: "api-keys", art: "/nft/pulse-01.svg" },
  { id: "pulse-02", name: "Symbiont Node", rarity: "common", price: 25, goal: "api-keys", art: "/nft/pulse-02.svg" },
  { id: "pulse-03", name: "Synapse Weaver", rarity: "uncommon", price: 50, goal: "specs", art: "/nft/pulse-03.svg" },
  { id: "pulse-04", name: "Membrane Rider", rarity: "uncommon", price: 50, goal: "specs", art: "/nft/pulse-04.svg" },
  { id: "pulse-05", name: "Organism Core", rarity: "rare", price: 100, goal: "both", art: "/nft/pulse-05.svg" },
  { id: "pulse-06", name: "Genesis Pulse", rarity: "mythic", price: 250, goal: "both", art: "/nft/pulse-06.svg" },
];

/* ── Helpers ─────────────────────────────────────────────────────────── */

function defaultState() {
  return { goals: GOALS, contributions: [] };
}

function loadState() {
  try {
    return JSON.parse(readFileSync(DATA_FILE, "utf8"));
  } catch {
    return defaultState();
  }
}

function saveState(state) {
  mkdirSync(dirname(DATA_FILE), { recursive: true });
  writeFileSync(DATA_FILE, JSON.stringify(state, null, 2));
}

function splitAmount(goal, amount) {
  if (goal === "both") return { "api-keys": amount / 2, specs: amount / 2 };
  return { [goal]: amount };
}

function totals(state) {
  const raised = { "api-keys": 0, specs: 0 };
  for (const c of state.contributions) {
    const parts = splitAmount(c.goal, c.amount);
    raised["api-keys"] += parts["api-keys"] || 0;
    raised.specs += parts.specs || 0;
  }
  return state.goals.map((g) => ({
    ...g,
    raised: Math.round(raised[g.id] * 100) / 100,
  }));
}

function railsSummary(state) {
  const out = { stripe: 0, crypto: 0, nft: 0 };
  for (const c of state.contributions) {
    if (c.method in out) out[c.method] += c.amount;
    else out.stripe += c.amount; // legacy contributions without method
  }
  return out;
}

function findTier(id) {
  return TIERS.find((t) => t.id === id);
}

function findPass(id) {
  return NFT_PASSES.find((p) => p.id === id);
}

/* ── Express ─────────────────────────────────────────────────────────── */

const app = express();
app.use(express.json());

/* GET /api/fund — full state */
app.get("/api/fund", (_req, res) => {
  const state = loadState();
  res.json({
    mode,
    tiers: TIERS,
    goals: totals(state),
    rails: railsSummary(state),
    count: state.contributions.length,
    wallets: WALLETS,
    nft: NFT_PASSES.map((p) => ({
      ...p,
      minted: state.contributions.filter(
        (c) => c.method === "nft" && c.pass_id === p.id
      ).length,
    })),
  });
});

/* POST /api/fund/checkout — Stripe */
app.post("/api/fund/checkout", async (req, res) => {
  const tier = findTier(req.body.tier);
  if (!tier) return res.status(400).json({ error: "unknown tier" });

  if (!stripe) {
    return res.json({ url: `${APP_URL}/?paid=demo&tier=${tier.id}` });
  }

  const session = await stripe.checkout.sessions.create({
    mode: "payment",
    line_items: [
      {
        price_data: {
          currency: "usd",
          product_data: { name: `IXPANSION — ${tier.name}` },
          unit_amount: tier.amount * 100,
        },
        quantity: 1,
      },
    ],
    metadata: { tier: tier.id, goal: tier.goal },
    success_url: `${APP_URL}/?paid=stripe&session_id={CHECKOUT_SESSION_ID}`,
    cancel_url: `${APP_URL}/?fund=cancelled`,
  });
  res.json({ url: session.url });
});

/* POST /api/fund/nft/mint — record an NFT mint */
app.post("/api/fund/nft/mint", (req, res) => {
  const pass = findPass(req.body.pass_id);
  if (!pass) return res.status(400).json({ error: "unknown pass" });

  const state = loadState();
  const passMints = state.contributions.filter(
    (c) => c.method === "nft" && c.pass_id === pass.id
  );
  const tokenId = passMints.length + 1;

  const contribution = {
    id: randomUUID(),
    method: "nft",
    pass_id: pass.id,
    pass_name: pass.name,
    rarity: pass.rarity,
    goal: pass.goal,
    amount: pass.price,
    ts: new Date().toISOString(),
    demo: mode === "demo",
    token_id: tokenId,
    note: `NFT mint ${pass.name} #${tokenId}`,
  };
  state.contributions.push(contribution);
  saveState(state);
  res.json({ goals: totals(state), rails: railsSummary(state), contribution });
});

/* POST /api/fund/record — general (Stripe / crypto / demo) */
app.post("/api/fund/record", async (req, res) => {
  const state = loadState();
  const { session_id: sessionId, tier: tierId, demo, method, tx_hash } = req.body;
  let tier;
  let amount;
  let goal;
  let note;
  let recMethod = "stripe";

  if (sessionId) {
    if (!stripe) return res.status(400).json({ error: "stripe not configured" });
    if (state.contributions.some((c) => c.session_id === sessionId)) {
      return res.json({
        goals: totals(state),
        rails: railsSummary(state),
        contribution: state.contributions.find((c) => c.session_id === sessionId),
      });
    }
    const session = await stripe.checkout.sessions.retrieve(sessionId);
    if (session.payment_status !== "paid") {
      return res.status(400).json({ error: "session not paid" });
    }
    tier = findTier(session.metadata.tier);
    amount = session.amount_total / 100;
    goal = session.metadata.goal;
    note = `Stripe session ${sessionId}`;
  } else if (method === "crypto" && tierId) {
    tier = findTier(tierId);
    if (!tier) return res.status(400).json({ error: "unknown tier" });
    amount = tier.amount;
    goal = tier.goal;
    recMethod = "crypto";
    note = `Crypto transfer ${tx_hash || "demo"}`;
  } else if (demo && tierId) {
    tier = findTier(tierId);
    if (!tier) return res.status(400).json({ error: "unknown tier" });
    amount = tier.amount;
    goal = tier.goal;
    recMethod = "stripe";
    note = "demo contribution";
  } else {
    return res.status(400).json({ error: "missing session_id, crypto tier, or demo tier" });
  }

  const contribution = {
    id: randomUUID(),
    method: recMethod,
    tier: tier.id,
    goal,
    amount,
    ts: new Date().toISOString(),
    demo: Boolean(demo) || !sessionId,
    session_id: sessionId || null,
    tx_hash: tx_hash || null,
    note,
  };
  state.contributions.push(contribution);
  saveState(state);
  res.json({ goals: totals(state), rails: railsSummary(state), contribution });
});

app.listen(PORT, () => {
  console.log(`[fund] mode=${mode} listening on http://127.0.0.1:${PORT}`);
  if (!stripe) console.log("[fund] no STRIPE_SECRET_KEY — running in demo mode");
});
