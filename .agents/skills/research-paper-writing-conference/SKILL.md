---
name: research-paper-writing-conference
description: Help develop and revise an ML, AI, systems, cybersecurity, or related research paper for a conference submission using the Research Paper Writing workflow, with story-first planning, claim-evidence alignment, reviewer-style self-review, human-authorship safeguards, originality/plagiarism safeguards, project-grounded evidence, and strict adherence to the user's conference template. Use when working on a research paper, conference paper, Abstract, Introduction, Related Work, Method, Experiments, Conclusion, figures, tables, citations, paper review, or final submission checks.
---

# Research Paper Writing — Conference / Human-Authored Mode

## Purpose

Use this skill to help turn the user's real project, experiments, and notes into a clear, defensible conference paper.

The backbone follows the original research-paper-writing workflow: clarify the story first, use section-specific guidance, keep one message per paragraph, reverse-outline after writing, align claims with evidence, and review the paper as a skeptical reviewer.

This version adds only the controls needed for this use case:

1. Human-authored submission mode.
2. Originality and plagiarism safeguards.
3. Project/evidence provenance.
4. Conference-template compliance.
5. A final submission gate.

## Non-Negotiable Rules

1. Do not invent experiments, metrics, datasets, citations, implementation details, or reviewer feedback.
2. Do not turn an unsupported observation into a factual claim.
3. Do not call a result SOTA, state-of-the-art, best, novel, significant, or first unless the available evidence supports that exact scope.
4. Keep the terminology and scientific meaning supplied by the author stable across the paper.
5. Prefer the user's project artifacts, experiment outputs, notes, and provided sources over generic assumptions.
6. Do not silently fill missing information. Mark it as missing and tell the author what evidence is needed.
7. Do not copy sentences or distinctive phrasing from papers, websites, theses, or templates. Use source material for understanding and evidence, not as a prose source.
8. Never fabricate or guess a bibliography entry. Every reference used in the manuscript must be traceable to a real source.
9. Do not manipulate wording to evade plagiarism or AI-detection systems. The goal is genuinely author-driven writing, not detector gaming.
10. Treat the user's conference template and venue instructions as the formatting source of truth when they are provided.

## Human-Authorship Mode

The user's stated requirement is that the submitted paper must be humane and contain no AI-written content.

Therefore, default to **Human-Authored Mode**:

- Help with story construction, outlines, experiment planning, evidence maps, reviewer questions, terminology consistency, factual checks, citation placement, and critique.
- When the user provides manuscript prose, allow editing for clarity, grammar, flow, and correctness while preserving the author's meaning and voice.
- Do not produce a fresh submission-ready paragraph or section from only a topic description in Human-Authored Mode.
- When asked to "write" a section from scratch, first produce the writing plan, claims to establish, evidence required, and paragraph roles. The author should then write the prose.
- If a sentence is supplied by the author and needs polishing, keep the edit close to the supplied wording and do not add new scientific claims.
- Clearly distinguish author-provided text from agent suggestions.

This process cannot guarantee how an external AI detector will classify text. Do not make such a guarantee.

## Core Workflow

### Phase 0 — Intake and source grounding

Before prose work:

1. Identify the exact paper topic, task, target venue, format/template, and current manuscript location.
2. Inspect the project repository and relevant artifacts before making technical claims.
3. Identify the available evidence: code, READMEs, experiment logs, result files, plots, tables, configs, datasets, baselines, and prior drafts.
4. Create a compact evidence inventory before drafting.
5. Mark every important fact as one of: `author-provided`, `experiment-derived`, `literature-derived`, or `inference`.
6. Never upgrade `inference` into measured fact without evidence.

Load: `references/project-evidence-and-provenance.md`

### Phase 1 — Decide the paper story

Before sentence-level writing:

1. What task/problem is being solved?
2. Why does the problem matter?
3. What is the unresolved technical challenge?
4. Why do existing approaches fail on that challenge?
5. What is the paper's actual contribution?
6. Why does the proposed idea address the challenge?
7. What evidence demonstrates the contribution?
8. What is the honest scope and limitation?

Then create a mini-outline from task -> challenge -> solution -> evidence -> takeaway.

### Phase 2 — Plan experiments around claims

Make the experiment plan answer the paper's actual claims:

- comparison experiments for claims of effectiveness,
- ablations for claims about modules/design choices,
- robustness/generalization tests for claims about scope,
- qualitative examples for claims about behavior or failure cases.

