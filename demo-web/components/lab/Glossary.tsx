"use client";

import { useId, useState, type ReactNode } from "react";
import { BTN, Drawer } from "./common";

/** One plain sentence per term. The same text feeds the dotted-underline tooltips and the "?" drawer. */
export const GLOSSARY = {
  test: "A test function is one test node in the graph; pytest parametrisation can expand it into several test cases, which is what a run counts.",
  "blast radius": "The code and tests a change can reach through calls and imports in the code graph.",
  "co-change": "Two files that were edited together in past commits, often used as a sign that they are related.",
  binding: "Matching a failing test's name to the test source file that defines it, at a pinned commit.",
  "base commit": "The commit a change starts from; its test results show what was already broken.",
  triage: "Sorting each failing test into mine (this change broke it), inherited or flaky.",
  inherited: "A failure that was already there on the base commit, before this change.",
  flaky: "A test that both passes and fails on the same commit, so its failure says nothing about the change.",
  "selection rate": "The share of the candidate tests that you choose to run.",
  "Recall@10": "The share of a change's failing test files that appear among the ten files ranked first.",
  APFD: "Average percentage of faults detected: how early a test order reaches the failures, from 0 to 1.",
  LambdaRank: "A learning-to-rank objective that trains the model to push the failing tests to the top of the list.",
} as const;
export type TermKey = keyof typeof GLOSSARY;

/** A term with a dotted underline; hovering or focusing it shows its one-sentence definition. */
export function Term({ k, children }: { k: TermKey; children?: ReactNode }) {
  const [open, setOpen] = useState(false);
  const id = useId();
  return (
    <span className="relative inline-block">
      <span tabIndex={0} role="term" aria-describedby={id} className="br-term" onMouseEnter={() => setOpen(true)} onMouseLeave={() => setOpen(false)}
        onFocus={() => setOpen(true)} onBlur={() => setOpen(false)}>{children ?? k}</span>
      <span id={id} role="tooltip" className={`br-term-tip ui ${open ? "" : "sr-only"}`}>{GLOSSARY[k]}</span>
    </span>
  );
}

/** The "?" button of the top bar and the drawer that lists every term. */
export function GlossaryButton() {
  const [open, setOpen] = useState(false);
  return (
    <>
      <button type="button" onClick={() => setOpen(true)} className={`${BTN} font-semibold`} aria-haspopup="dialog" aria-label="Glossary" title="Glossary">?</button>
      {open && (
        <Drawer side="right" title="Glossary" onClose={() => setOpen(false)}>
          <dl className="ui m-0 min-h-0 flex-1 space-y-3 overflow-y-auto p-4">
            {(Object.keys(GLOSSARY) as TermKey[]).map((k) => (
              <div key={k}>
                <dt className="text-md font-semibold text-ink">{k}</dt>
                <dd className="m-0 mt-0.5 text-base text-muted">{GLOSSARY[k]}</dd>
              </div>
            ))}
          </dl>
        </Drawer>
      )}
    </>
  );
}
