"use client";

import { PipelineFigure } from "./Figures";
import { parsePrimary } from "./lib";
import { Caption, Mono, ratePct } from "./ui";
import type { OverviewDoc } from "./types";

type E3Compare = { primary: string; interim: boolean; interim_text: string } | null;
type Loc = { variants: Record<string, { mode: string; k: number; n: number; cell: string }[]> } | null;

function PrExample({ o }: { o: OverviewDoc }) {
  const p = o.pr1;
  if (!p) return <p className="ui text-[14px] text-muted">The recorded PR comment is not exported in this build. Run <Mono>make demo-data</Mono>.</p>;
  const passed = p.tests_total;
  return (
    <figure className="my-0">
      <div className="ui border border-rule bg-panel p-4 text-[14px]">
        <p className="m-0 font-medium">
          itsdangerous pull request 1: <span className="text-fail">{p.failing_count} of {p.tests_total} tests failed</span>
        </p>
        <ul className="m-0 mt-2 list-none p-0">
          {p.failing.map((f) => (
            <li key={f.test_id} className="py-0.5">
              <Mono className="text-[12.5px]">{f.test_id.replace("tests/test_itsdangerous/", "")}</Mono>
              <span className="ml-2 text-fail">failed</span>
            </li>
          ))}
        </ul>
        <p className="mb-1 mt-3 text-muted">The failures trace to one line:</p>
        <p className="m-0"><Mono>{p.file}:{p.line}</Mono></p>
        <p className="mb-1 mt-3 text-muted">One-line patch that the bot proposed:</p>
        <pre className="m-0 overflow-x-auto border border-rule bg-panel p-2 text-[13px] leading-snug">
          {p.old !== null && <span className="block text-fail">{`- ${p.old.trim()}`}</span>}
          <span className="block text-pass">{`+ ${p.new.trim()}`}</span>
        </pre>
        <p className="mb-0 mt-3">
          <span className="font-medium text-pass">{passed} tests passed with the fix.</span>{" "}
          <a href={o.live_pr_url}>Open the live pull request</a>.
        </p>
      </div>
      <Caption kind="Figure">
        The comment BlastRadius posted on pull request 1 of a fork of pallets/itsdangerous, where one comparison was flipped on purpose.
        The patch is shown only because the full suite passed with it. Source: <Mono>{p.source}</Mono>.
      </Caption>
    </figure>
  );
}

/** Three findings, each one sentence with its number and a link to its Results subsection. */
function Findings({ o, e3, loc }: { o: OverviewDoc; e3: E3Compare; loc: Loc }) {
  const co = o.headline.methods.find((m) => m.method === "co-change, all partner files");
  const hist = o.headline.methods.find((m) => m.method === "historical-frequency baseline");
  const pr = e3 ? parsePrimary(e3.primary) : null;
  const std = loc?.variants.standard ?? [];
  const l3 = std.find((x) => x.mode.startsWith("L3"));
  const l4 = std.find((x) => x.mode.startsWith("L4"));
  return (
    <ol className="prose-col my-4 list-decimal pl-6">
      <li className="mb-2">
        {co && hist ? (
          <>Of the tests that failed, past failure history named {ratePct(hist.micro_recall)} in its top {o.headline.k} and co-change
            named {ratePct(co.micro_recall)} (micro recall, {hist.micro_recall.n.toLocaleString()} and {co.micro_recall.n.toLocaleString()} of {hist.micro_recall.d.toLocaleString()}). {" "}
            <a href="#rq1">Results, RQ1</a>.</>
        ) : "RQ1 numbers are not exported."}
      </li>
      <li className="mb-2">
        {pr ? (
          <>{pr.interim ? "In the interim sample" : "In the pre-registered test"} with {pr.model} on {pr.n} standard seeded tasks, the change-aware
            arm R2 produced a fix that passes the full suite for {pr.r2[0]} of {pr.r2[1]} tasks against {pr.r1[0]} of {pr.r1[1]} for the
            log-only arm R1 (exact one-sided McNemar p = {pr.p}; R2 only {pr.r2Only}, R1 only {pr.r1Only}). {" "}
            <a href="#e3">Results, E3</a>.</>
        ) : "The E3 primary test is not exported."}
      </li>
      <li className="mb-2">
        {l3 && l4 ? (
          <>Knowing which functions the change touched (L4) puts the seeded function in the top three retrieved chunks for {l4.cell}{" "}
            of the standard tasks; whole-repository hybrid retrieval (L3) does so for {l3.cell}. {" "}
            <a href="#retrieval">Results, retrieval</a>.</>
        ) : "Retrieval numbers are not exported."}
      </li>
    </ol>
  );
}

export default function OverviewSection({ o, e3, loc }: { o: OverviewDoc; e3: E3Compare; loc: Loc }) {
  return (
    <section id="overview" aria-labelledby="h-overview" className="scroll-mt-20">
      <h2 id="h-overview" className="m-0 mb-3 max-w-[720px]">BlastRadius: which tests does a pull request break, and can a model tell in advance?</h2>
      <div className="grid gap-8 lg:grid-cols-[minmax(0,1.15fr)_minmax(0,1fr)]">
        <PrExample o={o} />
        <div>
          <h3 className="mt-0">What it does</h3>
          <p className="mt-0">BlastRadius ranks the test files a pull request is likely to break, so a CI server can run the risky ones first.</p>
          <p>It labels each failure as the change&apos;s own, already failing on the base commit, or flaky.</p>
          <p>For failures that are the change&apos;s own, it proposes a patch and shows it only after the full test suite passes with it.</p>
        </div>
      </div>

      <h3>The problem</h3>
      <div className="prose-col">
        <p className="mt-0">
          CI servers run the whole suite and report every red test, whoever caused it. A developer then has to work out which failures
          the pull request introduced, which were already failing on the base commit, and which are flaky. BR-Bench records, per test
          and per pull request, what actually failed in GitHub Actions, so a predictor can be scored against what happened instead of
          against proxies such as coverage or mutation.
        </p>
      </div>

      <h3>Pipeline</h3>
      <PipelineFigure />

      <h3>Three findings</h3>
      <Findings o={o} e3={e3} loc={loc} />
    </section>
  );
}
