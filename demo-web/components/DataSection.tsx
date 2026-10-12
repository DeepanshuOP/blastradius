"use client";

import { BarFigure } from "./Figures";
import { Decisions, type PanelsDoc } from "./Panels";
import type { CorpusDoc, OverviewDoc, ResultsDoc } from "./types";
import { Mono, NumTable, TD, TH, ratePct } from "./ui";


const REPO = "https://github.com/DeepanshuOP/blastradius";

export default function DataSection({ c, o, r, panels }: { c: CorpusDoc; o: OverviewDoc; r: ResultsDoc; panels: PanelsDoc | null }) {
  const runs = c.runs_funnel.stages;
  const gate1p = r.gates.rows.find((g) => g.gate.includes("(D-44, primary)"));
  const gate1s = r.gates.rows.find((g) => g.gate.includes("(secondary)"));
  const bind = o.binding;
  const lang = c.strict_by_language.rows;
  const java = lang.find((x) => x.language === "Java");
  const py = lang.find((x) => x.language === "Python");
  return (
    <section id="data" aria-labelledby="h-data" className="scroll-mt-20">
      <h2 id="h-data" className="m-0 mb-3">Data: BR-Bench</h2>
      <div className="prose-col">
        <h3>Label definition</h3>
        <p className="mt-0">
          A test is <em>fault-revealing</em> for a pull request run when it fails at the head commit, did not fail in the run of the
          base commit, and is not flaky across sibling runs of the same head:
        </p>
        <pre className="ui overflow-x-auto border border-rule bg-panel p-3 text-[14px]">T_reveal = T_head_fail − T_base_fail − T_flaky</pre>
        <p>
          The exact rules, including how the strict and relaxed splits differ, are in{" "}
          <a href={`${REPO}/blob/main/docs/SCHEMAS.md`}>docs/SCHEMAS.md</a>.
        </p>
      </div>

      <h3>Attrition funnel</h3>
      <BarFigure
        log max={runs[0].count}
        bars={runs.map((s, i) => ({ label: s.stage, value: s.count, text: s.count.toLocaleString(), strong: i === runs.length - 1 }))}
        summary={`Runs funnel on a log scale: ${runs.map((s) => `${s.stage} ${s.count.toLocaleString()}`).join(", ")}.`}
        caption={<>From every discovered run to a benchmark instance with at least one strict label (log scale; each stage is a subset of the one above). Source: <Mono>{c.runs_funnel.source}</Mono>.</>}
      />

      <h3>Corpus</h3>
      <NumTable
        caption={<>BR-Bench by label strictness, and the strict set by language. The strict set is the one every experiment uses.</>}
        source={`${c.splits.source}`}>
        <table className="w-full min-w-[640px] border-collapse">
          <thead><tr><th className={TH}>subset</th><th className={`${TH} text-right`}>repositories</th><th className={`${TH} text-right`}>instances</th>
            <th className={`${TH} text-right`}>labels</th><th className={`${TH} text-right`}>distinct tests</th></tr></thead>
          <tbody>
            {c.splits.rows.map((x) => (
              <tr key={x.split}><td className={TD}>{x.split}</td><td className={`${TD} text-right`}>{x.repos}</td><td className={`${TD} text-right`}>{x.instances.text}</td>
                <td className={`${TD} text-right`}>{x.labels.text}</td><td className={`${TD} text-right`}>{x.distinct_tests.toLocaleString()}</td></tr>
            ))}
            {lang.map((x) => (
              <tr key={x.language}><td className={TD}>strict, {x.language}</td><td className={`${TD} text-right`}>{x.repos}</td><td className={`${TD} text-right`}>{x.instances.text}</td>
                <td className={`${TD} text-right`}>{x.labels.text}</td><td className={`${TD} text-right`}>{x.distinct_tests.toLocaleString()}</td></tr>
            ))}
          </tbody>
        </table>
      </NumTable>

      <h3>Release</h3>
      <div className="prose-col">
        <ul className="mt-0 list-disc pl-6">
          {(panels?.release.dois ?? []).map((d) => (
            <li key={d.doi}>{d.what[0].toUpperCase() + d.what.slice(1)} DOI: <a href={`https://doi.org/${d.doi}`}>{d.doi}</a></li>
          ))}
          <li>Licence: code MIT, data CC BY 4.0; the vendored graph builder keeps its own licence files.</li>
        </ul>
      </div>

      <h3>Known limits</h3>
      <ul className="prose-col mt-0 list-disc pl-6">
        <li>
          Gate 1 (corpus size) is not met: {gate1p ? `${gate1p.measured.text} strict labels` : "strict labels"} against the threshold of
          5,000{gate1s ? `, and ${gate1s.measured.text} strict instances against the same threshold` : ""}.
        </li>
        <li>
          Test-to-file binding is reported with both figures, always together: {ratePct(bind.combined)} combined ({bind.combined.n.toLocaleString()}/{bind.combined.d.toLocaleString()}) and{" "}
          {ratePct(bind.full_confidence)} at full confidence ({bind.full_confidence.n.toLocaleString()}/{bind.full_confidence.d.toLocaleString()}); the second is below the 70% threshold.
        </li>
        <li>
          Parser precision is measured on development sets only: the logs the parsers were built against. The independent held-out
          figure was not measured, so the 100% on those sets is a fit number.
        </li>
        <li>
          The corpus is mostly Java: {java ? `${java.repos} repositories and ${java.instances.text} strict instances` : "Java"}, against{" "}
          {py ? `${py.repos} Python repositories and ${py.instances.text}` : "Python"}. The chronological test split of E1 is Java only.
        </li>
      </ul>

      <details className="prose-col mt-4 border-t border-rule pt-2">
        <summary className="ui text-[15px] font-medium">Method notes</summary>
        <ul className="list-disc pl-6">
          <li><a href={`${REPO}/blob/main/docs/DECISIONS.md`}>docs/DECISIONS.md</a>: every design decision with its rationale and revisit trigger.</li>
          <li><a href={`${REPO}/blob/main/docs/SCHEMAS.md`}>docs/SCHEMAS.md</a>: the frozen table schemas and the canonical <Mono>test_id</Mono>.</li>
          <li><a href={`${REPO}/blob/main/docs/DATASHEET.md`}>docs/DATASHEET.md</a>: provenance, pseudonymisation and known biases of the release.</li>
        </ul>
        {panels && <div className="mt-4"><Decisions d={panels.decisions} /></div>}
      </details>
    </section>
  );
}
