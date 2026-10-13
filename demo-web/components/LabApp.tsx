"use client";

import { useEffect, useState } from "react";
import Evidence, { useBuiltFrom } from "./Demo";
import { GraphExplorer } from "./lab/Explorer";
import LabPage from "./lab/LabPage";
import { useDoc } from "./lib";
import TrySection from "./TrySection";
import type { PanelsDoc } from "./Panels";
import { Mono, short } from "./ui";
import UseIt from "./UseIt";

const TABS = [
  { id: "lab", label: "Live Lab" },
  { id: "graph", label: "Graph Explorer" },
  { id: "evidence", label: "Evidence" },
  { id: "use", label: "Use it" },
] as const;
type Tab = (typeof TABS)[number]["id"];
const REPO = "https://github.com/DeepanshuOP/blastradius";

function readHash(): Tab {
  const h = typeof window === "undefined" ? "" : window.location.hash.replace(/^#/, "").split("/")[0];
  return (TABS.find((t) => t.id === h)?.id ?? (["overview", "data", "results", "compare"].includes(h) ? "evidence" : ["try-it", "use-it"].includes(h) ? "use" : "lab")) as Tab;
}

function Theme() {
  const [theme, setTheme] = useState<"dark" | "light">("dark");
  useEffect(() => {
    try { if (localStorage.getItem("br-theme") === "light") setTheme("light"); } catch { /* storage blocked */ }
  }, []);
  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    try { localStorage.setItem("br-theme", theme); } catch { /* storage blocked */ }
  }, [theme]);
  return (
    <button type="button" onClick={() => setTheme(theme === "dark" ? "light" : "dark")} className="ui rounded border border-rule px-2 py-1 text-sm text-muted hover:text-ink" aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} theme`}>
      {theme === "dark" ? "Light" : "Dark"}
    </button>
  );
}

export default function LabApp() {
  const [tab, setTab] = useState<Tab>("lab");
  const panels = useDoc<PanelsDoc>("panels");
  const built = useBuiltFrom();
  useEffect(() => {
    setTab(readHash());
    const on = () => setTab(readHash());
    window.addEventListener("hashchange", on);
    return () => window.removeEventListener("hashchange", on);
  }, []);
  const go = (t: Tab) => { setTab(t); window.history.replaceState(null, "", `#${t}`); window.scrollTo({ top: 0 }); };
  return (
    <div className="min-h-screen">
      <a href="#main" className="ui sr-only focus:not-sr-only focus:absolute focus:left-2 focus:top-2 focus:bg-panel focus:p-2">Skip to content</a>
      <header className="sticky top-0 z-30 border-b border-rule bg-page/95 backdrop-blur-0">
        <div className="mx-auto flex max-w-[1760px] flex-wrap items-center gap-x-6 gap-y-1 px-3 py-2">
          <span className="ui text-md font-semibold tracking-tight"><span className="text-accent">●</span> BlastRadius</span>
          <nav aria-label="Primary" className="flex flex-wrap gap-1">
            {TABS.map((t) => (
              <button key={t.id} type="button" onClick={() => go(t.id)} aria-current={tab === t.id ? "page" : undefined}
                className={`ui rounded px-3 py-1 text-base ${tab === t.id ? "bg-panel font-semibold text-ink ring-1 ring-rule" : "text-muted hover:text-ink"}`}>{t.label}</button>
            ))}
          </nav>
          <span className="ui ml-auto hidden text-xs text-muted md:inline">Execution-grounded change impact prediction for CI</span>
          <Theme />
        </div>
      </header>
      {tab === "lab" && <LabPage />}
      {tab === "graph" && <GraphExplorer />}
      {tab === "evidence" && <Evidence />}
      {tab === "use" && (
        <main id="main" className="mx-auto max-w-[1100px] space-y-12 px-4 py-8">
          <TrySection />
          <section id="use-it" aria-labelledby="h-use" className="scroll-mt-20">
            <h2 id="h-use" className="m-0 mb-3">Use it</h2>
            <div className="prose-col"><p className="mt-0">Three ways to run BlastRadius on your own repository: a GitHub Action, a Jenkins stage and a command line.</p></div>
            <UseIt />
          </section>
        </main>
      )}
      <footer className="ui mx-auto mt-10 max-w-[1760px] border-t border-rule px-3 pb-8 pt-5 text-sm text-muted">
        <p className="m-0">Team: Prisha Vadhavkar, Sanskriti Singh and Deepanshu. Guide: Dr. Yoga Raja C A.</p>
        <p className="mb-0 mt-2">
          {(panels.doc?.release.dois ?? []).map((d, i) => (
            <span key={d.doi}>{i > 0 ? "; " : ""}{d.what[0].toUpperCase() + d.what.slice(1)} DOI <a href={`https://doi.org/${d.doi}`}>{d.doi}</a></span>
          ))}
          {panels.doc ? ". " : ""}
          Repository <a href={REPO}>{REPO.replace("https://", "")}</a>. Licence: code MIT, data CC BY 4.0.
        </p>
        <p className="mb-0 mt-2">Built from commit <Mono>{built ? short(built) : "unknown"}</Mono>.</p>
      </footer>
    </div>
  );
}
