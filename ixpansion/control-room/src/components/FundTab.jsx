import { useCallback, useEffect, useState } from "react";
import { ArrowUpRight, CheckCircle2, Coins, CreditCard, GalleryHorizontalEnd, ShieldCheck, Wallet } from "lucide-react";
import { Badge, Panel } from "./ui.jsx";

const money = (n) => `$${Number(n).toFixed(2)}`;

const RAILS = [
  { id: "usd", label: "USD", icon: CreditCard },
  { id: "crypto", label: "Crypto", icon: Coins },
  { id: "nft", label: "NFT Passes", icon: GalleryHorizontalEnd },
];

export default function FundTab() {
  const [state, setState] = useState(null);
  const [rail, setRail] = useState("usd");
  const [busy, setBusy] = useState(null);
  const [notice, setNotice] = useState("");
  const [recent, setRecent] = useState(null);

  const refresh = useCallback(async () => {
    const res = await fetch("/api/fund");
    setState(await res.json());
  }, []);

  useEffect(() => {
    refresh();
    const q = new URLSearchParams(window.location.search);
    if (!q.get("paid")) return;
    const body =
      q.get("paid") === "demo"
        ? { demo: true, tier: q.get("tier") }
        : { session_id: q.get("session_id") };
    fetch("/api/fund/record", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    })
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`record failed (${r.status})`))))
      .then((data) => {
        setNotice(`Payment recorded: ${money(data.contribution.amount)} → ${data.contribution.goal} goal.`);
        window.history.replaceState({}, "", "/");
        return refresh();
      })
      .catch((err) => setNotice(`Could not record payment: ${err.message}`));
  }, [refresh]);

  if (!state) return <div className="muted">Loading funding state…</div>;

  async function checkoutStripe(tier) {
    setBusy(`stripe-${tier.id}`);
    try {
      const res = await fetch("/api/fund/checkout", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tier: tier.id }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "checkout failed");
      window.location.assign(data.url);
    } catch (err) {
      setNotice(`Checkout failed: ${err.message}`);
      setBusy(null);
    }
  }

  async function recordCrypto(tier) {
    setBusy(`crypto-${tier.id}`);
    try {
      const fakeTx = "0x" + Array.from({ length: 16 }, () => "0123456789abcdef"[Math.floor(Math.random() * 16)]).join("");
      const res = await fetch("/api/fund/record", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ method: "crypto", tier: tier.id, tx_hash: fakeTx }),
      });
      const data = await res.json();
      setRecent(data.contribution);
      setNotice(`Crypto recorded: ${money(data.contribution.amount)} tx ${fakeTx.slice(0, 12)}…`);
      await refresh();
    } catch (err) {
      setNotice(`Crypto record failed: ${err.message}`);
    } finally {
      setBusy(null);
    }
  }

  async function mintPass(pass) {
    setBusy(`nft-${pass.id}`);
    try {
      const res = await fetch("/api/fund/nft/mint", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pass_id: pass.id }),
      });
      const data = await res.json();
      setRecent(data.contribution);
      setNotice(`Minted ${pass.name} #${data.contribution.token_id} — ${money(pass.price)} to ${pass.goal} goal.`);
      await refresh();
    } catch (err) {
      setNotice(`Mint failed: ${err.message}`);
    } finally {
      setBusy(null);
    }
  }

  const totalRaised = state.goals.reduce((s, g) => s + g.raised, 0);
  const totalTarget = state.goals.reduce((s, g) => s + g.target, 0);

  return (
    <>
      {notice && (
        <div className="fund-notice" role="status">
          <CheckCircle2 size={16} />
          {notice}
          <button className="fund-notice-x" onClick={() => setNotice("")}>×</button>
        </div>
      )}

      <div className="stats">
        <div className="stat">
          <div className="k">War chest</div>
          <div className="v">
            {money(totalRaised)}
            <em>/ {money(totalTarget)}</em>
          </div>
        </div>
        <div className="stat">
          <div className="k">Contributions</div>
          <div className="v">{state.count}</div>
        </div>
        <div className="stat">
          <div className="k">Mode</div>
          <div className="v">{state.mode === "live" ? "STRIPE" : "DEMO"}</div>
        </div>
      </div>

      <div className="fund-layout">
        <Panel title="Funding goals" hint="cashflow → capability">
          <div className="fund-goals">
            {state.goals.map((g) => {
              const pct = Math.min(100, (g.raised / g.target) * 100);
              return (
                <div className="fund-goal" key={g.id}>
                  <div className="fund-goal-top">
                    <b>{g.label}</b>
                    <span>{money(g.raised)} / {money(g.target)}</span>
                  </div>
                  <div className="progress fund-progress">
                    <i style={{ width: `${pct}%` }} />
                  </div>
                  <div className="fund-goal-meta">
                    <span>{pct >= 100 ? "target hit — scaling" : `${Math.round(pct)}% funded`}</span>
                    <Badge tone={pct >= 100 ? "done" : "wip"}>{pct >= 100 ? "LIVE" : "RAISING"}</Badge>
                  </div>
                </div>
              );
            })}
          </div>

          <div className="fund-rails-row">
            <div className="rail-chip" style={{ "--c": "var(--accent)" }}>USD {money(state.rails?.stripe || 0)}</div>
            <div className="rail-chip" style={{ "--c": "var(--accent-2)" }}>Crypto {money(state.rails?.crypto || 0)}</div>
            <div className="rail-chip" style={{ "--c": "var(--purple)" }}>NFT {money(state.rails?.nft || 0)}</div>
          </div>
        </Panel>

        <div className="fund-right">
          <div className="rail-switcher" role="tablist">
            {RAILS.map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                role="tab"
                aria-selected={rail === id}
                className={`tab rail-tab ${rail === id ? "active" : ""}`}
                onClick={() => setRail(id)}
              >
                <Icon size={14} />
                {label}
              </button>
            ))}
          </div>

          {rail === "usd" && (
            <Panel title="Fund with USD" hint="Stripe Checkout">
              <div className="fund-note">
                <Wallet size={15} />
                <span>Stripe-hosted Checkout — we never touch card data. PCI handled by Stripe.</span>
              </div>
              <div className="tier-grid">
                {state.tiers.map((tier) => (
                  <div className="tier" key={tier.id} style={{ "--tier": tier.accent }}>
                    <div className="tier-name">{tier.name}</div>
                    <div className="tier-amount">{money(tier.amount)}</div>
                    <div className="tier-per">{tier.per}</div>
                    <button className="tier-cta" disabled={busy === `stripe-${tier.id}`} onClick={() => checkoutStripe(tier)}>
                      {busy === `stripe-${tier.id}` ? "Opening…" : "Fund"}
                      {busy !== `stripe-${tier.id}` && <ArrowUpRight size={14} />}
                    </button>
                  </div>
                ))}
              </div>
              <div className="fund-secure"><ShieldCheck size={14} /> Checkout Sessions API · test mode safe to click</div>
            </Panel>
          )}

          {rail === "crypto" && (
            <Panel title="Fund with Crypto" hint="ETH + USDC">
              <div className="fund-note">
                <Coins size={15} />
                <span>Send to any wallet below. In demo mode, "simulate transfer" records the contribution.</span>
              </div>
              <div className="wallet-list">
                {state.wallets.map((w, i) => (
                  <div className="wallet-row" key={i}>
                    <Badge tone="blue">{w.chain}</Badge>
                    <span className="wallet-label">{w.label}</span>
                    <code className="wallet-addr">{w.address}</code>
                  </div>
                ))}
              </div>
              <div className="tier-grid" style={{ marginTop: 14 }}>
                {state.tiers.map((tier) => (
                  <div className="tier" key={tier.id} style={{ "--tier": tier.accent }}>
                    <div className="tier-name">{tier.name}</div>
                    <div className="tier-amount">{money(tier.amount)}</div>
                    <div className="tier-per">ETH equivalent shown in wallet list</div>
                    <button className="tier-cta" disabled={busy === `crypto-${tier.id}`} onClick={() => recordCrypto(tier)}>
                      {busy === `crypto-${tier.id}` ? "Recording…" : "Simulate Transfer"}
                      {busy !== `crypto-${tier.id}` && <Coins size={14} />}
                    </button>
                  </div>
                ))}
              </div>
              <div className="fund-secure"><ShieldCheck size={14} /> Real mode: verify on-chain tx hash before crediting</div>
            </Panel>
          )}

          {rail === "nft" && (
            <Panel title="NFT Collector Passes" hint="on-chain art → funding">
              <div className="fund-note">
                <GalleryHorizontalEnd size={15} />
                <span>Each pass is generative organism art. Minting records a contribution to the war chest.</span>
              </div>
              <div className="nft-grid">
                {state.nft.map((pass) => (
                  <div className={`nft-card rarity-${pass.rarity}`} key={pass.id}>
                    <img src={pass.art} alt={pass.name} className="nft-img" />
                    <div className="nft-info">
                      <div className="nft-name">{pass.name}</div>
                      <div className="nft-meta">
                        <Badge tone={pass.rarity === "mythic" ? "done" : pass.rarity === "rare" ? "wip" : "blue"}>{pass.rarity}</Badge>
                        <span className="nft-price">{money(pass.price)}</span>
                        <span className="nft-minted">{pass.minted} minted</span>
                      </div>
                      <button className="tier-cta" disabled={busy === `nft-${pass.id}`} onClick={() => mintPass(pass)}>
                        {busy === `nft-${pass.id}` ? "Minting…" : "Mint Pass"}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
              {recent && recent.method === "nft" && (
                <div className="fund-notice" style={{ marginTop: 14 }}>
                  <CheckCircle2 size={14} />
                  Last mint: {recent.pass_name} #{recent.token_id} — token {recent.id.slice(0, 8)}
                </div>
              )}
              <div className="fund-secure"><ShieldCheck size={14} /> Demo mints are recorded locally · real mints would call a contract</div>
            </Panel>
          )}
        </div>
      </div>
    </>
  );
}
