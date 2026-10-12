"use client";

import { useEffect, useRef, useState } from "react";
import Compare from "./Compare";
import DataSection from "./DataSection";
import { useDoc } from "./lib";
import OverviewSection from "./OverviewSection";
import ResultsSection, { type CompareLite, type E1Doc, type E2Doc, type E3Doc, type RagDoc } from "./ResultsSection";
import { EvidenceStrip } from "./lab/EvidenceStrip";
import type { PanelsDoc } from "./Panels";
import type { CorpusDoc, OverviewDoc, ResultsDoc } from "./types";
import { Mono } from "./ui";

const SECTIONS: { id: string; label: string }[] = [
  { id: "overview", label: "Overview" },
  { id: "data", label: "Data" },
  { id: "results", label: "Results" },
  { id: "compare", label: "Compare" },
];

type E1File = { e1: E1Doc };
type E2File = { e2: E2Doc };
type E3File = { e3: E3Doc };

/** Fills "Figure n." and "Table n." in order of appearance, in the whole page, whenever content changes. */
function useCaptionNumbers(root: React.RefObject<HTMLElement>) {
  useEffect(() => {
    const el = root.current;
    if (!el) return;
    const number = () => {
      const counts: Record<string, number> = {};
      el.querySelectorAll<HTMLElement>("[data-cap]").forEach((cap) => {
        const kind = cap.dataset.cap ?? "";
        counts[kind] = (counts[kind] ?? 0) + 1;
        const slot = cap.querySelector<HTMLElement>(".cap-num");
        if (slot && slot.textContent !== String(counts[kind])) slot.textContent = String(counts[kind]);
      });
    };
    number();
    const mo = new MutationObserver(number);
    mo.observe(el, { childList: true, subtree: true });
    return () => mo.disconnect();
  }, [root]);
}

/** The id of the section nearest the top of the viewport, for the table of contents. */
function useActive(ids: string[]): string {
  const [active, setActive] = useState(ids[0]);
  useEffect(() => {
    const onScroll = () => {
      let cur = ids[0];
      for (const id of ids) {
        const el = document.getElementById(id);
        if (el && el.getBoundingClientRect().top <= 96) cur = id;
      }
      setActive(cur);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, [ids]);
  return active;
}

function Toc({ active, vertical }: { active: string; vertical: boolean }) {
  return (
    <ul className={`m-0 list-none p-0 ${vertical ? "flex flex-col gap-1" : "flex flex-col"}`}>
      {SECTIONS.map((s) => (
        <li key={s.id}>
          <a href={`#${s.id}`} aria-current={active === s.id ? "location" : undefined}
            className={`ui block py-1 pl-3 text-[15px] no-underline ${vertical ? "border-l-2" : ""} ${active === s.id ? "border-accent font-semibold text-ink" : "border-transparent text-muted hover:text-ink"}`}>
            {s.label}
          </a>
        </li>
      ))}
    </ul>
  );
}

/** The section heading while its data loads, so every anchor of the table of contents exists from the first paint. */
function Pending({ id, title }: { id: string; title: string }) {
  return (
    <section id={id} aria-labelledby={`h-${id}`} className="scroll-mt-20">
      <h2 id={`h-${id}`} className="m-0 mb-3">{title}</h2>
      <p className="text-muted">Loading.</p>
    </section>
  );
}

/** The Evidence tab: the paper's results, unchanged in content, under a strip of four key results. */
export default function Evidence() {
  const overview = useDoc<OverviewDoc>("overview");
  const corpus = useDoc<CorpusDoc>("corpus");
  const results = useDoc<ResultsDoc>("results");
  const panels = useDoc<PanelsDoc>("panels");
  const e1 = useDoc<E1File>("e1");
  const e2 = useDoc<E2File>("e2");
  const e3 = useDoc<E3File>("e3");
  const compare = useDoc<CompareLite & { generated_at_git_sha: string; e3: { primary: string; interim: boolean; interim_text: string } | null }>("compare");
  const rag = useDoc<RagDoc & { ask: NonNullable<RagDoc>["ask"] }>("rag");
  const main = useRef<HTMLElement>(null);
  const ids = SECTIONS.map((s) => s.id);
  const active = useActive(ids);
  useCaptionNumbers(main);
  const errors = [overview, corpus, results].map((d) => d.error).filter(Boolean);
  const o = overview.doc;

  return (
    <div className="mx-auto flex max-w-[1320px] gap-10 px-4 sm:px-6 lg:px-8">
      <aside className="hidden w-44 shrink-0 lg:block">
        <nav aria-label="Evidence sections" className="sticky top-20 pt-8">
          <p className="ui m-0 mb-3 text-[13px] font-semibold uppercase tracking-wide text-muted">Evidence</p>
          <Toc active={active} vertical />
          <p className="cap mt-6 pr-2">Execution-grounded change impact prediction for CI.</p>
        </nav>
      </aside>
      <main id="main" ref={main} className="min-w-0 flex-1 py-6">
        <div className="mb-8"><EvidenceStrip /></div>
        {errors.length > 0 && (
          <p className="ui border border-fail p-3 text-[15px] text-fail">Could not load /data: {String(errors[0])}. Run <Mono>make demo-data</Mono>.</p>
        )}
        <div className="space-y-16">
          {o ? <OverviewSection o={o} e3={compare.doc?.e3 ?? null} loc={compare.doc?.localization ?? null} /> : <Pending id="overview" title="Overview" />}
          {corpus.doc && o && results.doc ? <DataSection c={corpus.doc} o={o} r={results.doc} panels={panels.doc} /> : <Pending id="data" title="Data: BR-Bench" />}
          <ResultsSection r={results.doc} e1={e1.doc?.e1 ?? null} e2={e2.doc?.e2 ?? null} e3={e3.doc?.e3 ?? null} c={compare.doc} rag={rag.doc} panels={panels.doc} />
          <Compare />
        </div>
      </main>
    </div>
  );
}

/** The commit this build's data was generated from (footer). */
export function useBuiltFrom(): string | undefined {
  const overview = useDoc<OverviewDoc>("overview");
  const compare = useDoc<{ generated_at_git_sha: string }>("compare");
  return overview.doc?.built_from ?? compare.doc?.generated_at_git_sha;
}
