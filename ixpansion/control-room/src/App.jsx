import { useState } from "react";
import { FlaskConical, LayoutDashboard, ListTree, Send, FolderOpen, Wallet } from "lucide-react";
import OverviewTab from "./components/OverviewTab.jsx";
import RecipesTab from "./components/RecipesTab.jsx";
import RouterTab from "./components/RouterTab.jsx";
import ReportsTab from "./components/ReportsTab.jsx";
import FundTab from "./components/FundTab.jsx";

const TABS = [
  { id: "overview", label: "Overview", icon: LayoutDashboard },
  { id: "recipes", label: "Recipes", icon: ListTree },
  { id: "router", label: "Router", icon: Send },
  { id: "reports", label: "Reports", icon: FolderOpen },
  { id: "fund", label: "Fund", icon: Wallet },
];

export default function App() {
  const [tab, setTab] = useState("overview");
  return (
    <div className="app">
      <header className="header">
        <div className="logo">
          <FlaskConical size={22} />
        </div>
        <div className="title-block">
          <h1>IXPANSION Control Room</h1>
          <p>Recipe experiment platform — organisms in sync, pulses live.</p>
        </div>
        <span className="pulse">SYNCED</span>
      </header>

      <nav className="tabs" role="tablist">
        {TABS.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            role="tab"
            aria-selected={tab === id}
            className={`tab ${tab === id ? "active" : ""}`}
            onClick={() => setTab(id)}
          >
            <Icon size={15} />
            {label}
          </button>
        ))}
      </nav>

      {tab === "overview" && <OverviewTab />}
      {tab === "recipes" && <RecipesTab />}
      {tab === "router" && <RouterTab />}
      {tab === "reports" && <ReportsTab />}
      {tab === "fund" && <FundTab />}

      <footer className="foot">
        <span>ixpansion/control-room · React + Vite + Stripe Checkout</span>
        <span>experiments X-01 → X-10 · funding feeds API keys + specs</span>
      </footer>
    </div>
  );
}