Do not add experiments just to make the paper look busy. Every experiment should answer a reviewer question.

Load: `references/experiments.md`

### Phase 3 — Write sections in dependency order

Recommended order:

1. Introduction story/outline.
2. Method outline and pipeline figure sketch.
3. Method prose.
4. Experimental design and results.
5. Related Work.
6. Conclusion and limitations.
7. Abstract.
8. Title.

This follows the principle that the paper should be understood before it is polished.

Load only the section guide needed for the current task:

- Introduction -> `references/introduction.md`
- Abstract -> `references/abstract.md`
- Related Work -> `references/related-work.md`
- Method -> `references/method.md`
- Experiments -> `references/experiments.md`
- Conclusion -> `references/conclusion.md`

### Phase 4 — Human writing and revision pass

For each paragraph:

1. Identify its single message.
2. Put that message in the first sentence when appropriate.
3. Make every technical noun understandable from local context.
4. Check sentence-to-sentence relation: cause, contrast, consequence, refinement, or example.
5. Check whether every statement is needed.
6. Preserve a natural author voice; avoid generic, inflated, overly polished, or repetitive academic filler.
7. Prefer concrete statements tied to the project over broad claims about the field.

Load: `references/does-my-writing-flow-source.md`

### Phase 5 — Claim/evidence audit

For every important claim, especially in the Abstract and Introduction, record:

`Claim | Evidence | Source | Scope | Status`

Possible status values:

- `supported`
- `supported with limited scope`
- `needs evidence`
- `needs citation`
- `overstated`
- `remove`

Hard rule: if the claim cannot be supported, weaken or remove it.

### Phase 6 — Reviewer-style self-review

Review the paper as a skeptical reviewer. Test five dimensions:

1. Contribution.
2. Writing clarity.
3. Experimental strength.
4. Evaluation completeness.
5. Method design soundness.

Then add checks specific to this version:

6. Human authorship/originality.
7. Citation and provenance integrity.
8. Conference-template compliance.

Load: `references/paper-review.md` and `references/human-authorship-and-originality.md`.

### Phase 7 — Final conference-submission gate

Before submission, verify:

1. No template placeholder text remains.
2. Paper title and abstract obey the provided template rules.
3. Figure/table placement and captions follow the provided format.
4. Acronyms are defined on first use.
5. Equations, units, citations, author order, and references are formatted consistently.
6. Every manuscript claim has appropriate evidence or citation.
7. No bibliography entry is fabricated.
8. No result is reported that cannot be traced to the project artifacts.
9. No paragraph contains copied or source-like prose.
10. The author has personally reviewed and accepted every sentence intended for submission.

Load: `references/ieee-conference-format.md` and `references/final-submission-gate.md`.

## Paragraph Clarity / Reverse Outline

Use this whenever the user asks whether the paper "flows" or is clear:

1. Read as an outside reader.
2. State the paper thesis/main claim.
3. List every paragraph's topic sentence.
4. List the evidence/explanation points under each paragraph.
5. Check paragraph -> thesis mapping.
6. Check evidence -> paragraph mapping.
7. Revise or remove paragraphs that cannot be mapped cleanly.
8. Temporarily add headings or transition phrases during revision when needed, then remove unnecessary scaffolding.

## Section-Specific Method Rule

For each Method subsection, when applicable, explicitly think through:

1. Motivation: what problem requires this module?
2. Design: what exactly is done, in what order, from input to output?
3. Technical advantage: why should this design help, and what evidence can verify that?

## Figures and Tables

Treat visual communication as part of the argument, not decoration.

- Pipeline figures should make the core novelty or mechanism visible.
- Tables should have one clear message.
- Captions should explain setting, notation, and what the reader is looking at without repeating the whole discussion.
- Avoid cosmetic complexity that does not improve interpretation.

## Output Contract

When helping with a section, provide:

1. The section logic/outline.
2. The evidence or citation requirements for each part.
3. Author-facing revision guidance, or close edits to supplied text.
4. A short self-review checklist.
5. A claim-evidence map for major claims.

In Human-Authored Mode, do not replace the manuscript with freshly generated submission-ready prose unless the user explicitly changes the authorship requirement.

## Scope Discipline

Do not force this workflow to create novelty where none is established. A strong paper can be clear and honest about what it contributes, what it does not contribute, and where its evaluation is limited.
