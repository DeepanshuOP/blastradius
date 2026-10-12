"use client";

import Agents from "./Agents";
import Analyze from "./Analyze";
import Ask from "./Ask";
import LiveRun from "./LiveRun";
import { useDoc } from "./lib";
import type { IndexDoc } from "./types";
import { Mono } from "./ui";

function Block({ id, title, does, children }: { id: string; title: string; does: React.ReactNode; children: React.ReactNode }) {
  return (
    <section id={id} aria-labelledby={`h-${id}`} className="scroll-mt-20 border-t border-rule pt-2">
      <h3 id={`h-${id}`}>{title}</h3>
      <p className="prose-col mt-0">{does}</p>
      {children}
    </section>
  );
}

export default function TrySection() {
  const { doc: index, error } = useDoc<IndexDoc>("index");
  return (
    <section id="try-it" aria-labelledby="h-try" className="scroll-mt-20">
      <h2 id="h-try" className="m-0 mb-3">Try it</h2>
      <div className="prose-col">
        <p className="mt-0">
          Four things to run. The static build replays recordings; <Mono>make demo-web</Mono> on a local checkout enables live analysis and,
          with a key and the network, live questions.
        </p>
      </div>
      <Block id="try-analyze" title="Analyze a repository"
        does={<>Clones a public Python or Java repository, builds its code graph and ranks the files and tests a user story touches. Input: a GitHub URL and a one-sentence story; no language model and no token are used. Needs the local server.</>}>
        <Analyze />
      </Block>
      <Block id="try-ask" title="Ask"
        does={<>Answers a question about a repository from retrieved code, failure history and documents, with citations. Input: a repository and a question; it runs live when a key and the network are present, and otherwise shows the recorded answers.</>}>
        <Ask />
      </Block>
      <Block id="try-agents" title="Agent scenarios"
        does={<>Replays four recorded runs of the seven-agent workflow, from a user story to a deployed change or a blocked one. Input: choose a scenario; nothing is executed.</>}>
        <Agents />
      </Block>
      <Block id="try-run" title="Live-run replay"
        does={<>Walks one real pull-request failure through the pipeline stage by stage, from the raw CI log to the predictors scored against what failed. Input: choose an instance; nothing is executed.</>}>
        {error && <p className="text-fail">Could not load /data/index.json ({error}). Run <Mono>make demo-data</Mono>.</p>}
        {index ? <LiveRun index={index} /> : !error && <p className="text-muted">Loading.</p>}
      </Block>
    </section>
  );
}
