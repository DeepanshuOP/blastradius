# 💥 BlastRadius — Unified Master Roadmap v2.0
### Execution-Grounded Change Impact Prediction for Modern CI

> **This document replaces `BlastRadius_Supreme_Roadmap_v1.md` and `BlastRadius_Roadmap_Vol2_Graphify_and_Expansion.md` permanently.** Both sources are archived and are not to be consulted again. Every item in both survives here; Appendix A proves it line by line.
>
> **Course:** BITE497J Project I · School of Computer Science Engineering and Information Systems, VIT · Fall Semester 2026–27
> **Team:** Prisha Vadhavkar (23BIT0010) · Sanskriti Singh (23BIT0256) · Deepanshu (23BIT0264)
> **Guide:** Dr. Yoga Raja C A
> **Project domain:** Software Engineering — Software Maintenance and Evolution
> **Approved title (Zeroth Review, 16-07-2026, status YES):** *BlastRadius: Graph-Based Change Impact Prediction and Dependency Analysis for Software Repositories*
>
> **Stack:** Python 3.11 · tree-sitter (via Graphify fork) · NetworkX · DuckDB + Parquet · PyTorch Geometric · LightGBM · FastAPI · Next.js 15 / TypeScript · Docker · HuggingFace Datasets · Zenodo
> **Build method:** Claude Code (agentic, one micro-task at a time) · Windows/PowerShell + WSL2 · Antigravity for UI work
> **Target venues:** **MSR 2027 Data & Tool Showcase** (primary, paper 10 Nov 2026) · **MSR 2027 Technical Track** (stretch, 23 Oct 2026) · Dublin, co-located with ICSE 2027, 26–27 Apr 2027
> **Benchmarked against:** Meta Predictive Test Selection · Ekstazi / STARTS / HyRTS · RIPPLE (ICSE 2026) · Launchable · Graphify `get_pr_impact`
>
> **Document date:** 4 August 2026. **Day 0 of Phase 0 is today.**

---

## Table of Contents

**Part 0 — How to Read This Document**
- [0.1 Provenance legend](#01-provenance-legend)
- [0.2 What changed from v1 and v2](#02-what-changed-from-v1-and-v2)
- [0.3 The one structural deviation from the v1 spine](#03-the-one-structural-deviation-from-the-v1-spine)

**Part I — Strategy & Framing**
- [1. Project North Star](#1-project-north-star)
- [2. The Novelty Thesis](#2-the-novelty-thesis)
- [3. Hard Dates & Venue Strategy](#3-hard-dates--venue-strategy)
- [4. Part I Expansion — Product Layer](#4-part-i-expansion--product-layer)
  - [4.1 Vision & positioning](#41-vision--positioning)
  - [4.2 Personas & jobs-to-be-done](#42-personas--jobs-to-be-done)
  - [4.3 Explicit non-goals](#43-explicit-non-goals)
  - [4.4 Naming & artifact identity](#44-naming--artifact-identity)
  - [4.5 Scope reconciliation with the approved Zeroth Review](#45-scope-reconciliation-with-the-approved-zeroth-review)

**Part II — Threats & Risk**
- [5. Threat Register T1–T6](#5-threat-register-t1t6)
- [6. Part II Expansion — Extended Threats & Consolidated Risk Register](#6-part-ii-expansion--extended-threats--consolidated-risk-register)

**Part III — Phase Plan**
- [7. Phases Overview](#7-phases-overview)
- [8. Phase 0 — Week Zero: The Harvester](#8-phase-0--week-zero-the-harvester)
- [9. Phase 1 — Corpus Construction & Ground Truth](#9-phase-1--corpus-construction--ground-truth)
- [10. Phase 2 — The Graph Layer](#10-phase-2--the-graph-layer)
- [11. Phase 3 — The Measurement Study](#11-phase-3--the-measurement-study)
- [12. Phase 4 — The Predictor](#12-phase-4--the-predictor)
- [13. Phase 5 — Tool & Web Demo](#13-phase-5--tool--web-demo)
- [14. Phase 6 — Paper, Artifact, Submission](#14-phase-6--paper-artifact-submission)

**Part IV — The Graph Layer, Specified to Implementation Depth**
- [15. Ingestion & Parsing](#15-ingestion--parsing)
- [16. Graph Schema](#16-graph-schema)
- [17. Hard Problems & Accepted Unsoundness](#17-hard-problems--accepted-unsoundness)
- [18. Diff Mapping & Impact Propagation](#18-diff-mapping--impact-propagation)
- [19. Incrementality, Storage & Scale](#19-incrementality-storage--scale)
- [20. Query & Surfacing](#20-query--surfacing)

**Part V — Dataset & Evaluation: The Research Contribution**
- [21. Ground Truth Construction](#21-ground-truth-construction)
- [22. Dataset Schema & Release](#22-dataset-schema--release)
- [23. Repository Selection](#23-repository-selection)
- [24. Baselines](#24-baselines)
- [25. Metrics](#25-metrics)
- [26. Threats to Validity](#26-threats-to-validity)
- [27. Reproducibility & Artifact-Evaluation Readiness](#27-reproducibility--artifact-evaluation-readiness)
- [28. Novelty Positioning Against the Approved Reference List](#28-novelty-positioning-against-the-approved-reference-list)

**Part VI — Engineering Reference**
- [29. Graphify Forensic Reuse Map](#29-graphify-forensic-reuse-map)
- [30. Full Tech Stack](#30-full-tech-stack)
- [31. Data Schemas](#31-data-schemas)
- [32. Evaluation Protocol](#32-evaluation-protocol)
- [33. Repository Layout](#33-repository-layout)
- [34. Claude Code Working Protocol & Prompt Library](#34-claude-code-working-protocol--prompt-library)

**Part VII — Delivery & Team**
- [35. Master Task Graph](#35-master-task-graph)
- [36. Team Split & Workstream Interfaces](#36-team-split--workstream-interfaces)
- [37. Week-by-Week Timeline](#37-week-by-week-timeline)
- [38. Course Deliverable Mapping](#38-course-deliverable-mapping)
- [39. Prioritization Pass & the Review 1 MVP Cut Line](#39-prioritization-pass--the-review-1-mvp-cut-line)
- [40. Workstream Dependency Graph](#40-workstream-dependency-graph)
- [41. Metrics — Research, Engineering SLOs, Project Health](#41-metrics--research-engineering-slos-project-health)

**Part VIII — Decisions, Questions, Deferred Work**
- [42. Decision Register](#42-decision-register)
- [43. Open Questions Requiring a Human Decision](#43-open-questions-requiring-a-human-decision)
- [44. Deferred / Institutional Upgrade Paths](#44-deferred--institutional-upgrade-paths)

**Part IX — Defence & Reference**
- [45. Reviewer Pre-Mortem](#45-reviewer-pre-mortem)
- [46. Immediate Next Actions](#46-immediate-next-actions)
- [47. References](#47-references)
- [48. Final Note](#48-final-note)

**Appendices**
- [Appendix A — Coverage Matrix](#appendix-a--coverage-matrix)
- [Appendix B — Changelog](#appendix-b--changelog)
- [Appendix C — Glossary](#appendix-c--glossary)
- [Appendix D — Self-Check](#appendix-d--self-check)

---

# Part 0 — How to Read This Document

## 0.1 Provenance legend

Every top-level item carries a tag.

| Tag | Meaning |
| --- | --- |
| `[v1]` | Carried from `BlastRadius_Supreme_Roadmap_v1.md`, substantively unchanged |
| `[v2]` | Carried from `BlastRadius_Roadmap_Vol2_Graphify_and_Expansion.md`, substantively unchanged |
| `[merged]` | Both sources described this; the more rigorous version is the base and the other's unique details are absorbed |
| `[new]` | Did not exist in either source — produced by this unification pass |
| `[unverified]` | A factual claim inherited from a source that has not been independently checked. **Do not put an `[unverified]` claim in a paper, a slide, or a viva answer without checking it first.** |

Two further conventions:

- **Decision blocks** (`D-##`) appear wherever the sources contradicted each other, or where this pass had to choose between options the sources left open. Nothing was silently resolved.
- **Expansion subsections** (`### N.x Expansion`) sit at the end of the part they belong to. If you knew v1, everything before an Expansion heading will be familiar; everything inside one is new or absorbed.

## 0.2 What changed from v1 and v2

Short version, for someone who read v1 last week:

1. **Volume II is fully folded in.** The Graphify forensic map, the `TestResolver` design, the prompt library, the repo layout, the course-deliverable mapping, risks T7–T12, ideas B.1–B.7, and RQ5–RQ11 are now in their proper sections rather than in a companion file. Volume II's Part G ("What Changed From Volume I") has been *applied*, not just recorded.
2. **The graph layer is now a chapter, not a phase.** Part IV specifies it to implementation depth: parser strategy with a defended choice, the full node and edge taxonomy, node identity across renames, the hard problems and the unsoundness we accept on purpose, the propagation algorithm with actual scoring, storage-backend evaluation, budgets, and the explainability contract. This was the single weakest area of both sources.
3. **The dataset and evaluation chapter is now stated as a research contribution** (Part V), written against what an MSR reviewer will look for rather than against what a course rubric will look for.
4. **A product and delivery layer was added** (§4, §39, §40, §41): vision, personas, explicit non-goals, a scored backlog with an MVP cut line for Review 1, the workstream dependency graph, and three tiers of metrics.
5. **Sixteen decision blocks** now carry the conflicts that were previously buried or unresolved.
6. **Scope drift against the approved Zeroth Review is flagged explicitly** in §4.5 rather than quietly absorbed.

## 0.3 The one structural deviation from the v1 spine

v1's section order is the skeleton of this document and is preserved end to end. There is exactly one deviation, and it is deliberate: **the deep graph specification lives in Part IV rather than inside §10 (Phase 2)**. Phase 2 remains where v1 put it, with its original subtasks intact, and now points into Part IV for the implementation detail. Burying a twelve-thousand-word implementation chapter inside a four-week phase block would have made both unreadable. Everything else follows v1's ordering exactly.

---

# Part I — Strategy & Framing

## 1. Project North Star

`[v1]`

BlastRadius answers the question every developer asks before pressing "merge": **which tests will this change actually break?**

Not "which files were historically edited together" (that is *co-change*). Not "which tests could theoretically reach the changed code" (that is *reachability*). But which tests, in the real CI pipeline, **actually turned red because of this change**.

That distinction is the entire project. It is the difference between a course project and a paper.

The existing field is split into three camps that never talk to each other:

| Camp | What it predicts | Where labels come from | Representative work |
| --- | --- | --- | --- |
| **Change Impact Analysis (IA)** | Co-changed program elements | Git history (what devs edited together) | RIPPLE (ICSE'26) `[unverified]`, Borg et al. (TSE'17), Huang et al. (TSE'22) |
| **Regression Test Selection (RTS)** | Reachable tests | Static/dynamic dependency analysis | Ekstazi, STARTS, HyRTS, JcgEks (FSE'24) `[unverified]` |
| **Predictive Test Selection (PTS)** | Failing tests | Proprietary CI logs | Meta (ICSE-SEIP'19), Launchable, Google |

The IA camp has public data but the wrong labels. The RTS camp has principled labels but they are *safe over-approximations*, not observations. The PTS camp has the right labels but the data is locked inside Meta, Google, and Salesforce.

**BlastRadius closes the triangle.** We build the first public, execution-grounded, PR-linked, multi-language benchmark that pairs a code change with the individual tests that actually failed — and we use it to measure how badly the other two camps' proxies diverge from reality.

**Even if our predictor loses, the measurement wins.** That is the single most important design decision in this document.

## 2. The Novelty Thesis

`[v1]`

Write this on a whiteboard. Every design decision traces back to it.

> Change impact analysis is evaluated against the wrong ground truth. The field's dominant label — *co-change* — is a proxy for developer behaviour, not for defect propagation. We construct the first public, CI-execution-grounded impact benchmark and show that co-change sets, static reachability sets, and fault-revealing sets are substantially disjoint. We then show that a graph-based predictor trained on execution outcomes outperforms both proxies at the task practitioners actually care about: catching regressions while running fewer tests.

### 2.1 Why this survives a hostile reviewer `[v1]`

**"RIPPLE already does this."** RIPPLE identifies *co-changed* program elements and is explicitly framed around intent-aware co-change relationships. It never observes a test outcome. We are predicting a different dependent variable. Cite it in Related Work as the closest IA work and state the label difference in one sentence.

**"Meta already did predictive test selection in 2019."** Yes — on a proprietary monorepo with an internal build system, with no public artifact. Their reported result (catching 99.9% of regressions while running ~33% of impacted tests) has never been independently replicated on open-source CI because the data did not exist. We are creating the data that makes replication possible. That is a Data & Tool Showcase contribution on its own.

**"RTPTorrent already has test outcomes."** RTPTorrent (MSR 2020) is 20 Java projects on **Travis CI**, built for regression test *prioritization*. Travis's OSS role collapsed after 2021, the data is pre-2020, it is single-language, and it is organized by build job, not by pull request with a changed-file diff. Our contribution is GitHub-Actions-era, PR-anchored, multi-language, and carries the changed-file → failing-test edge explicitly.

**"GHALogs already has GitHub Actions logs."** GHALogs (MSR 2025) is 116k workflows / 25k projects / 513k runs with full logs `[unverified]` — a superb *substrate*, and we should cite and possibly build on it. But it stops at the log. It does not parse per-test verdicts, does not link runs to PR diffs, does not de-flake, and does not label fault revelation. The gap between "we have the logs" and "we have labelled (change → failing test) pairs" is the entire engineering contribution.

**"Isn't this just SWE-bench?"** SWE-bench / SWT-Bench / CI-Repair-Bench are *agent evaluation* benchmarks: given a bug, can a model fix it. We are a *prediction* benchmark: given a diff, which tests go red. Different task, different consumers, different metrics.

### 2.2 The three deliverables `[v1]`

Unchanged from Zeroth Review, sharpened:

1. **BR-Bench** — a labelled, execution-grounded CI-outcome dataset on HuggingFace + Zenodo (DOI).
2. **BlastRadius** — an open-source tool: graph builder + predictor + web demo, MIT licensed.
3. **The measurement paper** — quantifying co-change vs reachability vs fault-revelation divergence.

### 2.3 Good news on the approved abstract `[v1]`

The submitted Zeroth Review abstract already says the system will be *"evaluated using publicly available GitHub repositories by comparing the predicted impact with actual modifications **and CI/CD test outcomes**."* The fault-revelation reframe is **already inside the approved scope**. No title change, no re-approval. When briefing Dr. Yoga Raja C A, frame it as: *"we are prioritising the CI/CD-outcome half of the evaluation as the primary contribution, because that is where the literature gap is."*

The approved keyword list helps further: it already contains **Regression Test Prediction** and **Software Repository Mining**, which is exactly the reframe, in the guide's own approved document. Read §4.5 before the briefing anyway — there is real drift, and it is better volunteered than discovered.

## 3. Hard Dates & Venue Strategy

`[merged]` — v1's table, re-verified against the live MSR 2027 site on 4 Aug 2026 during this unification pass. Re-verify again in September; conference sites move dates.

| Date | Event | Track |
| --- | --- | --- |
| **~25 Aug 2026** | MSR 2027 Mining Challenge dataset proposal call opens | Mining Challenge |
| **Tue 20 Oct 2026** | Abstract deadline (mandatory) | MSR Technical |
| **Fri 23 Oct 2026** | Full paper deadline — 10pp + 2pp refs, ACM sigconf, **double-anonymous** | MSR Technical |
| **Thu 5 Nov 2026** | Abstract deadline ✅ *confirmed on the live site* | **MSR Data & Tool Showcase** |
| **Tue 10 Nov 2026** | Paper deadline — **4pp + 1pp refs** ✅ *confirmed*, IEEEtran 10pt, **single-anonymous** ✅ *confirmed* | **MSR Data & Tool Showcase** |
| Thu 3 Dec 2026 | Early reject notification | Technical |
| 4–8 Dec 2026 | Author response period | Technical |
| Tue 5 Jan 2027 | Acceptance notification | Data & Tool |
| Fri 8 Jan 2027 | Author notification | Technical |
| Sun 24 Jan 2027 | Camera ready | Data & Tool |
| Tue 26 Jan 2027 | Camera ready | Technical |
| **26–27 Apr 2027** | Conference, The Convention Centre Dublin ✅ *confirmed* | — |

### 3.1 Recommended strategy: Data & Tool Showcase is the primary target `[v1]`

Reasons, in order of weight:

1. **Timeline.** 10 Nov gives you 18 more days than 23 Oct, and the course runs to October. Those 18 days are the difference between a rushed submission and a clean one.
2. **Length.** 4 pages + 1 of references is achievable by a three-person undergraduate team. 10 pages of ACM two-column with a full empirical evaluation is not, on this timeline, at MSR's acceptance bar.
3. **Fit.** The track exists precisely for reusable datasets and tools designed for the MSR community as a whole. That is literally BR-Bench.
4. **Distinguished Paper Award** is offered on this track.
5. **Single-anonymous** review means author names stay on the paper — much less artifact-anonymisation friction. Confirmed on the live track page: single-anonymous is used *because* the track requires describing prior uses of the data, which would disclose identity anyway.

### 3.2 Dual-submission plan `[v1]`

Only if Phase 3 lands early. The two tracks accept *different contributions*, so a Technical Track submission on the **measurement study** (RQ1/RQ2 — the divergence analysis) and a Data & Tool submission on the **dataset + tool** are not duplicate submissions. They must share no substantial text and must cross-cite. If there is any doubt about whether the split is clean, submit only to Data & Tool. A desk rejection for concurrent submission would be catastrophic and is not worth the upside. See **D-16**.

### 3.3 Mining Challenge wildcard `[v1]`

If BR-Bench is in decent shape by late August, submit a 1–2 page dataset proposal to the MSR 2027 Mining Challenge call. If selected, the dataset becomes the dataset the entire conference builds on, the proposal appears in the proceedings, and the team joins the organizing committee. Low probability, absurdly high payoff, ~6 hours of work. Do it.

### 3.4 Mandatory compliance checklist (both tracks) `[v1]`

- [ ] Artifact archived on **Zenodo / figshare / OSF with a DOI** — GitHub alone is explicitly not accepted.
- [ ] Data released under **CC-BY 4.0** or **CC0**; code under **MIT** (compatible with the Graphify fork).
- [ ] `CITATION.cff` in the repo; DOI-based citation in the camera-ready.
- [ ] Collection tooling open-sourced with documented re-creation instructions.
- [ ] `requirements.txt` / `pyproject.toml` + a running example reviewers can execute.
- [ ] FAIR principles statement (Findable, Accessible, Interoperable, Reusable — the track page names these explicitly).
- [ ] Generative-AI usage disclosure in Acknowledgements (Claude Code is in use — **disclose it**; ACM and IEEE both require this).
- [ ] `[new]` IEEE Conference Proceedings formatting: title 24pt, body 10pt, LaTeX `IEEEtran`. Confirmed on the track page.
- [ ] `[new]` At least one author registers and presents. Budget for this or plan for a remote/virtual presentation policy — check by January.

---

## 4. Part I Expansion — Product Layer

`[new]` — absent from both sources. A roadmap that never states what the product *is* outside the paper will drift toward whatever the paper needs that week.

### 4.1 Vision & positioning

**Vision.** A developer opening a pull request should see, before any CI runs, a ranked and *justified* list of the tests most likely to fail — and be able to click any one of them and see the exact path through the codebase that put it there.

**Positioning statement.** For **developers and CI maintainers on medium-to-large repositories** who **cannot afford to run the full test suite on every push**, BlastRadius is a **change-impact ranking tool** that **predicts which tests will actually fail, not which tests could theoretically be affected**. Unlike **static regression-test-selection tools**, which optimise for safe over-approximation, BlastRadius optimises for **the ranked shortlist a human will actually read**, and it is trained and evaluated on **observed CI outcomes rather than co-change proxies**.

**Two products, one codebase.** This matters for prioritisation:

| | BR-Bench (the dataset) | BlastRadius (the tool) |
| --- | --- | --- |
| Primary consumer | MSR researchers | Developers, CI maintainers |
| Success measure | Cited, reused, extended | Installed, run, trusted |
| Failure mode | Labels are wrong | Predictions are unexplainable |
| Deadline pressure | 10 Nov 2026 | Review 3 / viva |
| If time runs out | **Protect this one** | Ship a reduced demo |

### 4.2 Personas & jobs-to-be-done

| Persona | Job to be done | What they need from BlastRadius | Success signal | Priority |
| --- | --- | --- | --- | --- |
| **Reviewer** (reviews someone else's PR) | "Tell me where to look and what to be suspicious of" | A short ranked list of at-risk tests and the files they connect to, with the path shown | Reviewer opens the panel before reading the diff | **P1** |
| **Author** (opened the PR) | "Which tests should I run locally before I push again?" | `blastradius predict --base main` on the working tree, ranked, in <10s | Author runs it more than once per PR | **P1** |
| **CI maintainer** | "Cut CI minutes without letting regressions through" | A cost curve, a calibrated threshold, and a safe abstain path | Adopts the GitHub Action on one repo | **P2** |
| **MSR researcher** | "Give me labelled (change → failing test) pairs I can build on" | Parquet + HuggingFace + a datasheet + a loader that works first try | `load_dataset()` in someone else's paper | **P0 (primary)** |
| **Course examiner / guide** | "Is this a real system, defensibly built?" | A live demo, corpus statistics, and honest numbers | Passes Review 1/2/3 and the viva | **P0 (hard constraint)** |
| **Coding agent** `[v2 B.6]` | "Which tests validate this edit before I commit?" | An MCP tool that answers in one call | Deferred — see §44 | **P4 (deferred)** |

The two P0s are not in conflict, but they pull in different directions under time pressure: the examiner wants a working demo, the MSR reviewer wants a trustworthy dataset. **§39's cut line resolves this explicitly** — the demo is scoped small and early rather than large and late.

### 4.3 Explicit non-goals

Writing these down is what stops a three-person team from accidentally attempting a PhD. BlastRadius deliberately **does not**:

1. **Prove impact.** We rank; we do not compute a sound over-approximation. If you need a safety guarantee, use STARTS or Ekstazi. Stated in the paper's Limitations, not hidden.
2. **Perform data-flow analysis.** No program dependence graph, no slicing, no points-to analysis. See §16.1 and **D-05**.
3. **Require a successful build.** The entire pipeline works from source at an arbitrary SHA without compiling. This is a hard constraint, not a shortcut — see §15.3.
4. **Support every language.** Java and Python. TypeScript is a stretch goal that will probably be cut. See **D-03**.
5. **Do cross-repository / supply-chain impact in v1.** Parked with the infrastructure noted — see §44 and `[v2 B.4]`.
6. **Replace code review.** It is an attention-direction tool, not an approval gate.
7. **Run in real time inside CI on the critical path.** The GitHub Action comments after the fact; it never blocks a merge.
8. **Guarantee flakiness-free labels.** We filter, annotate, and ship three splits. We do not claim a clean label set.
9. **Use an LLM anywhere in the reproducible pipeline.** See Rule 6 in §34 and **D-17**.
10. **Handle monorepos in v1.** See **D-13**.

### 4.4 Naming & artifact identity

`[v2 A.0]` — Graphify's own `PRInfo` dataclass documentation uses the phrase **"blast radius"** to describe `communities_touched` + `nodes_affected`. The term is also common DevOps vocabulary (Terraform, SRE, chaos engineering). It is not anyone's trademark and nobody owns it.

Three options were on the table:

1. **Keep `BlastRadius`.** Already in the approved Zeroth Review title. Evocative, memorable. The collision is with a phrase, not a product name.
2. **Keep the project name, rename the artifacts.** Tool = `blastradius`, dataset = **`BR-Bench`**. Datasets get cited independently of tools, so distinct naming actually helps.
3. Rename entirely — unnecessary, and would require re-approval.

Resolved as **D-08** below: option 2.

### 4.5 Scope reconciliation with the approved Zeroth Review

`[new]` — required by the merge brief: *where the roadmaps have drifted beyond the approved scope, flag it explicitly rather than quietly expanding.*

The approved abstract (16-07-2026, status YES) commits to: an AST + dependency graph over source files, classes and functions; prediction of affected **files and test cases**; presentation through an **interactive dependency graph**; evaluation on **public GitHub repositories** against **actual modifications and CI/CD test outcomes**; metrics **precision, recall, F1**.

| # | Roadmap element | Inside approved scope? | Verdict | Action |
| --- | --- | --- | --- | --- |
| 1 | CI/CD test outcomes as the *primary* ground truth | Yes — the abstract names them | **No drift.** Re-prioritisation within approved scope | Mention in the Week 1 briefing, no approval needed |
| 2 | Predicting affected **files** as a distinct output | Yes — abstract says "files and test cases" | **No drift**, but v1 nearly dropped it | **Restored** as a first-class output — see §18.8 |
| 3 | Interactive dependency graph UI | Yes — explicitly promised | **No drift** | Phase 5 delivers it; do not cut it |
| 4 | Precision / recall / F1 | Yes | **No drift** | Reported, plus ranking metrics — see §25 |
| 5 | **Ranking metrics** (Recall@k, MAP, MRR, APFD, NDCG) | Not named in the abstract | **Minor drift — additive.** Justified because impact is a ranked list | Report P/R/F1 *as well*, never instead |
| 6 | **A learned model** (LightGBM, R-GCN) | Abstract says "graph-based framework"; no ML mentioned | **Genuine drift.** The keyword *Regression Test Prediction* covers it, but the abstract body does not | **Tell the guide.** Frame as: the graph produces features; the model ranks them |
| 7 | **A released public dataset (BR-Bench) as the headline contribution** | Not in the abstract at all | **The largest drift in the project** | **Tell the guide explicitly.** Frame as: the dataset is what makes the evaluation the abstract promised actually possible |
| 8 | **External venue targeting (MSR 2027)** | Not in the abstract | **Drift — but the good kind** | Tell the guide in Week 1; guides advocate harder with a real venue |
| 9 | Corpus scale (300 candidate repos, ≥50k instances, 6-month rolling capture) | Abstract says "publicly available GitHub repositories", unquantified | **Scale drift.** Not a scope violation, but a resourcing one | Show the corpus dashboard at Review 1 so the scale is visible and owned |
| 10 | Docker re-execution gold subset | Not mentioned | **Method detail, not scope drift** | No action |
| 11 | Flakiness filtering and three splits | Not mentioned | **Method detail** | No action |
| 12 | Language restriction to Java + Python | Abstract is language-agnostic | **Narrowing, not expansion** | State the restriction in Review 1 with the justification from §15.2 |
| 13 | Forking a third-party tool (Graphify) as the extraction engine | Not mentioned | **Drift worth pre-empting** | Say it out loud at Review 1 with the LOC ratio from §29.3. A guide who hears it from you is fine; a guide who discovers it is not |

**The one-paragraph version for the guide:** *"The approved abstract promised evaluation against CI/CD test outcomes. It turns out no public dataset of that kind exists, so building it became the main technical work — and it's good enough to submit externally to MSR 2027. The system itself is unchanged from what you approved: AST plus dependency graph, predicting affected files and tests, shown in an interactive graph. What's new is that we also release the evaluation data, and we rank with a learned model on top of the graph rather than with a fixed heuristic."*

---

# Part II — Threats & Risk

## 5. Threat Register T1–T6

`[v1]` — **read this before writing any code.** Six things can kill this project. Five of them are data problems, and the first one is on a countdown timer.

### 5.1 T1 — 🔴 CRITICAL: GitHub Actions logs expire after 90 days `[v1]`

Workflow logs and artifacts for **public repositories are retained 90 days maximum**, and public repos cannot extend it (only private/internal can go to 400 days). Run *metadata* (conclusion, timestamps, SHAs) persists indefinitely via the API; **the per-test detail you need lives only in logs and artifacts.**

Today is 4 Aug 2026. Every day you do not harvest, you permanently lose a day of ground truth from ~early May 2026.

**Mitigation: the harvester ships in Week 0, before the graph builder, before the model, before anything.** It is the only irreversible deadline in the project. Everything else can be rebuilt; expired logs cannot.

Design it as a rolling daemon that runs continuously from Week 0 to submission. By 10 Nov you will have ~14 weeks of continuous capture plus a ~90-day retrospective backfill — roughly six months of coverage, which is a defensible corpus window.

### 5.2 T2 — 🟠 Survivorship bias in merged PRs `[v1]`

If you label from the merge commit, you see a green pipeline every time — developers fix failures *before* merging. Your positive class evaporates.

**Mitigation: label at the level of individual pushes within the PR, not the merge.** Every push to a PR head triggers a new workflow run. The intermediate red runs are exactly your ground truth. The GitHub API exposes this: `GET /repos/{o}/{r}/pulls/{n}/commits` gives every head SHA in the PR's life, and `GET /repos/{o}/{r}/actions/runs?head_sha={sha}` gives the runs for each. Your unit of observation is the **(head SHA, workflow run)** pair, not the PR.

Also harvest **closed-unmerged PRs** and **`push` events on non-default branches**, which have a much higher failure base rate and are usually thrown away by mining studies.

### 5.3 T3 — 🟠 Flaky test contamination `[v1]`

A test that fails non-deterministically is a false positive in your label set. Industry reports put flakiness at meaningful double-digit percentages of test failures; on Travis, ~1.72% of all builds were manually restarted with nearly half passing on retry, and in OpenStack 55% of reviews involved repeated builds with 42% changing test results. `[unverified — attribute these three figures to a specific paper before they go in a slide or the paper; they are the kind of number a reviewer checks]`

**Mitigation: a four-filter flakiness pipeline, with the label kept but annotated rather than silently dropped.**

1. **Same-SHA flip rule** — identical commit SHA, two runs, different verdict for the same test ⇒ flaky. Highest-confidence signal; costs nothing because re-runs are already in the API.
2. **Broken-trunk filter (Dr. CI pattern)** — if the test also fails on the PR's *base* commit run, the change did not cause it. Exclude from positives. This is the single highest-value filter and it is cheap.
3. **Rolling flip-rate** — per-test failure rate over a trailing 30-day window; flag any test above a threshold (start at 2%, report sensitivity).
4. **Coverage-free DeFlaker heuristic** — if a failing test has no graph path of length ≤ *k* to any changed file, mark it `suspect_unrelated`.

Ship **three splits**: `strict` (all four filters), `permissive` (filter 2 only), `raw`. Report headline numbers on `strict`, sensitivity on the others. Reviewers reward this; it converts a threat into a methodological contribution.

### 5.4 T4 — 🟡 Language and build-system fragmentation `[v1]`

Every ecosystem reports test results differently. You cannot support all of them.

**Mitigation — recommended language stack, in priority order:**

| Priority | Language | Report format | Why |
| --- | --- | --- | --- |
| **1** | **Java** (Maven/Gradle) | Surefire/Failsafe JUnit XML | **Baseline comparability.** Ekstazi, STARTS, HyRTS, RTPTorrent are all Java. Without Java you cannot compare against the RTS state of the art, and a reviewer will ask why. |
| **2** | **Python** (pytest) | `--junitxml` | Largest GHA corpus; simplest to re-execute in Docker for the gold subset. |
| **3** | TypeScript (Jest/Vitest) | JSON reporter | Stretch goal. Adds a "multi-paradigm" claim. Cut without hesitation if Weeks 1–5 slip. |

Java + Python is the target. Ship Java first — it unlocks the baselines. TypeScript is a nice-to-have that you will probably cut, and that is fine. Full justification and the type-system argument in §15.2; decision recorded as **D-03**.

### 5.5 T5 — 🟡 Log parsing is a swamp `[v1]`

Raw GHA logs are unstructured, ANSI-coloured, timestamp-prefixed, and every runner formats differently.

**Mitigation: prefer structured sources over log scraping, in this order.**

1. **Check-run annotations** (`GET /repos/{o}/{r}/check-runs/{id}/annotations`) — repos using `EnricoMi/publish-unit-test-result-action` or `dorny/test-reporter` emit one annotation per failing test with the test name and file path. Structured, and **persists past 90 days**. Prefer this above everything.
2. **Workflow artifacts** (`GET .../actions/runs/{id}/artifacts`) — many repos upload the JUnit XML directly. Small, perfectly structured, machine-readable. 90-day window.
3. **Job logs** (`GET .../actions/jobs/{id}/logs`) — the fallback. Parse with per-framework regexes; strip ANSI and the ISO-8601 line prefix first.
4. **Docker re-execution** — the gold subset only (see T6).

Make source-tier a first-class column in the schema (`label_source ∈ {annotation, artifact, log, reexec}`) and report per-tier accuracy. Reviewers love provenance honesty.

### 5.6 T6 — 🟡 "Your labels are observational, not causal" `[v1]`

The strongest reviewer objection you will face. Observing that test *t* failed on a run containing change *c* does not prove *c* caused it.

**Mitigation: a small, expensive, beautiful gold subset.** Take 300–500 instances. For each, in Docker: check out base SHA, run the test suite, record verdicts. Check out head SHA, run again. A test that is `PASS@base → FAIL@head` is *causally* attributable to the change under a fixed environment. This is the same F→P construction SWE-bench uses, inverted.

Use it to (a) validate that your cheap observational labels agree with causal labels at rate *r*, and (b) report *r* as a headline number. Budget ~72–120 machine-hours; parallelise across three laptops or a free-tier cloud VM. Start this in Week 6, not Week 12.

---

## 6. Part II Expansion — Extended Threats & Consolidated Risk Register

### 6.1 T7–T12 `[v2 Part F]`

| # | Risk | Severity | Mitigation |
| --- | --- | --- | --- |
| **T7** | **Graphify upstream churn.** 150 releases; v8 is an active dev branch, not a stable tag. An upstream change mid-project could break the fork. | 🟠 | Pin the commit SHA on day one. Vendor rather than track. Never `git pull` upstream after Week 2 without re-running the full pipeline. |
| **T8** | **Test-node binding rate too low.** If <70% of CI test IDs bind to graph nodes, graph features are mostly nulls. | 🔴 | Measure in **Week 5, not October**. Dashboard metric. Mitigations: widen conventions, add `tests_by_layout`, use SCIP for Java, or drop low-binding repos. |
| **T9** | **Matrix builds multiply everything.** One PR × 12 OS/version legs = 12 runs, partially overlapping failures. | 🟡 | Decide the aggregation rule in Week 2 (**D-12**: union failures, record `n_matrix_legs`) and state it in the paper. Do not let this be discovered during labelling. |
| **T10** | **Monorepos break the "one graph per repo" assumption.** | 🟡 | Detect multi-module layouts via `manifest_ingest.py` package nodes; either exclude monorepos from v1 or scope graphs per module. **D-13** decides in Week 3. |
| **T11** | **Dataset leakage into future LLM training.** Once BR-Bench is public, models trained after release may have memorised it. | 🟡 | Not this paper's problem, but note it in Limitations and adopt a **canary string** in the dataset — a growing convention for public benchmarks. |
| **T12** | **Three-person integration failure.** The most common cause of death for team projects. | 🟠 | Weekly Sunday integration (§34 Rule 9). Add: no branch lives longer than 5 days; the `test_id` contract test must pass on every merge. |

### 6.2 T13–T19 `[new]`

| # | Risk | Severity | Why it is real | Mitigation |
| --- | --- | --- | --- | --- |
| **T13** | **MSR deadline collides with placement season and course reviews.** Deepanshu owns Phases 0/1/4 — the critical path — and is simultaneously in an active campus placement window. Review 2 and the Technical-Track deadline both land in October. | 🔴 | Named explicitly in the merge brief as a required entry. A single unavailable person on the critical path in the last three weeks is how this project fails. | **Declare the blackout window now, in Week 1, before it is needed.** Front-load Deepanshu's irreversible work (harvester T0.3, labelling engine T1.3) into August. Pre-assign a named backup per critical task: Sanskriti covers labelling, Prisha covers feature extraction. Add a `owner_backup` column to the Master Task Graph. Nothing on the critical path may have exactly one person who understands it. |
| **T14** | **Repo attrition below the corpus floor.** 300 candidates → ~60–100 usable is v1's estimate; if the real number is 25, the corpus is too thin for per-repo random-effects analysis. | 🟠 | Attrition compounds across four independent filters (CI liveness, parseable, bindable, has failures). | Measure attrition per filter stage on the dashboard from Week 1. Gate 1 (Week 4) triggers frame widening. Fallback: drop the ≥500-star threshold to ≥200 and re-run the frame. |
| **T15** | **Graph build does not scale to real repositories.** A 20k-file Java monorepo with deep inheritance can blow the 10-minute cold-build budget and the 8 GB memory ceiling. | 🟠 | Named in the merge brief. tree-sitter is fast, but symbol resolution across a large corpus is the quadratic part. | Hard budgets in §19.4 with an enforcement gate: any repo exceeding the ceiling is dropped from the frame at ingestion, not at analysis time, and the exclusion is counted and reported. Cap on transitive closure depth (§18.4). |
| **T16** | **Dynamic-language imprecision destroys precision.** Python's name-based resolution produces phantom edges; if the Python subset's precision is far worse than Java's, the headline number is dragged down by half the corpus. | 🟠 | Named in the merge brief. This is the known weakness of AST-only analysis on duck-typed languages. | **Turn it into a finding, not a defect.** Report every headline metric stratified by language. If Python is worse, that *is* RQ5-adjacent evidence about graph precision. Measure phantom-edge rate directly using Graphify's `test_phantom_cross_package_call.py` as a template. |
| **T17** | **CI log mining yields too little usable signal.** Parser coverage of 40–70% is v1's own expectation; if annotations are rare and artifacts are rarer, the log tier carries everything and its precision is the weakest. | 🟠 | Named in the merge brief. The yield is a product of three probabilities: repo runs tests × failure is captured × parser extracts names. | Instrument yield per stage from day 3 of harvesting, not week 4. If the annotation tier is <10% of instances, prioritise repos that use `publish-unit-test-result-action` in the frame — a legitimate, disclosable sampling bias. |
| **T18** | **Schema churn after Phase 1.** Retro-fitting a schema change across 40 files and a built corpus is a week nobody has. | 🟡 | v1 flags this in §31 but does not risk-register it. | Freeze schemas in Week 2 with all three team members signing off. Any post-freeze change requires a written migration note and a full pipeline re-run on the mini-corpus. |
| **T19** | **Ethics/legal exposure from mining 300 untrusted repositories.** Cloning and parsing arbitrary code; publishing derived data containing commit authorship. | 🟡 | Not in either source as a *risk*, only as a paper section. | Keep Graphify's `security.py` in full (§29.2). Public repos with a `LICENSE` only. Pseudonymise `author_login`. `gitleaks` scan before release. Honour GitHub ToS. State all of it in the paper. |

### 6.3 Consolidated risk register `[new]`

Likelihood × Impact, with owner and the observable that should trigger the mitigation.

| ID | Risk | Likelihood | Impact | Exposure | Owner | Trigger / early-warning signal |
| --- | --- | --- | --- | --- | --- | --- |
| T1 | GHA log expiry | **Certain** | Fatal | 🔴🔴 | Deepanshu | The calendar. Mitigation starts today. |
| T8 | Test-node binding rate <70% | Medium | Fatal | 🔴 | Prisha | Dashboard binding-rate tile, Week 5 |
| T13 | Placement + deadline collision | **High** | Severe | 🔴 | All three | Placement calendar published in Week 1 |
| T6 | "Observational, not causal" | High | Severe | 🟠 | Deepanshu | Reviewer pre-mortem; gold subset by Week 8 |
| T2 | Survivorship bias | High | Severe | 🟠 | Deepanshu | Positive-class prevalence on dashboard <2% |
| T3 | Flaky contamination | **Certain** | Moderate | 🟠 | Sanskriti | Same-SHA flip rate >5% of failures |
| T14 | Repo attrition | Medium | Severe | 🟠 | Prisha | Usable-repo count <40 at Week 3 |
| T15 | Graph build does not scale | Medium | Severe | 🟠 | Prisha | Any cold build >10 min at Week 4 |
| T16 | Dynamic-language imprecision | **High** | Moderate | 🟠 | Sanskriti | Python precision <½ Java precision at Week 7 |
| T17 | Too little CI signal | Medium | Severe | 🟠 | Sanskriti | Parser coverage <30% at Week 3 |
| T12 | Integration failure | Medium | Severe | 🟠 | All three | Any branch older than 5 days |
| T7 | Graphify upstream churn | Low | Severe | 🟡 | Prisha | Pinned SHA drift detected in CI |
| T4 | Language fragmentation | High | Moderate | 🟡 | Sanskriti | TS parser slipping past Week 5 → cut |
| T5 | Log parsing swamp | **Certain** | Moderate | 🟡 | Sanskriti | Per-parser precision <95% on fixtures |
| T9 | Matrix builds | High | Low | 🟡 | Deepanshu | `n_matrix_legs` > 1 on >20% of instances |
| T10 | Monorepos | Medium | Low | 🟡 | Prisha | >3 frame repos detected as multi-module |
| T18 | Schema churn | Medium | Moderate | 🟡 | All three | Any schema PR after Week 2 |
| T19 | Ethics/legal | Low | Severe | 🟡 | Deepanshu | Pre-release `gitleaks` scan |
| T11 | Dataset leakage into LLMs | Low | Low | 🟢 | — | Post-publication only |

**Read the register this way:** the top four are the ones to actively manage weekly. Everything at 🟡 needs a named mitigation in the plan and a check at the relevant gate, not continuous attention.

---

# Part III — Phase Plan

## 7. Phases Overview

`[v1]`

| Phase | Name | Window | Duration | Key Output | Gate |
| --- | --- | --- | --- | --- | --- |
| **0** | 🔴 Week Zero — The Harvester | Aug 4–10 | 6 days | Daemon capturing GHA runs 24/7 | Data flowing before any other work |
| **1** | Corpus & Ground Truth | Aug 10–Sep 6 | 4 wks | BR-Bench v0.1, ≥50k labelled instances | ≥5k positive (failing) instances |
| **2** | Graph Layer | Aug 24–Sep 20 | 4 wks | Commit-pinned code graphs via Graphify fork | Graph builds for 20 repos in <10 min each |
| **3** | The Measurement Study | Sep 14–Oct 11 | 4 wks | RQ1–RQ3 answered, all baselines run | Divergence result is statistically solid |
| **4** | The Predictor | Sep 28–Oct 25 | 4 wks | LightGBM + R-GCN, beats all baselines | Recall@20% > best baseline, *p* < 0.05 |
| **5** | Tool & Web Demo | Oct 12–Nov 2 | 3 wks | CLI + FastAPI + Next.js demo + GH Action | Reviewer can run it in <10 min |
| **6** | Paper, Artifact, Submission | Oct 19–Nov 10 | 3 wks | 4pp IEEE paper + Zenodo DOI | Submitted 10 Nov |

Phases deliberately overlap. **Phase 0 must not.**

---

## 8. Phase 0 — Week Zero: The Harvester

**Status: START TODAY · Aug 4–10 · Duration 6 days · Owner: Deepanshu · Backup: Sanskriti** `[v1, owner_backup new]`

Nothing else matters this week. Every hour of delay costs an hour of permanently unrecoverable ground truth. The harvester is deliberately dumb: it captures raw material now, and you parse it later at leisure.

**Design principle: capture wide, parse narrow.** Store raw responses to disk (gzipped JSONL), never parse in the hot path. Parsing bugs are fixable; expired logs are not.

### 8.1 T0.1 — Repository sampling frame *(~3 hrs)* `[v1]`

Prompt goal: produce `data/frame/repos.csv` — the candidate repository universe.

- Query **SEART GitHub Search** (`https://seart-ghs.si.usi.ch/`) rather than hand-rolling GitHub search. It indexes every repo with ≥10 stars across 25 characteristics and exists precisely for MSR sampling. Cite Dabic, Aghajani & Bavota (MSR 2021).
- Selection criteria: language ∈ {Java, Python}; ≥500 stars; ≥1000 commits; not a fork; ≥1 commit in the last 60 days; has a `LICENSE`; ≥50 PRs in the last 90 days.
- Then filter for **CI liveness** via the API: repo must have ≥100 workflow runs in the last 90 days and a workflow whose name/steps match test intent (`test`, `ci`, `build`, `pytest`, `mvn`, `gradle`).
- Exclude workflows matching `release|deploy|docker|publish|docs|dependabot|codeql|lint-only`.
- Target: **300 candidate repos**, which will attrit to ~60–100 usable ones. Over-sample aggressively; attrition on this pipeline is brutal.

Subtasks:
1. Export SEART query results to CSV; store the exact query string in `data/frame/QUERY.md` for reproducibility.
2. Write `src/harvest/liveness.py` — for each repo, hit `GET /repos/{o}/{r}/actions/runs?per_page=1` and read `total_count`.
3. Write `src/harvest/workflow_triage.py` — fetch `.github/workflows/*.yml`, classify each workflow as `test | build | deploy | other` by name + step commands.
4. Emit `repos.csv` with columns: `owner, repo, lang, stars, commits, default_branch, n_runs_90d, test_workflow_ids, license`.
5. Manually eyeball the top 50 — 30 minutes of human review here saves a week later.

### 8.2 T0.2 — Token pool & rate-limit governor *(~2 hrs)* `[v1]`

Prompt goal: `src/harvest/ratelimit.py` — never get 403'd, never lose a night of harvesting.

- Authenticated REST limit is 5,000 requests/hour **per token**. Three team members = three fine-grained PATs = 15,000/hour. Store in `.env`, never commit.
- Implement a token pool with round-robin selection, per-token remaining-quota tracking read from `X-RateLimit-Remaining` / `X-RateLimit-Reset` headers.
- Honour `Retry-After` on 429 and secondary-rate-limit responses. Exponential backoff with jitter, max 6 retries.
- Budget model: ~3–5 requests per workflow run (jobs list + N log/artifact fetches). At 15k/hr that is ~3,000–5,000 runs/hour, comfortably 50k+ runs/day with backoff headroom.
- Persist a resumable cursor per repo in SQLite so a crash never re-fetches.

Subtasks:
1. Implement `TokenPool` class with quota-aware selection.
2. Implement `get_with_backoff()` wrapper — the *only* HTTP entry point in the codebase.
3. Log every request to `logs/requests.jsonl` (url, status, tokens_remaining, duration) for later rate analysis.
4. Add a `--dry-run` mode that estimates the request budget for a repo list without spending it.

Ready-to-paste prompt: §34.4 C.1.

### 8.3 T0.3 — The rolling harvester daemon *(~6 hrs)* ⭐ THE CRITICAL TASK `[v1]`

Prompt goal: `src/harvest/daemon.py` — a resumable, idempotent, crash-tolerant capture loop.

For each repo, for each PR updated in the window, capture:

```
GET /repos/{o}/{r}/pulls?state=all&sort=updated&direction=desc   → PR metadata
GET /repos/{o}/{r}/pulls/{n}/files                              → changed files + patch
GET /repos/{o}/{r}/pulls/{n}/commits                            → every head SHA in the PR's life
GET /repos/{o}/{r}/actions/runs?head_sha={sha}                  → runs for that SHA
GET /repos/{o}/{r}/actions/runs/{id}/jobs                       → per-job conclusions
GET /repos/{o}/{r}/commits/{sha}/check-runs                     → check runs (annotation source)
GET /repos/{o}/{r}/check-runs/{cid}/annotations                 → per-test failures ★ persists >90d
GET /repos/{o}/{r}/actions/runs/{id}/artifacts                  → JUnit XML artifacts ★ structured
GET /repos/{o}/{r}/actions/jobs/{jid}/logs                      → raw logs ✂ 90-day window
```

Write raw responses to `data/raw/{owner}__{repo}/{yyyy-mm}/{kind}.jsonl.gz`. Never mutate. Never parse here.

Subtasks:
1. Implement per-repo cursor state in SQLite (`repo, last_pr_updated_at, last_run_id, status`).
2. Implement the capture loop with the endpoint sequence above, writing gzipped JSONL.
3. Prioritise **failed** runs (`conclusion=failure`) for log download — success logs are far less valuable per byte and you are storage-bound.
4. Download artifacts only when `name` matches `/test|junit|report|surefire|results/i` and `size_in_bytes < 50MB`.
5. Add SIGTERM handling that flushes cursors cleanly.
6. Deploy: run on the machine that stays on. A cheap always-on option is a `cron` job in WSL2 plus a GitHub Actions scheduled workflow as a redundant secondary harvester on a different token.
7. Emit a daily `data/raw/MANIFEST.json` with per-repo counts so you can watch the corpus grow.
8. `[v2 A.1]` Lift `_parse_ci` and `_path_match` out of Graphify's `prs.py` into the harvester. `_parse_ci` distils `statusCheckRollup` and correctly maps `CANCELLED`/`TIMED_OUT` → `FAILURE`; `_path_match` gets path-boundary correctness right (`config.py` must not match `g.py`) and has a real test suite behind it. Both solve exact problems on the critical path.

### 8.4 T0.4 — Storage layout & integrity *(~2 hrs)* `[v1]`

Prompt goal: never lose data, always know what you have.

- Directory contract: `data/raw/` (immutable, append-only) → `data/interim/` (parsed, regenerable) → `data/processed/` (Parquet, the dataset) → `data/gold/` (re-execution subset).
- SHA-256 every raw file; store hashes in `data/raw/CHECKSUMS.txt`.
- Set up **rclone or rsync to a second physical location nightly**. One dead SSD ends this project. This is not paranoia; it is the cheapest insurance you will ever buy.
- Add `.gitignore` for `data/` — never commit raw data to Git.

### 8.5 T0.5 — Live corpus dashboard *(~2 hrs)* `[v1]`

Prompt goal: a single `streamlit run dashboard.py` showing corpus health, refreshed daily.

- Runs captured (total, per day, per repo, per language).
- Failure rate distribution — you need to see the positive class accumulating.
- Label-source tier breakdown (annotation / artifact / log).
- Repos yielding zero failures (candidates for removal from the frame).
- Storage consumed and projected 90-day total.

This exists so that at any moment any team member can answer "do we have enough data yet?" without running a script. **It also becomes Figure 1 of the paper and the live demo at Review 1.**

### 8.6 Phase 0 exit criteria `[v1]`

- [ ] Harvester has run uninterrupted for 72 hours
- [ ] ≥50,000 workflow runs captured across ≥60 repos
- [ ] ≥3,000 runs with `conclusion=failure` captured **with** logs or annotations
- [ ] Nightly backup verified by restoring one file from the mirror
- [ ] Dashboard live and bookmarked by all three team members

### 8.7 Phase 0 Expansion

**T0.6 — Dependabot / dependency-bump PR capture** *(~1 hr)* `[v2 Part G.6]`
Harvest Dependabot and Renovate PRs explicitly, tagged as such. They cost nothing extra in the same crawl, they are abundant and machine-generated with consistent formatting, they have a meaningful failure rate, and they enable **RQ10** (do dependency bumps have a systematically different blast radius?) and the cross-repo extension in §44. Add `is_bot_pr` and `bot_name` to the instance record.

**T0.7 — Attrition instrumentation** *(~1 hr)* `[new]`
Every filter stage writes its input and output counts to `data/frame/ATTRITION.json`: candidates → CI-live → has-test-workflow → produces-parseable-outcomes → produces-failures → parseable-graph → binds-tests. Surface it as a funnel on the dashboard. This is both an early warning for **T14** and, later, a figure in the paper's dataset-construction section that reviewers specifically look for.

**T0.8 — Frame-freeze protocol** *(~30 min)* `[new]`
The repo frame must be frozen and version-tagged (`frame_v1.csv`, dated) before Phase 1 labelling begins. Repos may be *dropped* later with a recorded reason; repos may not be *added* after freeze without bumping the frame version and re-running affected analyses. Silent frame growth is an invisible confound.

---

## 9. Phase 1 — Corpus Construction & Ground Truth

**Status: NEXT · Aug 10–Sep 6 · Duration 4 weeks · Owner: Deepanshu (lead) + Sanskriti (parsers) · Backup: Sanskriti on labelling** `[v1, owner_backup new]`

Phase 0 gave you a pile of raw JSON. Phase 1 turns it into BR-Bench: a labelled, de-flaked, versioned dataset with defensible provenance.

### 9.1 T1.1 — Test-result parser suite *(~8 hrs)* `[v1]`

Prompt goal: `src/parse/` — one parser per (label source × framework), all emitting a single canonical record.

Canonical output record:
```python
TestOutcome(
    run_id: int, job_id: int, repo: str, head_sha: str,
    test_id: str,          # canonical: "module::class::method"
    test_file: str | None, # repo-relative path
    status: Literal["pass","fail","error","skip"],
    duration_s: float | None,
    failure_message: str | None,   # truncated to 2000 chars
    label_source: Literal["annotation","artifact","log","reexec"],
    parser_confidence: float,      # 1.0 for XML, lower for regex log parsing
)
```

Parsers to implement:
1. `annotations.py` — check-run annotations. Highest confidence, parse `path`, `title`, `message`.
2. `junit_xml.py` — Maven Surefire/Failsafe + pytest `--junitxml`. Same schema, one parser. Confidence 1.0.
3. `log_pytest.py` — regex over `FAILED tests/test_x.py::TestY::test_z - AssertionError`. Strip ANSI + timestamp prefix first.
4. `log_maven.py` — Surefire console output: `Tests run: N, Failures: N, Errors: N` blocks and `[ERROR] ClassName.methodName:LINE`.
5. `log_gradle.py` — `> Task :test FAILED` blocks and the test-summary section.
6. `log_jest.py` (optional) — `✕ test name` lines under `FAIL path/to/spec.ts`.

Subtasks:
1. Build a fixture corpus: hand-pick 40 real logs across frameworks into `tests/fixtures/`, hand-label expected output.
2. Implement each parser against fixtures; target ≥95% precision on test-name extraction.
3. Write `normalize_test_id()` — the single hardest and most important function in the parser layer. Java `com.foo.BarTest#testBaz` and pytest `tests/test_bar.py::TestBar::test_baz` must both map to a stable, comparable ID. Document the canonicalisation rules in the paper. **`[v2 G.1]` Do not write a new normalizer: extend `vendor/graphify-br/graphify/ids.py`, reuse its NFKC + casefold recipe, and inherit its `test_id_normalization_contract.py` contract test.** See **D-09**.
4. Implement `resolve_test_file()` — map a test ID back to a repo-relative source path. For Java, derive from the FQN + source roots; for Python it is already a path. **This mapping is what connects the label to the graph.** Without it the whole project is disconnected.
5. Report per-parser coverage: what fraction of failed jobs yielded at least one parsed test name. Expect 40–70%. Publish the number honestly.

Ready-to-paste prompt: §34.4 C.2.

### 9.2 T1.2 — Change-set extraction & diff features *(~4 hrs)* `[v1]`

Prompt goal: `src/parse/changeset.py` — from a PR head SHA, produce the changed-file set with structural detail.

- Files changed, additions, deletions, status (`added|modified|removed|renamed`).
- Hunk-level line ranges — needed later for function-level attribution.
- **Function/class-level change extraction** via tree-sitter: parse base and head versions of each changed file, diff the symbol tables, emit `changed_symbols: list[str]`. This is what lets you claim method-level granularity, which is where the RTS literature is (Ekstazi is class-level; JcgEks pushed to method level in FSE 2024 `[unverified]`).
- Change taxonomy flags: `touches_test_file`, `touches_build_config`, `touches_ci_config`, `is_dependency_bump`, `is_docs_only`, `is_formatting_only`.
- Exclude `is_docs_only` and `is_formatting_only` instances from the main splits but keep them as a labelled negative-control set — a nice sanity check in the paper (a docs-only change should predict *zero* failing tests; any model that does not is broken).

Full change taxonomy and the propagation semantics of each change type: **§18.2**.

### 9.3 T1.3 — The labelling engine *(~6 hrs)* ⭐ CORE `[v1]`

Prompt goal: `src/label/build_labels.py` — produce the (change, test, label) triples that are the dataset.

For each `(head_sha, workflow_run)`:
1. Resolve the **base SHA** (PR base at that moment) and locate the base's own workflow run.
2. Build `T_head_fail` = tests failing at head; `T_base_fail` = tests failing at base.
3. **Fault-revealing set** `T_reveal = T_head_fail \ T_base_fail` — the broken-trunk filter, applied here.
4. Apply same-SHA flip detection across all runs of `head_sha`; move flippers to `T_flaky`.
5. Apply rolling flip-rate filter; annotate remaining with `flakiness_score`.
6. Emit one row per (instance, candidate test) pair, where candidate tests = the full test set observed for that repo in a trailing window. Label = 1 if test ∈ `T_reveal`, else 0.

Subtasks:
1. Implement base-run resolution — non-trivial; the base SHA may have no run of the same workflow. Fall back to nearest ancestor commit with a run of the same `workflow_id`, and record `base_run_distance` as a data-quality column.
2. Implement the three splits: `strict`, `permissive`, `raw`.
3. Compute and store `flakiness_score` per test per repo per window.
4. Handle severe class imbalance explicitly — expect 1 positive per 200–2000 candidate tests. Store the full negatives but ship a `negatives_sampled` variant at a documented ratio for convenience.
5. Emit `data/processed/instances.parquet` and `labels.parquet` partitioned by repo.

Full edge-case list and the exact algorithm are in the ready-to-paste prompt at §34.4 C.3 — including the matrix-build union rule (**D-12**), the newly-added-test rule, the deleted-test rule, and the critical "empty base failure set ≠ base was green" trap.

### 9.4 T1.4 — Co-change label track (the comparison arm) *(~3 hrs)* `[v1]`

Prompt goal: `src/label/cochange.py` — reproduce the *other* camp's ground truth so you can measure divergence.

- Mine file-level co-change from Git history using **PyDriller**: for each changed file, the set of files that co-occurred in commits over a trailing window.
- Compute evolutionary coupling (support, confidence, lift) per file pair — the classic association-rule formulation used across the IA literature.
- Emit `cochange_impact_set` per instance: the top-*k* files by confidence.
- **This is not a baseline you are trying to beat. It is the measurement subject.** RQ1 is literally "how much does this set overlap with the fault-revealing set?"

### 9.5 T1.5 — Gold subset by Docker re-execution *(~10 hrs, start Week 6)* `[v1]`

Prompt goal: `src/gold/reexec.py` — 300–500 causally-attributed instances.

1. Select instances from repos with a reproducible container setup (prefer repos with a `Dockerfile` or a `setup-python` / `setup-java` workflow that pins versions).
2. For each: `git checkout {base_sha}` → install deps → run suite → record. Then `git checkout {head_sha}` → run suite → record.
3. `PASS@base → FAIL@head` = causal positive. `FAIL@base → FAIL@head` = pre-existing, excluded. Run each side **twice** to catch flakiness in-house.
4. Pin everything: base image digest, dependency lockfile, random seeds where the framework allows.
5. Report the **agreement rate** between observational labels and gold causal labels. This single number is the credibility anchor of the whole paper.

Budget: 300 instances × ~15 min × 2 checkouts × 2 repetitions ≈ 60 machine-hours. Parallelise 4-wide across team laptops overnight; two weeks of nights is enough. **Nobody owns this alone — it is embarrassingly parallel across all three machines.**

### 9.6 T1.6 — Dataset packaging & datasheet *(~4 hrs)* `[v1]`

Prompt goal: BR-Bench, ready to cite.

1. Parquet files with an explicit, documented schema (see §31).
2. HuggingFace dataset with a `README.md` dataset card and a working `load_dataset()` loader script.
3. **Datasheet for Datasets** (Gebru et al. format) — motivation, composition, collection, preprocessing, uses, distribution, maintenance. Reviewers on this track look for it.
4. Zenodo deposit with DOI; `CITATION.cff` in the repo.
5. `LICENSE`: CC-BY 4.0 for data, MIT for code.
6. Ethics/legal note: only public repos, only permissively licensed projects, no personal data beyond public commit authorship, honour GitHub ToS. State it explicitly in the paper.

### 9.7 Phase 1 exit criteria `[v1]`

- [ ] ≥50,000 labelled instances across ≥50 repos, ≥2 languages
- [ ] ≥5,000 positive (fault-revealing) instances in the `strict` split
- [ ] Parser precision ≥95% on the hand-labelled fixture set
- [ ] All three splits generated and internally consistent
- [ ] Datasheet drafted
- [ ] Gold subset pipeline running (does not need to be finished)

### 9.8 Phase 1 Expansion

**T1.7 — Canary string** *(~15 min)* `[v2 T11]`
Embed a documented canary string in the released dataset so future contamination of LLM training corpora is detectable. One line in the datasheet explains it.

**T1.8 — File-level ground truth track** *(~2 hrs)* `[new]`
The approved abstract promises prediction of affected **files**, not only tests. Build the second ground-truth arm: for each instance, the set of files modified in *subsequent* commits of the same PR plus files touched in the merge commit. This is the CIA-literature-native label and it is what makes the results comparable to Borg, Huang, Dai, and Gupta & Gupta. Cheap — it comes from data already harvested. See §18.8 and §21.4.

**T1.9 — Label-provenance mirror of Graphify's confidence tiers** *(~1 hr)* `[v2 A.1]`
Graphify tags extraction confidence as `EXTRACTED` / `INFERRED` / `AMBIGUOUS`. Mirror that pattern for label provenance rather than inventing a parallel vocabulary: it keeps one confidence language across graph and labels, and it is a precedent you can cite when a reviewer asks why the tiers exist.

---

## 10. Phase 2 — The Graph Layer

**Status: Aug 24–Sep 20 · Duration 4 weeks · Owner: Prisha (lead) + Deepanshu · Backup: Deepanshu** `[v1, owner_backup new]`

This is where Graphify enters. Read §29 (Graphify Forensic Reuse Map) before starting, and **Part IV for the implementation specification** — this section is the plan; Part IV is the design.

### 10.1 T2.1 — Fork and strip Graphify *(~5 hrs)* `[merged v1 + v2 A.2]`

Prompt goal: `vendor/graphify-br/` — a research-grade, deterministic fork.

Graphify is MIT licensed, so forking and vendoring is legally clean. Preserve the LICENSE and add a `NOTICE` file crediting `safishamsi/graphify`. Cite it in the paper.

```bash
git clone https://github.com/safishamsi/graphify.git vendor/graphify-br
cd vendor/graphify-br
git checkout v8
git log -1 --format=%H > ../GRAPHIFY_COMMIT.txt   # ← record for the paper
uv sync --all-extras
uv run pytest tests/ -q                            # ← baseline: everything green
```

Then, in order, committing after each step with tests green:

1. **Delete** the LEAVE modules and their tests (list in §29.4). Re-run suite. Fix imports.
2. **Remove the LLM semantic-extraction pass entirely.** Non-deterministic output is fatal for a reproducible research artifact, and it costs tokens you do not need to spend. Graphify's own docs confirm code-only corpora require no API key and run fully offline via tree-sitter — that is exactly the mode you want, permanently pinned.
3. **Pin** tree-sitter grammar versions in `pyproject.toml`. Record versions in `ENVIRONMENT.md`. Record the exact Graphify commit SHA in the paper's replication section.
4. **Add** `graphify/extractors/test_nodes.py` — test detection (§10.3, §29.6).
5. **Add** `graphify/test_resolution.py` — registered as a `LanguageResolver`, not a fork hack. See **D-10**.
6. **Extend** `validate.py` schema: `node_type`, `test_id`, new relations. Their validator then enforces your schema for free.
7. **Add** `graphify/commit_graph.py` — worktree-based commit-pinned builds.
8. **Add** `graphify/br_features.py` — the query/feature primitives.
9. **Keep** `LICENSE` (MIT). **Add** `NOTICE` crediting `safishamsi/graphify` with the pinned commit SHA.
10. Keep and harden: tree-sitter multi-language AST extraction, the SHA-256 content cache, `--update` incremental rebuild, the NetworkX node-link `graph.json` format, Leiden community detection, the HTML visualiser.
11. Strip: video/audio transcription, PDF/image/Office extraction, Obsidian/wiki export, all cloud backends, telemetry, query logging.
12. Run their test suite (`uv run pytest tests/ -q`) after every strip operation; fix what you broke. **If `test_phantom_cross_package_call.py` breaks, you have broken graph quality and you will not notice for six weeks.**

**Realistic LOC estimate for your additions: 1,200–2,000 lines, against ~15,000+ inherited.** That ratio is the whole argument for forking rather than building, and it is the number to quote at Review 1 when someone asks whether this is your own work.

### 10.2 T2.2 — Commit-pinned graph builder *(~6 hrs)* ⭐ `[v1]`

Prompt goal: `src/graph/build.py` — a graph *at a specific commit*, not "the graph of the repo".

Graphify builds one graph for a working directory. You need a graph per instance, at the base SHA of that instance. This is the single biggest extension you make to it.

1. `git worktree add` at the base SHA (much faster than clone-per-commit, and disk-cheap).
2. Run the stripped extractor; emit `graph_{repo}_{sha}.json`.
3. **Aggressive caching** — most consecutive instances differ by a handful of files. Use Graphify's `--update` incremental path plus content hashing: reuse the previous graph and re-extract only changed files. Target <10 s per incremental instance after the first full build.
4. Store graphs as compressed node-link JSON in `data/graphs/`, indexed by `(repo, sha)`.
5. Validate: node/edge counts, orphan rate, parse-failure rate per language. A repo with >20% parse failures gets dropped from the frame.
6. `[v2 G.4]` **Blocking correctness test:** assert that an incremental build at SHA *X* produces the *same* graph as a cold build at SHA *X*, over 5 real commits of a small repo. If they diverge, the whole dataset is untrustworthy. Treat any divergence as a release-blocking bug, not a known issue.

Full algorithm, invalidation strategy, and storage design: **§19**. Ready-to-paste prompt: §34.4 C.4.

### 10.3 T2.3 — Test-node typing and the test↔code bridge *(~5 hrs)* ⭐ CORE `[merged v1 + v2 A.3]`

Prompt goal: make tests first-class citizens in the graph.

Graphify's schema has `file_type ∈ {code, document, paper, image, rationale}`. You need `test`.

1. Classify every node as `test | source | config | build` using path heuristics (`src/test/java/**`, `tests/**`, `**/*_test.py`, `**/*.spec.ts`, `**/*Test.java`) plus AST signals (JUnit annotations, `unittest.TestCase` base class, pytest naming conventions).
2. **Bind each `test` node to its canonical `test_id`** from T1.1's `normalize_test_id()`. This is the join key between the graph and the labels. If this binding is weak, everything downstream is noise. Measure and report the binding rate.
3. Add `test → source` edges via **three binding strategies in confidence order** (§29.6), emitting all three with distinct confidence so the model can learn which to trust.
4. Extend the edge schema with `edge_type ∈ {imports, calls, inherits, tests, tests_by_convention, tests_by_layout, co_changes, co_fails, config_of}` and keep Graphify's `confidence` tagging (`EXTRACTED` = 1.0, `INFERRED` with a score).
5. Emit graph statistics per repo for the paper: |V|, |E|, test-node fraction, median test→source distance, binding rate.
6. `[v2 G.2]` Implement it as a **registered `LanguageResolver` plugin** in Graphify's `resolver_registry`, not as a bolted-on fork hack. Clean, upstreamable, and it puts Java FQN test binding exactly where such logic belongs.

**The metric that decides whether the project works: binding rate.** For every `test_id` observed in CI outcomes, does a graph node exist with that ID? **Measure it in Week 5** and put it on the dashboard. Below ~70% and graph features are mostly missing data — at which point you widen the conventions, add `tests_by_layout`, use SCIP for Java, or drop the affected repos. Do not discover this in October. This is threat **T8** and gate **Gate 1.5**.

### 10.4 T2.4 — Graph enrichment with history *(~4 hrs)* `[v1]`

Prompt goal: edges that encode more than syntax.

1. `co_changes` edges weighted by evolutionary coupling confidence from T1.4.
2. `co_fails` edges — tests that historically fail together (a strong signal in the test-prioritization literature).
3. Node attributes: churn (commits in trailing 90d), age, LOC, cyclomatic complexity (via `radon` for Python, `javalang`/PMD for Java), author count, historical failure rate for test nodes.
4. Persist as node/edge attribute tables in Parquet, keyed by `(repo, sha, node_id)` — do not bloat the JSON.

### 10.5 T2.5 — Graph query API *(~3 hrs)* `[v1]`

Prompt goal: `src/graph/query.py` — the feature-extraction primitives everything else calls.

- `shortest_path_length(changed_file, test_node)` — with and without `co_changes` edges.
- `min_distance_to_any_changed(test_node, changed_set)` — the single most predictive feature in the literature.
- `k_hop_neighborhood(changed_set, k)` — the reachability baseline.
- `same_community(test_node, changed_set)` — using Graphify's Leiden partition.
- `pagerank_delta` — centrality of changed nodes.
- Cache everything per `(repo, sha)` in DuckDB; recomputing shortest paths per instance is the thing that will make your pipeline take a week instead of an hour.

Full canonical query catalogue: **§20.1**.

### 10.6 Phase 2 exit criteria `[merged]`

- [ ] Graph builds for all corpus repos, <10 min cold / <10 s incremental
- [ ] Test-node binding rate ≥80% (measured against T1.1 test IDs); **≥70% is the hard floor** `[v2]`
- [ ] Query API benchmarked: <100 ms per instance for the full feature set
- [ ] Graph statistics table drafted for the paper
- [ ] `[v2]` Incremental-vs-cold-build equivalence test passing on 5 real commits
- [ ] `[new]` Parse-failure rate reported per language; every dropped repo has a recorded reason

### 10.7 Phase 2 Expansion

**T2.6 — SCIP precision tier for the Java subset** *(~6 hrs, optional)* `[v2 A.1]`
Graphify's `scip_ingest.py` ingests SCIP JSON — Sourcegraph's precise code-intelligence format. `scip-java` produces *compiler-accurate* symbol graphs rather than tree-sitter heuristics. Running it over the Java subset unlocks **RQ5**: *heuristic AST graph vs precise SCIP graph — how much does graph precision actually buy you against real CI outcomes?* Nobody has run that ablation. High reviewer value, medium effort, and it is a clean cut if time runs short. Requires a successful build, so it only applies to the reproducible-build subset — see §15.3.

**T2.7 — Package/manifest layer** *(~2 hrs)* `[v2 A.1]`
Keep Graphify's `manifest_ingest.py`: it parses `pyproject.toml`, `go.mod`, `pom.xml` into canonical package nodes with `depends_on` edges and one hub node per package. Dependency bumps are a large, distinctive class of CI failure and the class the proxies will be *worst* at — this gives you package nodes for free and directly feeds **RQ10**.

**T2.8 — Phantom-edge measurement** *(~2 hrs)* `[new]`
Adopt `test_phantom_cross_package_call.py` as the template for a *measured* metric, not just a regression test: report per-language phantom-edge rate on a hand-checked sample of 100 call edges. Phantom edges are what inflate the reachability baseline and turn graph features into noise (**T16**). A reported phantom rate is also the honest denominator for every precision claim about the graph.

**T2.9 — Graph-quality gate on the dashboard** *(~1 hr)* `[new]`
Four tiles: binding rate, parse-failure rate, orphan-node rate, phantom-edge estimate. All four visible weekly from Week 5. Graph quality failures are silent; the dashboard is what makes them loud.

---

## 11. Phase 3 — The Measurement Study

**Status: Sep 14–Oct 11 · Duration 4 weeks · Owner: Sanskriti (lead) + Prisha · Backup: Prisha** `[v1, owner_backup new]`

This phase produces the paper's headline result. **It does not depend on the predictor working.** If Phase 4 collapses, Phase 3 alone is a publishable measurement contribution. Protect it accordingly — it is your insurance policy.

### 11.1 The Research Questions `[v1]`

**RQ1 — How much do co-change, reachability, and fault-revelation impact sets diverge?**
> For a given change, let *C* = co-change predicted set, *R* = static reachability set, *F* = fault-revealing set. Report |C∩F|/|C∪F|, |R∩F|/|R∪F|, precision and recall of *C* and *R* against *F*, per language, per change size, per repo.

Hypothesis: *C* and *F* are nearly disjoint at the file level, and *R* has high recall but catastrophic precision (the known safety-vs-precision trade-off of RTS, quantified for the first time against real CI outcomes at PR granularity in the wild).

**RQ2 — What change characteristics predict divergence?**
> Which changes are the proxies wrong about? Change size, file type, cross-module reach, dependency bumps, config changes, test-file edits, author tenure.

Hypothesis: proxies degrade sharply on cross-module and configuration changes — precisely the changes developers most need help with. That framing turns a measurement into a *motivation*.

**RQ3 — Can a learned model trained on execution outcomes beat both proxies?**
> Phase 4's question, answered here in the same protocol.

**RQ4 (Data & Tool paper) — What does the dataset contain and how reliably was it labelled?**
> Composition, label-source tiers, flakiness prevalence, observational-vs-causal agreement rate from the gold subset.

### 11.2 Baseline subtasks `[v1]`

**T3.1 — Baseline: Retest-All** *(~1 hr)* — trivial but essential; the denominator for every cost claim.

**T3.2 — Baseline: Random & path-similarity** *(~2 hrs)* — random ranking; token-overlap between changed-file path and test-file path (surprisingly hard to beat on small changes — report it honestly).

**T3.3 — Baseline: Static reachability (STARTS-like)** *(~4 hrs)* — *k*-hop reachability over the BlastRadius graph from changed files to test nodes, for *k* ∈ {1,2,3,∞}. This is the in-house re-implementation of the static class-level RTS idea, and it is what makes RQ1's *R* set.

**T3.4 — Baseline: Ekstazi (real tool, Java subset)** *(~6 hrs)* — run actual Ekstazi on the Java gold subset. Yes, it is painful. Yes, a reviewer will ask. This is the difference between "we compared against a re-implementation" and "we compared against the tool." Run it on the ~50 instances where the Maven build is reproducible; report on that subset and be explicit about the scope.

**T3.5 — Baseline: Historical failure frequency** *(~2 hrs)* — rank tests by trailing-window failure rate. This is the non-trivial baseline RTPTorrent ships and it is startlingly strong. **If you cannot beat it, you do not have a paper — so build it early and know the number.**

**T3.6 — Baseline: Evolutionary coupling / co-change association rules** *(~3 hrs)* — from T1.4. The IA-camp baseline, standing in for the RIPPLE-family approach.

**T3.7 — Baseline: Graphify `get_pr_impact`** *(~3 hrs)* ⭐ HIGH VALUE `[merged v1 + v2 G.5]`
Run stock Graphify's own PR impact heuristic (`graphify prs {n}`, `get_pr_impact`, `--conflicts` community overlap) against your labels.

`[v2]` **Split it into two baselines**, because its output is not a test ranking:
- **GRAPHIFY-COMMUNITY** — all test nodes whose Leiden community is in `communities_touched`, ranked by node degree.
- **GRAPHIFY-DIRECT** — only test nodes that are themselves inside changed files. Near-zero recall by construction; **report it anyway as the floor.**

`[v2 A.0]` And state the finding plainly: **`compute_pr_impact` is a zero-hop operation** — it iterates the node set, matches `source_file` against changed paths, and reports which nodes live *inside* the changed files plus their communities. It traverses no edges, propagates nothing, and has no concept of a test node.

This is a genuinely clever inclusion: a widely-adopted developer tool whose impact estimate has never been validated against CI outcomes. Evaluating it is a small, concrete, quotable finding — *"a popular graph-based impact tool achieves X% recall against real test failures"* — and exactly the kind of result the MSR audience enjoys. **Be scrupulously fair and non-adversarial**; frame it as "graph proximity heuristics in general", not as an attack on one project. Ready-to-paste prompt: §34.4 C.5.

### 11.3 T3.8 — Divergence analysis & statistics *(~8 hrs)* `[v1]`

1. Jaccard, precision, recall, F1 of each proxy set against *F*, with bootstrapped 95% CIs.
2. Stratify by language, change size (LOC, files touched), change type, repo.
3. Significance: Wilcoxon signed-rank for paired comparisons across instances; Holm–Bonferroni for multiple comparisons; **effect sizes (Cliff's delta)** — SE reviewers ask for effect sizes, not just *p*-values.
4. Per-repo random-effects analysis so no single mega-repo drives the result.

### 11.4 T3.9 — Figures *(~6 hrs)* `[v1]`

Figures are content, not decoration. Budget real time.

1. **Teaser (Fig. 1):** one real PR, three coloured impact sets overlaid on a small subgraph, showing the disjointness at a glance. This figure sells the paper.
2. **Pipeline (Fig. 2):** harvest → parse → label → graph → predict, with the label-source tiers visible.
3. **Venn/UpSet plot** of *C*, *R*, *F* overlap.
4. **Recall@k curves** for all baselines + model.
5. **Cost curve:** regressions caught vs % of test suite executed — the Meta-style framing that practitioners read first.
6. All figures: vector PDF, ≥10pt fonts, colour-blind-safe palette, readable at print size.

### 11.5 Phase 3 exit criteria `[v1]`

- [ ] All seven baselines implemented and evaluated on the same splits
- [ ] RQ1 answered with CIs and effect sizes
- [ ] Divergence result holds under all three flakiness splits (the robustness check that saves you in rebuttal)
- [ ] Teaser figure drafted

### 11.6 Phase 3 Expansion

**T3.10 — Qualitative failure taxonomy** *(~8 person-hours)* ⭐ **best effort-to-value item in the project** `[v2 B.3, G.7]`
RQ2 asks *what* predicts divergence; this asks *why*. Sample ~100 divergence cases. Two team members independently card-sort the failure modes, compute **Cohen's κ**, resolve disagreements, produce a taxonomy figure.

Likely categories: reflection and dynamic dispatch · dependency-version bumps · configuration and environment · test-fixture coupling · resource contention and ordering · cross-module contract changes · serialization/schema drift.

MSR reviewers value mixed-methods work disproportionately, it costs about a day, it requires no new engineering, and a taxonomy figure is highly citable. Answers **RQ8**.

**T3.11 — Impact half-life analysis** *(~3 hrs)* `[v2 B.5]`
Nobody has asked: **how long does a change stay dangerous?** With a time-indexed dataset, measure whether a file's fault-revealing footprint decays after modification, and whether recently-changed regions have elevated blast radius for *subsequent* changes. If impact has a measurable half-life, that is a new empirical finding about software evolution and it directly implies a time-decay feature for every RTS tool. One plot, one paragraph, potentially quite memorable. Answers **RQ9**.

**T3.12 — Dependency-bump stratum** *(~2 hrs)* `[v2 B.4, G.6]`
Using the Dependabot PRs harvested in T0.6, test whether dependency bumps have systematically different blast radius than source changes. Answers **RQ10**.

**T3.13 — Test-gap detection** *(~5 hrs)* `[v2 B.2]`
While building BR-Bench you will observe changes that **broke something no test covered** — visible as a change followed by a later revert, a follow-up fix commit, or a bug-report issue, with a green pipeline in between.

Invert the framing: **BlastRadius doesn't just predict which tests fail — it identifies where the test suite is blind.** If a change touches a high-centrality node whose *k*-hop test neighbourhood is empty, that is a coverage gap *in the dependency-graph sense*, detectable without running coverage instrumentation.

Why this is strong: it is a **positive, actionable developer-facing feature**, not just a prediction; "graph-detected test gaps" is measurable against SZZ-identified bug-inducing commits — did the gaps predict where bugs later appeared?; it is *safe*, because it needs only the graph and the test bindings, so it works even where the predictor underperforms; and it is a natural second paper. Answers **RQ6**. Prototype the panel in the demo — it is one query (§20.1 Q4).

**T3.14 — Flakiness-split sensitivity** *(~2 hrs)* `[v2 B.8]`
Report how much every result changes between `strict`, `permissive`, and `raw`. This is the robustness section. Answers **RQ11**.

**T3.15 — Extended research questions register** `[v2 B.8]`

| RQ | Question | Phase | Feasibility | In the 4-page paper? |
| --- | --- | --- | --- | --- |
| **RQ1** | How much do co-change, reachability and fault-revelation diverge? | 3 | Core | **Yes — headline** |
| **RQ2** | What change characteristics predict divergence? | 3 | Core | Yes |
| **RQ3** | Can a learned model beat both proxies? | 4 | Core | Yes, compressed |
| **RQ4** | What does the dataset contain and how reliably was it labelled? | 1–3 | Core | **Yes — §IV** |
| **RQ5** | How much does graph *precision* matter? (tree-sitter vs SCIP) | 3–4 | Medium — needs `scip-java`. High reviewer value | Stretch |
| **RQ6** | Can graph structure identify test-suite blind spots, and do they predict later bugs? | 3 | Medium — needs SZZ. **Best new-idea candidate** | Future work → second paper |
| **RQ7** | Is predicted blast radius well-calibrated, and what is the cost-optimal operating point? | 4 | **Easy** — reuses existing model output | **Yes** |
| **RQ8** | Qualitative taxonomy of proxy failures | 3 | **Easy** — ~8 person-hours, high value | **Yes** |
| **RQ9** | Does fault-revealing impact decay over time? | 3 | Easy — pure analysis | If space |
| **RQ10** | Do dependency bumps have different blast radius? | 3 | Easy — Dependabot PRs already harvested | If space |
| **RQ11** | How much do results change across flakiness splits? | 3 | Easy — the robustness section | **Yes — appendix** |

Do not attempt all of them. **RQ7 and RQ8 are nearly free and belong in the paper. RQ6 is the second paper.**

---

## 12. Phase 4 — The Predictor

**Status: Sep 28–Oct 25 · Duration 4 weeks · Owner: Deepanshu (lead) + Sanskriti · Backup: Sanskriti** `[v1, owner_backup new]`

### 12.1 Evaluation protocol — fix this before training anything `[v1]`

- **Time-based splits only.** Train on instances before date *t*, test after. A random split leaks future information through shared repos and tests and will inflate your numbers by a wide margin. This is the most common fatal flaw in ML4SE papers and reviewers hunt for it.
- **Two evaluation regimes:**
  - *Within-project*: train and test on the same repo (the realistic deployment setting).
  - *Cross-project (leave-one-project-out)*: never saw this repo in training (the generalisation claim).
  Report both. Cross-project will be much worse. Say so plainly — honest negative results on cross-project generalisation are themselves publishable and reviewers respect them.
- **Metrics:** Recall@k (k = 1/5/10/20% of suite), APFD / APTF, MAP, NDCG@10, plus RTS-native metrics: safety violation, precision violation, suite reduction %.
- **Headline framing:** "catches X% of fault-revealing tests while executing Y% of the suite" — directly comparable to the Meta result.

Full protocol: §32. Metric definitions and justification: §25.

### 12.2 T4.1 — Feature engineering *(~6 hrs)* `[v1]`

Mirror the Meta PTS feature families, extended with graph features. Group and ablate by family.

*Graph features (your contribution):*
- min / mean / median shortest-path distance from test to any changed file
- distance with and without `co_changes` edges (ablation isolates the history signal)
- same-Leiden-community indicator; community-overlap fraction
- number of distinct paths of length ≤3; edge-type-weighted distance
- PageRank / betweenness of changed nodes; "god node" indicator (Graphify's most-connected-node concept)
- test node degree, test subtree size

*Change features:*
- files changed, lines added/deleted, hunks, distinct directories, max directory depth
- change type flags from T1.2; touches build config; is dependency bump
- number of changed symbols (function/class level)

*Test-history features:*
- trailing failure rate (7d/30d/90d), flakiness score
- last-failed recency, times run, mean duration
- historical co-failure with tests currently predicted to fail

*Cross features:*
- historical failure rate of *this test* given *this file* changed (the classic association-rule feature; extremely strong within-project, useless cross-project — a great ablation story)
- author's historical failure rate; time since test last modified

`[new]` *Dynamic-boundary features* — see §17.3: `changed_file_has_dynamic_boundary`, `test_reaches_dynamic_boundary`, `n_reflection_sites_on_path`. These convert an acknowledged unsoundness into signal the model can use, and they feed the RQ8 taxonomy.

### 12.3 T4.2 — Model A: gradient-boosted trees *(~5 hrs)* `[v1]`

LightGBM ranker (`lambdarank`) and binary classifier. Handles extreme imbalance well with `scale_pos_weight`, trains in minutes, and is the honest strong baseline. **This will probably be your best model.** Accept that gracefully — a well-tuned GBDT beating a GNN is a legitimate and frequently-published finding.

Subtasks: hyperparameter search with Optuna; per-family ablation; SHAP feature attribution (feeds directly into the explainability story the Zeroth Review abstract promised).

### 12.4 T4.3 — Model B: heterogeneous GNN *(~10 hrs)* `[v1]`

PyTorch Geometric R-GCN or HGT over the code graph. Node types `{source, test, config, build}`, edge types from T2.3. Input features include a binary "changed" mask on the changed nodes. Task: link prediction / node classification over test nodes.

Subtasks: subgraph sampling (2–3 hop around changed nodes — full-graph training will OOM); neighbour sampling with `NeighborLoader`; class-imbalanced loss (focal loss); early stopping on validation Recall@20%.

**Honest expectation:** the GNN may not beat LightGBM. Budget one week; if it is not competitive after that, ship it as an ablation and move on. **Do not let it eat Phase 5.**

### 12.5 T4.4 — Model C (stretch): LLM re-ranker *(~6 hrs)* `[v1]`

Take the top-50 candidates from Model A, feed Claude the diff hunks + the test source, ask for a re-ranking with a one-line rationale per test. Evaluate Recall@10 improvement and cost per PR.

Value: (a) gives the tool a genuinely useful explanation feature; (b) makes the demo compelling; (c) a small, well-scoped LLM ablation is on-trend at MSR 2027 without being the whole paper. Keep it strictly optional and clearly separated — **do not let an LLM into the reproducible core pipeline.** Governed by **D-17**.

### 12.6 T4.5 — Statistical rigour & ablations *(~4 hrs)* `[v1]`

Five seeds per configuration, report mean ± std. Wilcoxon signed-rank vs the best baseline with Cliff's delta. Ablation table: graph features only / history only / change only / all. Learning curve: performance vs training-set size (justifies the dataset's value — "more data helps" is a strong argument for the dataset's existence).

### 12.7 Phase 4 exit criteria `[v1]`

- [ ] Model beats best baseline on Recall@20%, within-project, *p* < 0.05, non-negligible effect size
- [ ] Cross-project numbers reported honestly, however bad
- [ ] Ablation table complete
- [ ] SHAP explanations generated for the demo

### 12.8 Phase 4 Expansion

**T4.6 — Calibration analysis** *(~3 hrs)* `[v2 B.1, G.8]`
Reframe the output from a **set** to a **calibrated risk score**: P(this change breaks at least one test), plus a ranked per-test probability. This unlocks three things nobody in the CIA/RTS literature reports:

- **Calibration** — reliability diagram, Brier score, expected calibration error. Nobody reports these because with set-valued output you cannot. A well-calibrated risk score is a *different and more useful artifact* than a set.
- **A cost-optimal decision rule** — given cost-per-test-minute and cost-per-escaped-regression, the optimal cutoff is *derivable* rather than arbitrary. This turns "top-k tests" into an economics argument, which is what actually persuades practitioners.
- **Selective prediction** — abstain when uncertain and fall back to retest-all. *"Our model runs 12% of the suite on 80% of PRs and defers on the rest"* is a far more deployable claim than a single operating point.

Costs almost nothing — it is a different read of the same model output — and gives §V a distinctive angle. Answers **RQ7**.

**T4.7 — Leakage audit** *(~2 hrs)* `[new]`
Explicit, written audit of every feature against the time split: does any feature use information unavailable at prediction time? The classic offenders are trailing-window statistics computed over the full corpus rather than up to *t*, and the cross feature "failure rate of this test given this file changed". Also check for duplicate-code leakage between train and test repos (Allamanis 2019). Write the audit as a table in `analysis/leakage_audit.py` output; a reviewer who suspects leakage and finds a written audit is disarmed.

**T4.8 — Two prediction heads** *(~2 hrs)* `[new]`
Train and report the **file-level impact head** alongside the test-level head (§18.8, §21.4). The abstract promised both; the CIA literature is comparable only on the file-level one. Small extra cost, large gain in comparability to Borg / Huang / Dai / Gupta & Gupta.

---

## 13. Phase 5 — Tool & Web Demo

**Status: Oct 12–Nov 2 · Duration 3 weeks · Owner: Prisha (lead) · Backup: Deepanshu** `[v1, owner_backup new]`

The Zeroth Review promised "an interactive dependency graph, enabling developers to better understand the consequences of their changes." Deliver it — it satisfies the course requirement, it is a Data & Tool Showcase asset, and reviewers on that track explicitly evaluate whether they can install and run the thing.

### 13.1 T5.1 — `blastradius` CLI *(~5 hrs)* `[v1]`

```
blastradius init                       # build graph for current repo
blastradius predict --base main        # rank tests for the working diff
blastradius predict --pr 1234          # rank tests for a GitHub PR
blastradius explain <test_id>          # why this test was ranked high (SHAP + graph path)
blastradius serve                      # start local API + UI
```
Typer for the CLI, Rich for output. Ship as a PyPI package (`pip install blastradius`) — installability is a scored criterion on the Data & Tool track.

`[new]` Add `blastradius gaps` — the test-gap query from T3.13. One extra subcommand, and it is the most developer-useful thing in the tool.

### 13.2 T5.2 — FastAPI service *(~4 hrs)* `[v1]`

`POST /predict` (repo, base_sha, head_sha, changed_files) → ranked tests with scores and explanations. `GET /graph/{repo}/{sha}` → node-link JSON for the UI. `GET /health`. OpenAPI docs auto-generated. Cache graphs in DuckDB. Full API surface, pagination, and caching design: **§20.2**.

### 13.3 T5.3 — Next.js demo UI *(~10 hrs)* `[v1]`

- Paste a public GitHub PR URL → ranked "blast radius" of tests with confidence scores.
- Interactive force-directed graph — changed nodes red, predicted-affected tests orange, unaffected dimmed. Click a test → highlight the graph path that justifies it.
- "Cost saved" panel: *"run the top 12 of 847 tests to catch 94% of predicted failures."*
- Side-by-side comparison panel: co-change set vs reachability set vs BlastRadius prediction vs ground truth (for instances in BR-Bench) — this makes the paper's core finding **visible and clickable**, which is worth an enormous amount in a demo.
- Deploy on Vercel with a small set of pre-computed example PRs so it works without a backend under load.
- `[v2 A.1]` **Fork Graphify's vis.js view rather than starting from a blank canvas.** `callflow_html.py` / `tree_html.py` already give you an interactive graph, a Mermaid call-flow, and a D3 collapsible tree. Recolour for changed / predicted-affected / actually-failed. Library choice is **D-15**; hairball-avoidance strategy is **§20.3**.

### 13.4 T5.4 — GitHub Action *(~4 hrs)* `[v1]`

`blastradius-action` that comments on a PR with the predicted blast radius. Even if nobody adopts it, it demonstrates real-world integration and takes half a day. Ship it in the marketplace. **It comments; it never blocks a merge** (§4.3 non-goal 7).

### 13.5 T5.5 — MCP server *(~3 hrs, optional)* `[merged v1 + v2 G.9]`

Graphify already ships an MCP server (`serve.py`) exposing `query_graph`, `get_node`, `get_neighbors`, `shortest_path`, `list_prs`, `get_pr_impact`, `triage_prs`, over stdio + HTTP with API-key auth and a stateless mode. **Add one tool: `predict_blast_radius`.** ~40 lines for a Claude-native interface, and a demo that runs *inside* Claude Code — which reviewers and a viva panel find memorable.

### 13.6 T5.6 — Reproducibility package *(~5 hrs)* `[v1]`

- `Dockerfile` + `docker-compose.yml`: one command reproduces every table in the paper from the released Parquet files.
- `make all` target running the full pipeline on a 3-repo mini-corpus in <15 minutes (reviewers will not wait longer).
- `REPRODUCE.md` with exact commands, expected outputs, and runtime estimates.
- Pin every dependency. Record hardware and wall-clock time for each stage.

### 13.7 Phase 5 exit criteria `[v1]`

- [ ] `pip install blastradius && blastradius predict` works on a clean machine
- [ ] Demo deployed and publicly reachable
- [ ] `make all` reproduces at least one paper table end-to-end in <15 min
- [ ] Docker image builds from scratch on a second machine

### 13.8 Phase 5 Expansion

**T5.7 — Explainability contract enforcement** *(~2 hrs)* `[new]`
Every predicted test in the top-k must ship at least one justification: a graph path, a history record, or a convention binding. Predictions with none are marked `unexplained` and **counted**. Report the unexplained fraction — *"X% of our top-20 predictions have no graph justification"* is an honest metric and a genuinely interesting one. Spec: **§20.4**.

**T5.8 — Demo degradation plan** *(~1 hr)* `[new]`
The demo must survive having no backend: pre-computed examples ship as static JSON, the graph renders client-side, and a banner states which mode is active. A demo that 502s during a viva or a reviewer visit is worse than a demo with three canned examples.

---

## 14. Phase 6 — Paper, Artifact, Submission

**Status: Oct 19–Nov 10 · Duration 3 weeks · Owner: all three, Deepanshu integrating** `[v1]`

Use the `research-paper-writing` skill throughout. Its core rules apply directly: one message per paragraph, message stated in the first sentence, reverse-outline every section after drafting, and treat claim–evidence alignment as a hard constraint on the Abstract and Introduction.

### 14.1 The 4-page Data & Tool structure `[v1]`

IEEEtran, 10pt, 4pp + 1pp refs.

| Section | Budget | Content |
| --- | --- | --- |
| Abstract | 150 words | Gap → dataset → scale → one headline number → availability |
| I. Introduction | 0.6 pp | The co-change/reachability/fault-revelation triangle; why the gap matters; contributions as a bulleted list |
| II. Related Datasets | 0.4 pp | RTPTorrent, TravisTorrent, GHALogs, LogChunks, GHA workflow histories, CI-Repair-Bench — a **comparison table** is worth more than prose here |
| III. Dataset Construction | 1.2 pp | Sampling frame, harvest pipeline, parsers, labelling engine, flakiness filters, gold subset. Pipeline figure. |
| IV. Dataset Description | 0.8 pp | Schema table, summary statistics, label-source tiers, per-language breakdown, agreement rate |
| V. Example Use Cases | 0.5 pp | RQ1 divergence teaser + the predictor result, compressed; "future research questions this enables" (an explicitly required element of the CFP) |
| VI. Limitations | 0.3 pp | 90-day window, survivorship, observational labels, language coverage, flakiness residual |
| VII. Availability | 0.2 pp | Zenodo DOI, HuggingFace, GitHub, licences |

The CFP for this track has a literal required-elements list. Write section III/IV against that list line by line: data source, collection methodology and provenance, storage mechanism and schema, prior uses, originality relative to similar datasets, future research questions, possible improvements, limitations. **Missing one is an easy desk-level ding.**

### 14.2 Subtasks `[v1]`

**T6.1 — Story lock & outline** *(~3 hrs)* — one-sentence thesis, contribution bullets, section outline, figure list. Do this *before* writing prose.
**T6.2 — Draft §III–IV** *(~8 hrs)* — methods first; they are the easiest to write and the hardest to fake.
**T6.3 — Draft §I–II** *(~6 hrs)* — introduction last-but-one, once you know what you actually found.
**T6.4 — Abstract** *(~2 hrs)* — write it last. Every claim must map to a number in the paper.
**T6.5 — Claim–evidence audit** *(~3 hrs)* — table of `Claim | Evidence | Status`. Weaken or delete anything marked "needs evidence." Non-negotiable.
**T6.6 — Adversarial self-review** *(~4 hrs)* — five dimensions: contribution, clarity, experimental strength, evaluation completeness, method soundness. Each team member reviews as a hostile reviewer independently, then merge.
**T6.7 — Artifact freeze** *(~4 hrs)* — Zenodo DOI minted, HuggingFace public, GitHub release tagged, `CITATION.cff`, all links in the paper resolve.
**T6.8 — Submission mechanics** *(~2 hrs)* — IEEEtran `\documentclass[10pt,conference]{IEEEtran}` (no `compsoc`), page count verified, ORCIDs for all three authors, **AI-usage disclosure in Acknowledgements**, HotCRP submission at `msr2027-data-tool.hotcrp.com`, abstract in by **5 Nov**, paper by **10 Nov**.

### 14.3 Also produce (course deliverables) `[v1]`

- [ ] First Review / Second Review presentation decks — reuse paper figures
- [ ] Final project report in the VIT-mandated format
- [ ] Working demo for the viva
- [ ] arXiv preprint after submission (single-anonymous track, so no title-masking needed — but confirm before posting)

### 14.4 Phase 6 Expansion

**T6.9 — Upstream contribution to Graphify** *(~4 hrs, November, after submission)* `[v2 A.3, G.12]`
Once `test_nodes.py` and `TestResolver` are stable, open a PR against `safishamsi/graphify` adding test-node typing as an optional resolver. Their CONTRIBUTING explicitly invites language-extractor contributions with a fixture plus a test in `tests/test_languages.py`.

Worth an afternoon because: a merged PR into a widely-used repo is a genuine, verifiable line on all three résumés; the paper gets to say the extension was contributed upstream, which is real-world-impact evidence the MSR FOSS Impact Award rewards; it converts a potential *"you just forked someone's tool"* criticism into *"we extended and gave back"*; and the maintainer becomes someone who has heard of the work before the paper appears. **Do it in November, after submission**, so it cannot leak identity during review.

**T6.10 — The economics subsection** *(~4 hrs)* `[v2 B.7]`
One short subsection with real numbers computed from data already held: CI minutes consumed by the corpus in the observation window (from `run_started_at` and job durations); minutes saved at the model's operating point; extrapolated cost at GitHub-hosted-runner list price; estimated CO₂ using a published grid-intensity figure for the runner region. Practitioners and reviewers both respond to this, it takes an afternoon, and sustainability framing is increasingly welcome at MSR. **Present it as an estimate with stated assumptions, not a measurement.**

**T6.11 — VIT final report as the overflow buffer** *(~6 hrs)* `[v2 Part E]`
The VIT report format wants far more length than a 4-page paper. Write the paper tight and let the report absorb the overflow: extended related work, full baseline descriptions, all ablations, the qualitative taxonomy, the complete schema, the threat register. Nothing is wasted, and the report becomes the thing you hand a future student who continues the work.

**T6.12 — Pre-registration of the analysis plan** *(~1 hr)* `[new]`
Before running the final analyses, commit the RQ list, metric definitions, split boundaries, and significance procedure to a dated file in the repo. It costs an hour and it is the cleanest possible answer to "did you go fishing for a *p*-value?" It also stops the team from quietly redefining the headline metric in week 12.

---

# Part IV — The Graph Layer, Specified to Implementation Depth

`[new]` unless otherwise tagged. This part exists because the code graph is the technical core of BlastRadius and was the most under-specified area of both source roadmaps. **An engineer should be able to build from this without asking follow-up questions.** Where it expands a v1 or v2 item, the tag says so.

**Reading order:** §16.1 first (what we are building and why), then §15 (how source becomes nodes), then §17 (what we knowingly get wrong), then §18 (how a diff becomes a ranked list), then §19–§20 (making it fast and making it visible).

---

## 15. Ingestion & Parsing

### 15.1 Repository selection, cloning & local corpus management `[merged]`

Selection criteria live in §23 (they are a research-design question, not an engineering one). This section covers what happens to a repository *after* it is selected.

**Clone strategy.** Use `git clone --mirror` into `corpus/{owner}__{repo}.git`, never a working clone. A mirror is bare, holds all refs, and is roughly half the disk of a working clone. Working trees are then created on demand with `git worktree add --detach`, which is the mechanism the commit-pinned builder needs anyway (§19.1).

```
corpus/
  apache__commons-lang.git/        # bare mirror, the only thing that is fetched
  worktrees/                       # ephemeral, pooled, cleaned after each build
    apache__commons-lang/{sha}/
```

**Refresh policy.** `git remote update --prune` nightly, alongside the harvester. The mirror must contain every SHA the harvester has seen; a run whose head SHA is missing from the mirror (force-push, deleted branch) is recorded as `sha_unavailable` and excluded, with the count reported. This is a real and under-reported source of attrition in PR-mining studies.

**Disk budget.** Assume a mean mirror of ~200 MB and a p95 of ~1 GB. 300 candidates → ~60–120 GB for mirrors, on top of the 200–500 GB for raw logs (§30.1). Prune mirrors for repos dropped from the frame, but **record the drop reason before deleting** — the attrition table in §23.3 depends on it.

**Skip on ingest, not on analysis.** Refuse at clone time any repo with: total size > 5 GB, Git LFS pointers in source directories, >20k source files, or a shallow/incomplete history. Cheaper to reject early than to discover a 40-minute graph build in week 6 (**T15**).

**Submodules.** Do not initialise them. Submodule contents are a different repository with a different history, and their code would silently enter one repo's graph with no valid commit pinning. Record `has_submodules` as a repo attribute and treat unresolved submodule paths as external (§15.5).

**Security posture** `[v2 A.1]`: you are about to clone and parse 300 repositories you did not write. Adversarial filenames, control characters in identifiers, path-traversal in generated file names, and XML-entity bombs are real. **Keep all of Graphify's `security.py`** — `validate_url`, `safe_fetch` with size caps and timeouts, `validate_graph_path` (path-traversal guard), `sanitize_label` (strips control chars, caps at 256, HTML-escapes), SSRF protection. Their `.csproj`/XAML extractors already pre-screen `DOCTYPE`/`ENTITY` for XML DoS. Cite this in the paper's ethics/threats section; "we inherited a hardened extractor" is a better answer than "we didn't think about it."

### 15.2 Language scope — the decision and its defence `[merged v1 T4 + new]`

**Decision: Java and Python. TypeScript is a stretch that will most likely be cut.** Recorded as **D-03**.

The merge brief asks for single-language depth versus multi-language breadth to be picked and defended. This is the defence, and it rests on three arguments rather than one:

**1. Baseline comparability requires Java.** Ekstazi, STARTS, HyRTS, and RTPTorrent are all Java. A paper about change-impact prediction that cannot be compared against the RTS state of the art will be asked why, and the answer "we chose Python" is not survivable. Java is not optional.

**2. Corpus scale requires Python.** Python has the largest population of GitHub Actions repositories with parseable test output, and it is by far the cheapest ecosystem to re-execute in Docker for the gold subset (§9.5) — `pip install -r requirements.txt` versus resolving a Maven dependency tree at a two-year-old commit.

**3. The pair is itself a research variable, which single-language depth would forfeit.** Java is statically typed with resolvable FQNs; Python is duck-typed with name-based resolution. Graph precision should therefore differ systematically between them, and *that difference is measurable against the same CI ground truth*. Every headline metric is reported stratified by language, which turns **T16** (dynamic-language imprecision) from a defect into a finding, and it is the cheapest available approach to **RQ5**'s question about how much graph precision buys you.

**Why not three languages.** TypeScript adds a "multi-paradigm" claim and a third parser, a third test-ID canonicalisation, a third build-system story, and a third re-execution environment — for no additional baseline comparability and no new research variable. It is the first thing to cut and cutting it costs nothing but a sentence in Limitations.

**Why not one language.** A single-language dataset is what RTPTorrent already is. Multi-language is a stated differentiator in §2.1 and it is cheap at two, because tree-sitter makes the *parsing* nearly free — the cost is in test-ID normalisation and re-execution, and two is affordable.

**The pipeline is language-pluggable.** Adding a language is one extractor plus one test-ID rule plus one log parser. Say this in the paper; it converts "only two languages" from a limitation into an extension point.

### 15.3 Parser strategy — tree-sitter vs native frontends vs LSP/SCIP `[new]`

This is the most consequential engineering decision in Part IV, and the merge brief asks for a recommendation with tradeoffs. Here is the comparison, scored for *this* project's constraints: thousands of graphs at arbitrary historical commits, across 300 untrusted repositories, on laptops.

| Approach | Precision | Needs a successful build? | Speed (2k-file repo) | Multi-language | Maintenance cost | Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| **tree-sitter** (via Graphify) | Syntactic; name-based symbol resolution; misses dynamic dispatch and reflection | **No** | Seconds | 36 grammars, one interface | Low — inherited | ✅ **Primary spine** |
| **Eclipse JDT** (Java) | High — full type binding when the classpath resolves | Effectively yes (needs classpath) | Tens of seconds | Java only | Medium; JVM in the loop | ❌ v1 |
| **javalang** (Java, pure Python) | Syntactic only; no type resolution | No | Seconds | Java only | Low | ⚠️ Retained as a *complexity-metric* helper only (T2.4), not as a graph source |
| **Python `ast`** | Syntactic; stdlib, exact for one file | No | Fast | Python only | Low | ⚠️ Fallback when a tree-sitter grammar version fails |
| **Soot / WALA / Doop** | Very high — call graphs with points-to, CHA/RTA/VTA | **Yes — bytecode required** | Minutes to hours | JVM only | High | ❌ v1; documented upgrade path (§44) |
| **LSP-based extraction** | High — the language server does resolution | Usually yes (server wants a configured project) | Slow; per-file round trips; stateful server | Per-language servers | High — server lifecycle at scale is miserable | ❌ |
| **SCIP** (`scip-java`, `scip-python`) | **Compiler-accurate** symbol graph | **Yes** for `scip-java`; partial for `scip-python` | Minutes per commit | Growing set | Medium — Graphify has `scip_ingest.py` already | ✅ **Optional precision tier on the reproducible-build Java subset** (T2.6, RQ5) |

**Recommendation.** tree-sitter as the universal spine for every repository at every commit; SCIP as an optional high-precision tier on the Java subset where a build is reproducible.

**The reasoning is one constraint, and it is worth stating in the paper because it explains a gap in the literature.** Every high-precision analysis in the list requires a *successful build at the commit under analysis*. We need graphs at thousands of historical commits across hundreds of repositories we do not control, whose dependencies may no longer resolve. Requiring a build would collapse the corpus to the small subset that still compiles — which is precisely why the precise tools (Soot, WALA, JDT) have never been applied at mining-study scale, and precisely why the RTS literature is confined to a handful of well-behaved Java projects. **Build-independence is what buys the scale that makes the dataset a contribution.** We pay for it in precision, we measure what we paid (§17.7, T2.8), and RQ5 quantifies the exchange rate on the subset where both are possible.

**Grammar pinning is not optional.** tree-sitter grammars change their node-type names between versions; an unpinned grammar silently changes your graph. Pin every grammar in `pyproject.toml`, record versions in `ENVIRONMENT.md`, and treat a grammar bump as a full corpus rebuild (**T7**).

### 15.4 Build systems, monorepos, and resolving imports without a build `[new]`

Since we never build, every import must be resolved from source. Three mechanisms, in order of application:

**1. Source-root inference.** Detect roots before extraction and record them as repo metadata:

| Ecosystem | Main roots | Test roots | Signal |
| --- | --- | --- | --- |
| Maven | `src/main/java`, `src/main/resources` | `src/test/java` | `pom.xml` present, or the layout itself |
| Gradle | same, plus `src/{sourceSet}/java` | `src/test/java`, `src/integrationTest/java` | `build.gradle{,.kts}` |
| Python (src-layout) | `src/{pkg}` | `tests/` | `pyproject.toml` `[tool.setuptools]`, `src/` with `__init__.py` |
| Python (flat) | `{pkg}/` | `tests/`, `test/`, `*_test.py` alongside | `setup.py`, `setup.cfg`, `tox.ini` |

Record `source_roots` and `test_roots` per repo per SHA. A wrong source root silently breaks every Java FQN, so log the inference and eyeball it for the top 50 repos (T0.1 subtask 5 already budgets that half hour).

**2. Manifest ingestion** `[v2 A.1]`. Graphify's `manifest_ingest.py` parses `pyproject.toml`, `go.mod`, and `pom.xml` into canonical package nodes with `depends_on` edges and one hub node per package. This gives the package layer (§16.2) for free and makes dependency-bump PRs analysable (**RQ10**).

**3. Language-specific resolution rules.**

*Java:* the FQN is derivable from `package` declaration + class name without a classpath. Within-repo `import` statements resolve by FQN lookup against the node index. `import` of a package absent from the index → external, emit an `external_dep` node keyed by the package prefix, do not traverse. Wildcard imports (`import com.foo.*`) resolve to *all* in-repo classes under that package, tagged `INFERRED` at reduced confidence.

*Python:* resolve `import x.y.z` and `from x.y import z` against the directory tree relative to each source root, honouring `__init__.py` for packages and namespace packages without them. Relative imports (`from ..mod import f`) resolve against the module's own path. Anything unresolvable is external. **`conftest.py` is special-cased**: pytest fixtures defined in a `conftest.py` are implicitly available to every test below it in the tree, so emit `configured_by` edges from every test node to each `conftest.py` on its ancestor path. This is the single highest-yield framework-implicit edge in the Python subset and it is nearly free.

**Monorepos.** Detect via multiple manifests in distinct subtrees (>1 `pom.xml` in non-nested directories, or a Gradle settings file declaring multiple `include`s, or multiple `pyproject.toml`). Policy is **D-13**: exclude from the v1 frame, count and report the exclusion. The alternative — one graph per module with cross-module edges through package nodes — is correct and is the documented upgrade path (§44), but it multiplies the graph-versioning problem by the number of modules and is not a week that exists in this timeline.

### 15.5 Policy for unparseable, generated, vendored, and third-party code `[new]`

Excluded from extraction entirely, by path glob, before parsing:

```
**/node_modules/**  **/vendor/**  **/third_party/**  **/.venv/**  **/site-packages/**
**/target/**  **/build/**  **/dist/**  **/out/**  **/bin/**  **/__pycache__/**
**/*.min.js  **/*.bundle.js  **/*_pb2.py  **/*_pb2_grpc.py  **/*.pb.go
**/generated/**  **/gen/**  **/.git/**
```

Additional content-level exclusions applied after reading the first 4 KB of a file: any file containing a `@generated` marker, a `Code generated by ... DO NOT EDIT` header, or a single line longer than 5,000 characters (minified or serialised).

| Category | Policy | Rationale | Recorded as |
| --- | --- | --- | --- |
| **Unparseable** (grammar error) | Skip the file, keep a `file` node with `parse_status=failed`, no symbol nodes | The file still exists and can still be *changed*; dropping it entirely would make changed-file → graph mapping fail silently | `parse_failures` per (repo, sha) |
| **Generated** | Exclude from extraction; keep the `file` node | Generated code changes en masse and would swamp the change set; the *generator* is the real change | `is_generated` on the file node |
| **Vendored / third-party in-tree** | Exclude from extraction; emit one `external_dep` node per vendored package | It is someone else's code that we cannot version-pin; edges into it are not actionable impact | `is_vendored` |
| **External dependency** (not in tree) | `external_dep` node, terminal — never traversed | Traversing into dependencies is the cross-repo problem (§44) | `depends_on` edge from package node |
| **Binary / data / docs** | No node at all beyond a `file` node if it is in the change set | Cannot produce symbols | — |

**The parse-failure budget is a gate, not a metric.** A repo whose parse-failure rate exceeds **20%** at any harvested SHA is dropped from the frame with the reason recorded (v1 T2.2 subtask 5). Report the mean and distribution of parse-failure rate in the paper — reviewers of graph-based work ask, and having the number ready is worth more than the number itself being low.

---

## 16. Graph Schema

### 16.1 What we are building — and why not the alternatives `[new]` — see **D-05**

**BlastRadius builds a multi-layer typed property graph over source-derived symbols. It is not a program dependence graph and not a code property graph.**

Five layers, all in one NetworkX `MultiDiGraph` per `(repo, sha)`:

| Layer | Contains | Built by | Confidence |
| --- | --- | --- | --- |
| **L1 Structural** | repo / module / package / file / class / method containment | tree-sitter AST, deterministic | `EXTRACTED` |
| **L2 Symbolic** | imports, calls, inherits, implements, overrides, instantiates | tree-sitter + Graphify symbol resolvers | `EXTRACTED` / `INFERRED` |
| **L3 Test** | test nodes, `tests` / `tests_by_convention` / `tests_by_layout` bindings | `TestResolver` plugin (§29.6) | tiered 1.0 / 0.85 / 0.65 |
| **L4 Historical** | `co_changed_with`, `co_fails`, churn, age, failure rates | PyDriller + BR-Bench labels | weighted, never 1.0 |
| **L5 Configuration** | package nodes, `depends_on`, `configured_by`, CI-job nodes | `manifest_ingest.py` + workflow parsing | `EXTRACTED` |

**Why this and not a PDG.** A program dependence graph (Ferrante, Ottenstein & Warren, TOPLAS 1987) encodes intra-procedural control and data dependence; an SDG (Horwitz, Reps & Binkley, TOPLAS 1990) extends it inter-procedurally to support precise slicing. Both require data-flow analysis, which requires resolved types, which requires a build (§15.3) — and produce a graph roughly an order of magnitude larger per unit of source. We need thousands of graphs at historical commits and a per-instance query budget under 100 ms. Slicing precision is the wrong thing to buy with that budget: we are producing a **ranked shortlist a human will read**, and the marginal ranking gain from statement-level data flow over method-level reachability is small compared to the marginal gain from the historical layer, which costs almost nothing.

**Why not a full Code Property Graph.** A CPG (Yamaguchi et al., IEEE S&P 2014) merges AST, CFG, and PDG for vulnerability discovery, where you must reason about *how* data reaches a sink. Change impact does not need that: we need *whether* a change can reach a test, at method granularity, cheaply, at scale. A CPG buys precision we would then throw away when ranking.

**Why layers L4 and L5 exist at all, which no CIA graph formalism includes.** The entire premise of §2 is that syntactic reachability is a poor proxy for fault revelation. A graph that contains *only* syntax cannot express "these two files always break together for reasons the parser cannot see" — and that is exactly the signal the co-change camp has and the reachability camp lacks. Putting both in one graph is what lets one model use both, and it is what makes the RQ1 divergence measurable *inside* a single representation rather than across two incompatible ones.

**The honest one-line description for the paper:** *a method-granular, build-free, typed dependency graph augmented with test bindings and mined historical coupling, versioned per commit.*

### 16.2 Node taxonomy `[merged v1 §31 + new]`

Every node type named in the merge brief appears here. The **Tier** column states what is actually materialised in v1 — nothing is dropped, some things are deferred with a stated trigger.

| Node type | Key properties | Extraction source | Tier | Notes |
| --- | --- | --- | --- | --- |
| `repo` | `owner`, `name`, `lang`, `default_branch`, `frame_version` | frame CSV | **CORE** | One per graph; the graph root |
| `module` | `path`, `manifest_type` | manifest / source-root inference | **CORE** | For Java, a Maven module; for Python, a top-level package |
| `package` | `coordinates`, `version`, `is_external` | `manifest_ingest.py` | **CORE** | Both in-tree packages and external deps (`is_external=true`, terminal) |
| `file` | `path`, `loc`, `lang`, `parse_status`, `is_generated`, `is_vendored`, `content_sha` | file walk | **CORE** | Exists even when parsing failed — the changed-file join needs it |
| `class` | `fqn`, `is_abstract`, `is_interface`, `visibility`, `start_line`, `end_line` | AST | **CORE** | |
| `interface` | as `class` with `is_interface=true` | AST | **CORE** | Modelled as a `class` variant rather than a separate label, to keep traversal simple |
| `method` | `fqn`, `signature`, `arity`, `is_static`, `is_abstract`, `body_sha`, `start_line`, `end_line`, `complexity` | AST | **CORE** | `body_sha` is what makes body-vs-signature change detection cheap (§18.2) |
| `function` | as `method`, no owning class | AST | **CORE** | Python/TS module-level functions |
| `field` | `fqn`, `type_name`, `is_static`, `is_final` | AST | **v1.5** | Materialised only where `reads_field`/`writes_field` are enabled; see below |
| `parameter` | `name`, `type_name`, `position` | AST | **DEFERRED** | Stored as a `signature` string property on `method` rather than as nodes. Trigger to materialise: if signature-change propagation (§18.2) proves too coarse in the RQ8 taxonomy |
| `test_method` | `test_id`, `framework`, `binding_strategy`, `is_parameterised` | `TestResolver` | **CORE** ⭐ | The join key to CI outcomes. This is the project |
| `test_suite` | `test_id_prefix`, `n_tests` | `TestResolver` | **CORE** | The class or module containing tests; needed because some log formats only report at class granularity |
| `ci_job` | `workflow_id`, `job_name`, `matrix_leg` | workflow YAML + run metadata | **v1.5** | Lets the graph express "this test only runs on this job", which matters for matrix builds (**T9**) |
| `commit` | `sha`, `author_hash`, `ts` | Git | **DEFERRED — deliberately** | Commits are *not* nodes in the code graph. They are the graph's version key, and history lives in `co_changed_with` edge weights. Making commits nodes turns one graph per SHA into one enormous temporal graph and breaks the incremental build model. Trigger to revisit: only if temporal GNN work is attempted (§44) |
| `config_key` | `file`, `key_path`, `value_hash` | YAML/TOML/properties parse | **v1.5** | Config-driven behaviour is a known proxy-failure category (RQ8); a config *key* node is what lets `configured_by` point somewhere specific |
| `resource` | `path`, `kind` | file walk | **v1.5** | Test fixtures, golden files, SQL migrations. Cheap and surprisingly predictive — a changed golden file breaks exactly the tests that read it |
| `external_dep` | `coordinates`, `ecosystem` | manifest + unresolved imports | **CORE** | Terminal; never traversed into |

**Tier semantics.** **CORE** ships in Phase 2 and is required for the Phase 3 baselines. **v1.5** is built if Phase 2 exits early or during the Phase 3 slack; each is independently useful and independently cuttable. **DEFERRED** is not built, with the trigger recorded above.

### 16.3 Edge taxonomy `[merged v1 §31 + new]`

Every edge type named in the merge brief appears here.

| Edge | Direction | Confidence | Tier | Extraction mechanism | Cost |
| --- | --- | --- | --- | --- | --- |
| `contains` | parent → child | `EXTRACTED` 1.0 | **CORE** | AST nesting | Free |
| `imports` | file → file/package | `EXTRACTED` 1.0 / `INFERRED` on wildcards | **CORE** | Import statements + §15.4 resolution | Cheap |
| `calls` | method → method | `INFERRED` 0.5–1.0 | **CORE** | Graphify's call-graph second pass; name + arity matching | Moderate — the expensive pass |
| `inherits` | class → superclass | `EXTRACTED` 1.0 | **CORE** | `extends` / base-class list |  Cheap |
| `implements` | class → interface | `EXTRACTED` 1.0 | **CORE** | `implements` clause | Cheap |
| `overrides` | method → method | `INFERRED` 0.9 | **CORE** | Signature match up the `inherits`/`implements` chain | Cheap given the above |
| `instantiates` | method → class | `INFERRED` 0.8 | **CORE** | `new X()` / `X(...)` where `X` resolves to an in-repo class | Cheap |
| `reads_field` | method → field | `INFERRED` 0.7 | **v1.5** | Identifier resolution against the enclosing class's field table | Moderate |
| `writes_field` | method → field | `INFERRED` 0.7 | **v1.5** | Assignment targets | Moderate |
| `throws` | method → class | `EXTRACTED` 1.0 (Java declared) / `INFERRED` 0.6 (raise sites) | **v1.5** | `throws` clause; `raise X` | Cheap |
| `tests` | test_method → method/class | `EXTRACTED` 1.0 | **CORE** ⭐ | The test node has a `calls`/`imports` edge to the subject | Free — derived |
| `tests_by_convention` | test_method → class | `INFERRED` 0.85 | **CORE** ⭐ | `FooTest → Foo`, `test_bar.py → bar.py`, `Baz.spec.ts → Baz.ts` | Free |
| `tests_by_layout` | test_method → class | `INFERRED` 0.65 | **CORE** ⭐ | `src/test/java/com/x/FooTest.java ↔ src/main/java/com/x/Foo.java` | Free |
| `co_changed_with` | file ↔ file (undirected, weighted) | weighted by confidence/lift | **CORE** | PyDriller mining, trailing window (T1.4) | Moderate, computed once per repo-window |
| `co_fails` | test ↔ test (undirected, weighted) | weighted | **CORE** | BR-Bench outcome history | Cheap |
| `covered_by` | method → test_method | `EXTRACTED` 1.0 | **DEFERRED** | Requires real coverage instrumentation | **Only available on the gold subset**, where the suite is executed anyway. Trigger: if binding rate (**T8**) falls below 70% and needs a ground-truth anchor to diagnose |
| `configured_by` | node → config_key / file | `INFERRED` 0.5 | **v1.5** | `conftest.py` ancestry (Python, high yield), annotations, workflow YAML | Cheap for `conftest.py`, moderate otherwise |
| `depends_on` | package → package | `EXTRACTED` 1.0 | **CORE** | `manifest_ingest.py` | Free |
| `wires` | class → class | `INFERRED` 0.4 | **DEFERRED** | DI/IoC annotation analysis (§17.4) | Trigger: if the RQ8 taxonomy shows DI as a top-3 proxy-failure category |
| `runs_in` | test_method → ci_job | `INFERRED` 0.8 | **v1.5** | Workflow YAML + observed outcomes | Needed for matrix-build reasoning |

**Note on `covered_by`.** The merge brief lists it in the edge taxonomy. It is the *most* precise test-binding edge possible and we cannot have it at corpus scale, because obtaining it means running the suite under a coverage agent at every commit — which is exactly the cost that makes dynamic RTS impractical (Law & Rothermel 2003; Apiwattanapong et al. 2005). We get it *for free* on the ~300–500 gold-subset instances because the suite is already being executed there. **That makes it a validation instrument rather than a feature:** measure how well `tests` / `tests_by_convention` / `tests_by_layout` approximate true coverage on the gold subset, and report the three precision numbers. That is a small, novel, cheap result and it directly defends the binding strategy.

### 16.4 Property schema: materialised vs computed at query time `[new]`

| Quantity | Materialised | Computed at query | Cache | Why |
| --- | --- | --- | --- | --- |
| Node type, fqn, path, LOC, line ranges | ✅ per (repo, sha) | — | Parquet | Cheap, needed by everything |
| `body_sha`, `content_sha` | ✅ | — | Parquet | Drives incremental invalidation |
| Degree (in/out, per edge type) | ✅ | — | Parquet | O(E) once, O(1) forever |
| Leiden `community_id` | ✅ | — | Parquet | Expensive; recomputed only when >5% of nodes change (§19.1) |
| PageRank, betweenness | ✅ PageRank; ⚠️ betweenness sampled | — | Parquet | Exact betweenness is O(VE) — use *k*=200 pivot sampling and say so |
| Churn, age, author count, historical failure rate | ✅ per (repo, sha, window) | — | Parquet | Comes from Git/BR-Bench, not the graph |
| **Shortest path test→changed set** | ❌ | ✅ | **DuckDB, keyed `(repo, sha, changed_set_hash)`** | Depends on the *change*, which is per-instance. This is the hot path |
| *k*-hop neighbourhood | ❌ | ✅ | same | same |
| `same_community` indicator | ❌ | ✅ | trivial from materialised `community_id` | |
| Impact score | ❌ | ✅ | same | Depends on model weights, which change |
| Justification paths | ❌ | ✅ (top-*k* only) | not cached | Only ever computed for the tests actually shown |

**The one rule that determines pipeline runtime:** anything that depends only on `(repo, sha)` is materialised once; anything that depends on the changed set is computed per instance and cached on `changed_set_hash`. Getting this backwards is what turns an hour into a week (v1 T2.5).

### 16.5 Node identity across renames, moves, and refactors `[new]`

This is the hardest schema problem in the project, because graph nodes must be comparable across commits for the historical layer and for incremental builds, while source files move constantly.

**The ID recipe.**

```
symbol node:  {repo}::{lang}::{kind}::{normalized_fqn}[#{arity}]
file node:    {repo}::file::{normalized_path}
package node: {repo}::pkg::{ecosystem}::{coordinates}
test node:    {repo}::test::{canonical_test_id}
```

`normalized_fqn` and `normalized_path` both go through **Graphify's `ids.py` NFKC + casefold recipe**, which is cross-platform stable and already has a contract test (`test_id_normalization_contract.py`) — inherit it rather than writing a second normalizer (**D-09**). `_file_node_id` additionally qualifies a stem with parent-directory context to prevent collisions; keep that behaviour.

**What survives what:**

| Refactor | Symbol ID stable? | File ID stable? | Handling |
| --- | --- | --- | --- |
| Method body edited | ✅ | ✅ | `body_sha` changes; that *is* the change signal |
| Method renamed | ❌ | ✅ | Treated as delete + add. Seed the *callers* of the deleted symbol (§18.3) |
| Class moved between packages | ❌ (FQN changes) | ❌ | `identity_map` link, below |
| File moved, contents unchanged | ✅ for Python module-path-free symbols; ❌ for Java (package changes) | ❌ | `identity_map` link |
| Signature changed (param added) | ❌ if arity is in the ID | ✅ | **Deliberate.** A signature change *should* look like a new symbol — it breaks callers, which is exactly the propagation we want (§18.2) |
| Reformatting only | ✅ | ✅ | `body_sha` computed on a normalised token stream, not raw text, so formatting does not register as a change |

**The `identity_map`.** Node IDs are stable *by construction* only under body edits. For everything else, maintain `data/processed/identity_map.parquet`:

```
repo, from_sha, to_sha, old_node_id, new_node_id, kind {renamed|moved|split|merged}, confidence, evidence
```

Populated by two mechanisms, in order:
1. **Git rename detection.** `git diff --find-renames=50% --find-copies` between consecutive analysed SHAs gives file-level renames with a similarity score. Java symbol IDs are then remapped by substituting the package prefix.
2. **Body-hash matching.** For symbols whose ID vanished at `to_sha` and appeared at `to_sha` with an identical `body_sha` (or a MinHash similarity above 0.8 on the token stream), emit a `renamed`/`moved` link. Graphify's `dedup.py` (MinHash/LSH + Jaro-Winkler with a same-file partition constraint) is the right machinery here — take it rather than writing a matcher.

**The accepted failure mode, stated plainly:** a method that is renamed *and* substantially rewritten in the same commit will be recorded as a delete plus an add with no identity link. Its historical attributes (churn, failure history) reset. This is a real and unavoidable limitation of source-level identity tracking; report the rate of unlinked deletions as a data-quality column (`identity_break_rate`) rather than pretending it does not happen. It matters most for the historical features (L4) and barely at all for reachability (L2), which is a useful thing to be able to say when asked.

---

## 17. Hard Problems & Accepted Unsoundness

`[new]` — every static impact analysis is wrong in known ways. The difference between a defensible paper and an indefensible one is whether the wrongness was chosen and measured or discovered by a reviewer.

### 17.1 The stance

BlastRadius is **both unsound and imprecise, on purpose**:

- **Unsound** (misses real edges): reflection, dynamic dispatch through unresolved types, DI wiring, config-driven behaviour, and cross-process boundaries all produce dependencies we do not see.
- **Imprecise** (adds phantom edges): name-and-arity call matching creates edges that do not exist at run time, especially in Python.

RTS tools like Ekstazi and STARTS chase *safety* — the guarantee that no fault-revealing test is excluded (the framework in Rothermel & Harrold, TOSEM 1997). **We explicitly do not.** We produce a ranked shortlist, we measure precision and recall against observed CI outcomes, and we let the model learn how much to trust each edge type. §4.3 non-goal 1 states this; the paper's Limitations section states it again.

**This is the entire reason the dataset is valuable.** You cannot calibrate an unsound analysis without ground truth about what it missed. BR-Bench is that ground truth.

### 17.2 Dynamic dispatch, virtual calls, polymorphism, duck typing

| | Approach | Accepted unsoundness | Measurement |
| --- | --- | --- | --- |
| **Java virtual calls** | Class-hierarchy-style over-approximation (in the spirit of CHA, Dean/Grove/Chambers ECOOP 1995) restricted to types declared **in-repo**: a call to `Base.m()` produces `calls` edges to every in-repo override of `m` found via `inherits`/`implements`, each at reduced confidence `1/n_overrides` | No points-to analysis, so no RTA/VTA narrowing (Bacon & Sweeney OOPSLA 1996). Over-approximates: adds edges to overrides that can never be reached at this call site | Over-approximation raises recall and lowers precision; the trade is visible directly in the RQ1 reachability numbers |
| **Interface dispatch** | Same, via `implements` | An interface with 40 implementers produces 40 low-confidence edges | Cap: if `n_overrides > 20`, emit edges to none and instead mark the call site `dispatch_fanout_high` as a feature. Beyond ~20 the edges are noise and they wreck the distance features |
| **Python duck typing** | Name + arity matching within the resolved import closure of the calling module | Phantom edges when two unrelated classes share a method name. **This is the dominant precision loss in the Python subset** (**T16**) | T2.8 phantom-edge rate, hand-checked on 100 sampled call edges per language, reported in the paper |
| **Python dynamic attributes** | Not resolved | `getattr(obj, name)()` is invisible | Flagged as a dynamic boundary (§17.3) |

**Why over-approximation is the right default here.** Recall failures are invisible to the model — a missing edge means the feature is silently wrong. Precision failures are visible: the model learns to discount low-confidence edge types, because the confidence is a feature. Bias toward including the edge with honest confidence rather than excluding it.

### 17.3 Reflection, `eval`, dynamic imports, service locators

**We make no attempt to resolve them.** Sound reflection analysis is a research area of its own (Livshits, Whaley & Lam, APLAS 2005) and it needs points-to information we do not have.

Instead, **mark the boundary and make it a feature.** During extraction, flag any file containing:

```
Java:   Class.forName  .getMethod(  .getDeclaredMethod(  .newInstance(  ServiceLoader
        @Autowired  @Inject  @Bean  @Component  @Value  Proxy.newProxyInstance
Python: getattr(  setattr(  importlib  __import__  eval(  exec(  globals()[
        locals()[  type(  metaclass=  __getattr__  pkgutil  entry_points
```

Emit `has_dynamic_boundary=true` on the file node and `n_dynamic_sites` as a count. Derived features (§12.2): `changed_file_has_dynamic_boundary`, `test_reaches_dynamic_boundary`, `n_dynamic_sites_on_shortest_path`.

Three things this buys, all cheap:
1. The model can learn *"when a change touches reflective code, distrust the graph distance"* — which is precisely the correct behaviour.
2. It is a ready-made category in the RQ8 qualitative taxonomy, and one of the categories most likely to be top-3.
3. It is an honest, quantified answer to the reviewer question "what about reflection?" — *"present in X% of changed files; we flag it, we do not resolve it, and here is how much it degrades the graph features."*

### 17.4 Dependency injection, IoC, and annotation-driven wiring

Spring, Guice, and Python decorator frameworks create edges no call graph sees: the container wires an interface to an implementation at runtime.

**v1 policy: detect and flag, do not resolve.** Annotations are already parsed for test detection, so the marginal cost is near zero: record annotation names on class and method nodes as a `annotations: list[str]` property.

**The `wires` edge is specified (§16.3) but DEFERRED**, with an explicit trigger: *if the RQ8 taxonomy (T3.10) shows DI/IoC in the top three proxy-failure categories, build it.* A minimal version — `@Component`/`@Service`/`@Repository` classes linked to every `@Autowired` field whose declared type they implement — is perhaps 150 lines and would then be justified by evidence rather than by anticipation. **Not building it now is the decision; the trigger is what makes that decision reversible.**

### 17.5 Framework-implicit edges

Routes, ORM ↔ schema, event handlers, config-driven behaviour. The full space is unbounded — every framework invents new implicit edges. Ranked by yield-per-hour for *this* corpus:

| Implicit edge | Yield | Cost | v1? |
| --- | --- | --- | --- |
| **`conftest.py` → test** (pytest fixtures) | **Very high** — affects most Python test bindings | ~1 hr | ✅ **Build** (§15.4) |
| **JUnit annotations → test typing** (`@Test`, `@ParameterizedTest`, `@BeforeEach`) | **Very high** — required for test detection anyway | included in `TestResolver` | ✅ **Build** |
| Test resource/fixture files → test (`src/test/resources/**`, `tests/data/**` referenced by string literal) | Medium — a changed golden file breaks exactly its readers | ~3 hrs | ⚠️ **v1.5** (`resource` node + `configured_by`) |
| `@ParameterizedTest` / `@pytest.mark.parametrize` data sources | Medium | ~2 hrs | ⚠️ **v1.5** |
| Spring `@RequestMapping` route → handler | Low for test prediction | ~4 hrs | ❌ Deferred |
| ORM entity ↔ migration/schema | Low–medium; migrations do break tests | ~6 hrs | ❌ Deferred; flagged as a taxonomy category instead |
| Event handlers / observers / signals | Low | ~6 hrs | ❌ Deferred |

**The principle:** build the two that are on the critical path for test binding, build the resource layer if Phase 2 exits early, and record the rest as known unsoundness that the RQ8 taxonomy will quantify. A category that shows up in the taxonomy becomes a v2 feature with evidence behind it.

### 17.6 Cross-boundary edges: frontend ↔ API, RPC, message queues

**Out of scope for v1, and the reason is structural, not lazy.** Our unit of analysis is a single repository at a single commit, and our ground truth is that repository's CI outcome. A change in a frontend repo cannot turn a backend repo's tests red *in the observed data*, because they are different pipelines. The question is real and interesting — it is exactly **§44's cross-repo blast radius** — but it requires a different corpus construction (linked repos, coordinated releases) and a different ground truth.

**Partial compensation within a repo:** `co_changed_with` edges (L4) implicitly capture some cross-boundary coupling, because a frontend file and its API handler in the same repo *are* edited together. This is worth noting in the paper: the historical layer partially covers what the syntactic layer structurally cannot, which is a small argument in favour of the hybrid representation.

### 17.7 Precision vs recall, stated as a design position

| | We optimise for | We accept | Because |
| --- | --- | --- | --- |
| Edge extraction | **Recall** | Phantom edges | A missing edge is invisible; a low-confidence edge is a feature |
| Impact propagation | **Precision at the top of the ranking** | Poor recall in the tail | Nobody reads position 400 |
| Test binding | **Recall via three strategies** | Three different confidences | Binding rate below 70% kills the project (**T8**) |
| The final output | **Ranking quality (Recall@k)** | No safety guarantee | We rank; we do not prove (§4.3) |

**Everything in this table is measured against BR-Bench.** That sentence is the answer to most graph-quality objections, and it is only available to us because we built the dataset first.

---

## 18. Diff Mapping & Impact Propagation

### 18.1 Commit/PR diff → AST-level change extraction `[merged v1 T1.2 + new]` — see **D-07**

Line-level diffs are the wrong input: a one-line change inside a method body and a one-line change to its signature have completely different propagation semantics.

**Two tiers, deliberately:**

**Tier 1 — symbol-table differencing (default, corpus-wide).** For each changed file, parse base and head with tree-sitter, build `{symbol_id → (signature, body_sha, start, end, annotations)}` for both, and diff the maps. Cost: two parses per changed file, ~milliseconds. This is what runs on all ~50k instances.

**Tier 2 — tree differencing (gold subset only).** Run **GumTree** (Falleri et al., ASE 2014) or ChangeDistiller-style differencing (Fluri et al., TSE 2007) to get true edit scripts with move and update detection. Cost: seconds to tens of seconds per file, plus a JVM dependency for GumTree.

**Recommendation:** Tier 1 everywhere, Tier 2 on the 300–500 gold instances only, used to **validate that the cheap taxonomy agrees with the true edit script**. Report the agreement rate. This gives a rigorous answer to "you used a heuristic differ" without paying tree-differencing cost across the corpus, and it mirrors exactly the structure used for labels (cheap observational + expensive causal validation, §9.5) — a pattern worth naming in the paper because reviewers recognise consistency of method as a sign of care.

### 18.2 The change taxonomy and its propagation semantics `[new]`

| Change type | Detection (Tier 1) | Propagation semantics | Seed weight |
| --- | --- | --- | --- |
| `added` | symbol in head, not base | Seed the containing class/file; nothing calls it yet | 0.5 |
| `deleted` | symbol in base, not head | **Seed the callers found in the *base* graph** — this is the one case that must read the base graph, not the head | 1.0 |
| `renamed` | body_sha match across a delete/add pair (§16.5) | Treat as `deleted` + `added`; propagate to old callers | 1.0 |
| `moved` | identity_map `moved` link | Imports of the old path break | 0.8 |
| `signature_changed` | same name, different `signature` or arity | **Propagate to all callers at full weight** — this is the highest-yield change type | **1.0** |
| `body_changed` | same signature, different `body_sha` | Propagate to callers with decay | 0.8 |
| `annotation_changed` | `annotations` list differs | Can retype a test or rewire DI; propagate to the containing class | 0.7 |
| `import_changed` | file-level import set differs | Propagate along the new/removed import edge | 0.6 |
| `comment_only` | `body_sha` (token-normalised) identical, raw text differs | **No propagation** | 0.0 |
| `formatting_only` | token stream identical | **No propagation** | 0.0 |
| `is_docs_only` / `is_formatting_only` (file-level) | path/extension + the above | Excluded from main splits, retained as **negative controls** (v1 T1.2) | 0.0 |
| `is_dependency_bump` | manifest-only change, version field differs | Seed the *package* node; propagates via `depends_on` to every importer | 0.9 |
| `touches_ci_config` | `.github/workflows/**`, `tox.ini` | Can change which tests run at all — a distinct failure mode, flag it | 0.5 |
| `touches_build_config` | `pom.xml`, `build.gradle`, `pyproject.toml` | Same | 0.7 |
| `touches_test_file` | path in `test_roots` | The test itself changed; excluded from its own prediction to avoid label leakage | special |

**`touches_test_file` is a leakage trap and deserves a line of its own.** If a PR modifies `FooTest.java` and `FooTest.testBar` then fails, a naive model learns "the test that changed is the test that fails" — which is true, trivial, and useless. **Rule: a test whose own source file is in the changed set is excluded from the candidate set for that instance**, and the exclusion is counted and reported. Getting this wrong inflates every headline number and is exactly what a suspicious reviewer will probe. Covered by the T4.7 leakage audit.

### 18.3 Seed set construction `[new]`

```python
def build_seeds(instance, graph_base, graph_head) -> dict[NodeId, float]:
    seeds = {}
    for ch in instance.changed_symbols:
        if ch.type in ("deleted", "renamed"):
            # callers only exist in the base graph
            for caller in graph_base.predecessors(ch.node_id, edge_types={"calls"}):
                seeds[caller] = max(seeds.get(caller, 0), SEED_W[ch.type])
        else:
            seeds[ch.node_id] = max(seeds.get(ch.node_id, 0), SEED_W[ch.type])
    for f in instance.changed_files:
        if f.parse_status == "failed" or f.symbols_unresolved:
            # fall back to file granularity rather than dropping the change
            seeds[file_node(f.path)] = max(seeds.get(file_node(f.path), 0), 0.6)
    return seeds
```

Three rules that matter:

1. **Graphs are built at the base SHA**, because that is the state the developer changed *from* and the state whose structure explains the propagation. Deleted symbols only exist there.
2. **Never drop a change silently.** If symbol-level extraction fails for a file, fall back to a file-level seed at reduced weight. A dropped change is an instance with no seeds and a guaranteed zero score — invisible in aggregate, catastrophic in the tail.
3. **Seed weights are initial priors, not final constants.** They are the heuristic model's parameters and the learned model's features; §18.5 tunes them on validation data.

### 18.4 Forward and reverse reachability `[new]`

**Direction matters and is easy to get backwards.** To answer "what breaks", we need the things that *depend on* the changed code — the **reverse** direction along `calls` / `imports` / `inherits` — and then the **forward** direction along `tests` bindings.

```
Stage A (reverse):   seeds  ←calls─  ←imports─  ←inherits─  ←instantiates─   dependents, depth ≤ k
Stage B (forward):   dependents  ─tests→  ─tests_by_convention→  ─tests_by_layout→   candidate tests
Stage C (lateral):   seeds  ~co_changed_with~  files  ─contains→ ... ─tests→          historical candidates
```

Algorithm, as implemented in `src/graph/query.py`:

```python
def impacted(graph, seeds, k=4, max_frontier=5000):
    """Reverse-BFS over the inverted dependency subgraph, recording min distance."""
    dist = {n: 0 for n in seeds}
    frontier, depth = set(seeds), 0
    while frontier and depth < k:
        depth += 1
        nxt = set()
        for n in frontier:
            for pred, etype, conf in graph.in_edges(n, types=REVERSE_TYPES):
                if pred not in dist:
                    dist[pred] = depth
                    nxt.add(pred)
        if len(nxt) > max_frontier:            # explosion guard
            nxt = top_by_edge_confidence(nxt, max_frontier)
        frontier = nxt
    return dist
```

**Depth limit `k=4`, and why a limit exists at all.** Transitive closure over a real dependency graph reaches most of the repository within five or six hops — the classic "everything depends on the logger" problem. Past depth 4 the reached set stops discriminating: it is no longer an impact set, it is the repo. Report the **reach curve** (mean fraction of the repo reached at each *k*) as a figure; it is a one-plot justification for the cutoff and it is the kind of empirical detail that makes a methods section credible. Also run *k* ∈ {1,2,3,∞} as separate reachability baselines (T3.3), which means the choice of 4 is defended by data rather than asserted.

**The `max_frontier` guard.** God nodes (Graphify's own term for the highest-centrality nodes) cause frontier explosion. When the frontier exceeds 5,000, keep the highest-confidence-edge subset. Record `frontier_truncated=true` on the instance — a truncated instance is a legitimate data point, but it should be identifiable in the analysis.

### 18.5 Impact scoring `[new]`

The heuristic scorer, which is both the standalone tool's fallback (it works on a repo with no history) and a Phase 3 baseline:

$$
\text{score}(t) \;=\; \underbrace{\max_{n \in \text{deps}(t)} \Big[\gamma^{\,d(n)} \cdot w_{\text{edge}}(n \to t) \cdot c_{\text{bind}}(n \to t)\Big]}_{\text{structural}} \;+\; \beta \cdot \underbrace{h(t)}_{\text{history}} \;+\; \alpha \cdot \underbrace{\text{comm}(t)}_{\text{community}}
$$

| Term | Meaning | Default |
| --- | --- | --- |
| $d(n)$ | reverse-BFS distance from the seed set to dependency $n$ | from §18.4 |
| $\gamma$ | distance decay | **0.6** |
| $w_{\text{edge}}$ | edge-type weight: `calls` 1.0, `imports` 0.7, `inherits` 0.9, `instantiates` 0.6, `co_changed_with` scaled by lift | |
| $c_{\text{bind}}$ | binding confidence: `tests` 1.0, `tests_by_convention` 0.85, `tests_by_layout` 0.65 | |
| $h(t)$ | trailing-90d failure rate of test $t$, plus `co_fails` mass with already-high-scoring tests | |
| $\beta$ | history weight | **0.3** |
| $\text{comm}(t)$ | 1 if $t$'s Leiden community intersects the touched communities | |
| $\alpha$ | community weight | **0.1** |

**Use `max` over paths, not `sum`.** Summing rewards a test with many weak paths over a test with one strong direct call, which is backwards — and it makes the score scale with repository size, which destroys cross-repo comparability.

**Tune $\gamma, \beta, \alpha$ on the validation split only** (§32), and report the tuned values. In Phase 4 these become features and LightGBM learns the weighting; the heuristic version survives as `BLASTRADIUS-HEURISTIC`, a baseline that answers "how much of your result comes from the learned model versus from the graph?" — a question every reviewer of an ML4SE paper asks.

### 18.6 Historical evidence fusion `[merged v1 T1.4/T2.4 + new]`

Static reachability and mined history are two independent signals about the same question, and combining them is the point of the L4 layer.

**Two fusion schemes, both shipped:**

| | Scheme | Where used | Why |
| --- | --- | --- | --- |
| **A** | **Score blend** — the $\beta \cdot h(t)$ term in §18.5, with $\beta$ tuned on validation | The standalone tool, and the `BLASTRADIUS-HEURISTIC` baseline | Works on a repo with no BR-Bench history; deployable on day one; interpretable |
| **B** | **Feature-level fusion** — reachability features and history features enter LightGBM separately and the model learns the combination | The Phase 4 predictor and every headline number | Strictly better where data exists; the ablation (graph-only / history-only / both) is a required table |

**The ablation is a research result, not an engineering detail.** If history-only beats graph-only, that is a finding about change impact analysis that the field should hear, and it must be reported plainly rather than buried (v1's Gate 3 already commits to this).

**Cold-start behaviour matters for the tool's credibility.** A new repository has no co-change history and no failure history, so scheme A degrades to pure structure. Report performance stratified by history depth — *"with 30 days of history we reach X; with 90 days, Y"* — which is both an honest limitation and an argument for the dataset's ongoing value.

### 18.7 Cutoff heuristics — how the answer stays a shortlist `[new]`

Never return "the whole repo". Four mechanisms, applied in order:

1. **Hard cap.** Return at most `min(200 tests, 20% of the suite)`. Configurable; the default is what the cost curve says is worth a developer's attention.
2. **Score threshold from calibration.** Once T4.6 exists, cut at the probability where expected cost is minimised given cost-per-test-minute and cost-per-escaped-regression. This makes the cutoff *derived* rather than arbitrary — the economics argument from `[v2 B.1]`.
3. **Elbow detection.** Sort scores descending, cut at the largest second-difference within the top 50. Cheap, robust, and it adapts to instances where the graph is genuinely confident about three tests.
4. **Selective prediction / abstain.** If the top-1 score is below a floor, or `frontier_truncated`, or the change touches a dynamic boundary with no reachable tests, **abstain and recommend retest-all**. *"Runs 12% of the suite on 80% of PRs and defers on the rest"* is a far more deployable claim than a single operating point.

**Report the abstain rate.** A model that abstains 60% of the time is not deployable and the number should embarrass us into fixing it rather than being quietly omitted.

### 18.8 Test-case prediction vs file-level impact — two distinct outputs `[new — restores an approved-scope commitment]`

The approved Zeroth Review abstract promises prediction of *"the files and test cases that are likely to be affected."* v1 optimised almost entirely for tests. Both are shipped, as two heads over the same propagation.

| | **File-level impact** | **Test-level ranking** |
| --- | --- | --- |
| Output | Ranked source files likely to need changing | Ranked tests likely to fail |
| Ground truth | Files modified in later commits of the same PR + files in the merge commit (**T1.8**) | Fault-revealing tests from CI outcomes (T1.3) |
| Literature it is comparable to | **The CIA camp** — Borg, Huang, Dai, Zhao, Gupta & Gupta | The RTS and PTS camps |
| Metrics | Precision / Recall / F1 (as the abstract promises), plus MAP | Recall@k, APFD, MAP, NDCG |
| Propagation | Stage A only (§18.4), aggregated to file granularity | Stages A + B + C |
| Cost to add | ~2 hours — it is Stage A, which already runs | — |

**Why this is worth two hours.** It is the only output directly comparable to the seven papers in the approved reference list. Without it, §28's novelty positioning has to argue against those papers on a task none of them attempted, which is a weaker rhetorical position than *"on the task they did attempt, here is our number; and here is the additional task nobody could attempt before, because the data did not exist."*

---

## 19. Incrementality, Storage & Scale

### 19.1 Full build vs incremental update, and the invalidation strategy `[merged v2 C.4 + new]`

**Materialise a graph only at SHAs we actually need** — the base SHA of each instance — not at every commit. That is a reduction of roughly one to two orders of magnitude before any other optimisation.

```python
def build_graph_at(repo_path, sha, cache_dir) -> Path:
    """Returns the path to graph_{repo}_{sha}.json."""
```

**Algorithm:**

1. `git worktree add --detach {tmpdir} {sha}` — never clone per commit. Pool worktrees; `git worktree remove` after.
2. Find the nearest already-built graph for this repo by walking Git ancestry (`git merge-base --is-ancestor`). If one exists within **N = 50 commits**, go incremental; otherwise cold build.
3. **Incremental:** `git diff --name-only {prev_sha} {sha}` gives the dirty file set. Then:
   - Remove all nodes whose `source_file` is in the dirty set, and all their incident edges.
   - Re-extract only the dirty files via the Graphify extract path.
   - Splice the new subgraph in.
   - **Re-run symbol resolution for the dirty files *and their importers***, not globally. The importer set is one reverse-`imports` hop, which is cheap and is the part that is easy to get wrong: resolving only dirty files leaves stale edges pointing at deleted symbols.
4. **Re-run Leiden clustering only if >5% of nodes changed**; otherwise inherit community assignments and mark `communities_inherited=true`. Clustering is the expensive step and it is stable under small edits.
5. Store metadata: `{repo, sha, built_at, graphify_commit, n_nodes, n_edges, parse_failures, incremental_from, communities_inherited}`.

**The blocking correctness requirement** `[v2 G.4]`: an incremental build at SHA *X* must produce **the same graph** as a cold build at SHA *X*. Test it over 5 real commits of a small repo, as a CI test, on every merge. If they diverge, the dataset is untrustworthy — treat divergence as a release blocker, not a known issue. (Community IDs are exempt when `communities_inherited=true`; compare partitions by adjusted Rand index rather than by ID equality.)

**Reuse Graphify's SHA-256 content cache** (`cache.py`) rather than adding a second caching layer. Note its **zero-node skip** — it refuses to cache a file that produced no nodes, which prevents poisoned cache entries. That is a subtle bug-avoidance worth a week of discovery.

### 19.2 Storage backend evaluation `[new]` — see **D-06**

The merge brief asks for a real recommendation with reasoning for a three-person semester project.

| Backend | Setup cost | Per-commit graph versions | *k*-hop query | Ops burden | Ships inside the artifact? | Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| **NetworkX in-process + node-link JSON/Parquet** | None | Natural — one file per (repo, sha) | Fast in memory; O(V+E) load | None | ✅ `pip install` | ✅ **Traversal engine** |
| **DuckDB + Parquet** | None (embedded) | Natural — partition by (repo, sha) | Recursive CTEs work but are awkward for weighted multi-type traversal | None | ✅ | ✅ **System of record + feature cache** |
| **KuzuDB** | Low (embedded property graph, Cypher) | Would need one DB per SHA or a version property | Excellent — purpose-built | Low | ✅ embedded | ⚠️ **Documented upgrade path** |
| **Neo4j** | High (server, JVM, licence considerations) | Painful — a temporal property model on every node | Excellent | **High** | ❌ breaks one-command repro | ❌ v1 explicitly leaves this |
| **Memgraph** | Medium (server) | Same as Neo4j | Excellent, in-memory | Medium–high | ❌ | ❌ |
| **Postgres + recursive CTEs** | Medium (server) | Workable with a `sha` column | Adequate; slower than a graph engine | Medium | ❌ | ❌ |

**Recommendation: NetworkX for traversal, DuckDB + Parquet as the system of record.** Four reasons, in order:

1. **The artifact must run with one command.** A Data & Tool Showcase reviewer runs `docker compose up` or `make all`. Every server-based option adds a service, a port, a healthcheck, and a class of failure that happens on the reviewer's machine and not yours. This alone decides it.
2. **The access pattern is not what graph databases optimise.** We do not run ad-hoc deep queries over one enormous graph; we load a small graph (10⁴–10⁵ nodes), run one bounded traversal, and discard it. That is an in-memory workload.
3. **NetworkX is already the interchange format.** Graphify emits node-link JSON; PyTorch Geometric ingests it via `from_networkx`. Zero conversion layers is worth more than raw traversal speed at this scale.
4. **DuckDB is where the MSR community is heading** for exactly this kind of Parquet-backed analysis, and it gives SQL over tens of millions of rows on a laptop with no server. **Do not use MongoDB or Postgres here.**

**The upgrade trigger for Kuzu:** if a single repo's graph exceeds ~2 million nodes, or if the cross-repo global graph (§44) is built. Neither is in scope for v1.

### 19.3 Graph versioning `[new]` — see **D-14**

| Option | Storage | Query | Verdict |
| --- | --- | --- | --- |
| Full graph per commit, all commits | Enormous | Trivial | ❌ |
| **Full graph only at instance base SHAs** | ~50–200 MB per repo | Trivial | ✅ **Baseline choice** |
| **Snapshot every N=50 + deltas between** | ~4× smaller again | Load snapshot + replay deltas | ✅ **Applied on top, for repos with dense instances** |
| One temporal graph with validity intervals per node/edge | Smallest | Complex; every query needs a time predicate; incremental builds become mutations | ❌ — elegant and wrong for this timeline |

**Chosen: materialise at instance base SHAs, with snapshot+delta compaction.** Concretely: for each repo, sort the required SHAs by commit order; every 50th is a full snapshot; the rest are stored as `{added_nodes, removed_nodes, added_edges, removed_edges}` against the previous snapshot. Time-travel is "load nearest ancestor snapshot, replay deltas forward". A `graph_index.parquet` maps `(repo, sha) → (snapshot_path, delta_paths[])`.

This keeps the on-disk footprint tractable without inventing a temporal query language, and it composes with §19.1's incremental builder — a delta is exactly what the incremental build already computes.

### 19.4 Concrete budgets `[new]`

Hard numbers. Anything exceeding a ceiling is **excluded at ingestion with the exclusion counted**, never discovered during analysis (**T15**).

| Quantity | Budget | Enforcement |
| --- | --- | --- |
| Repo size (source files) | ≤ 20,000 | Reject at clone (§15.1) |
| Repo size (LOC, extractable) | ≤ 2,000,000 | Reject at clone |
| Repo mirror on disk | ≤ 5 GB | Reject at clone |
| **Cold graph build** | **≤ 10 min** (target: ≤ 3 min at p50) | Timeout → repo dropped, reason recorded |
| **Incremental graph build** | **≤ 10 s** on a ~2,000-file repo | Alert if p95 > 30 s |
| Graph size in memory | ≤ 8 GB per build process | Hard `resource` limit; OOM → drop repo |
| Graph on disk, compressed | ≤ 50 MB per snapshot | Monitor |
| **Query latency, full feature set per instance** | **≤ 100 ms** | Benchmark in CI on the mini-corpus |
| Parse-failure rate | ≤ 20% per (repo, sha) | Repo dropped above this |
| Corpus graph store total | ≤ 150 GB | Compaction (§19.3) if exceeded |
| Raw logs | 200–500 GB | Prune success-run logs after parsing |

**Worked feasibility check.** 80 usable repos × ~600 instances each ≈ 48,000 instances (consistent with the ≥50k Phase 1 target). At one cold build per repo (10 min) plus one incremental per instance (10 s): 80 × 10 min + 48,000 × 10 s ≈ 13 h + 133 h ≈ **6 machine-days, parallelisable 3-wide across team laptops ≈ 2 days wall-clock**. That fits inside Phase 2's four-week window with an order of magnitude of headroom — which is the point of checking.

**If it blows up anyway,** in order: (1) cap instances per repo at 300 by uniform temporal sampling, which halves the cost and *improves* per-repo balance for the random-effects analysis; (2) drop the largest-quartile repos; (3) reduce *k* from 4 to 3. Do not optimise the extractor — it is Graphify's and it is already `ProcessPoolExecutor`-parallel.

---

## 20. Query & Surfacing

### 20.1 The canonical questions, written as queries `[new]`

These ten are the system's contract. Everything in the API, the CLI, and the UI is one of them.

| # | Question | Semantics | Latency budget |
| --- | --- | --- | --- |
| **Q1** | *Which tests will this change break?* | seeds → §18.4 Stage A+B+C → §18.5 score → §18.7 cutoff | ≤ 100 ms |
| **Q2** | *Why was this test flagged?* | Top-3 shortest justification paths from any seed to `t`, with edge types and confidences, plus SHAP top-3 | ≤ 50 ms |
| **Q3** | *Which files will need to change?* | Stage A aggregated to file granularity (§18.8) | ≤ 100 ms |
| **Q4** | *Where is the test suite blind?* | Changed nodes with `pagerank > p90` whose *k*-hop test neighbourhood is empty (**RQ6**, T3.13) | ≤ 200 ms |
| **Q5** | *Which open PRs conflict with this one?* | Pairwise intersection of impact sets and of `communities_touched` (Graphify's `--conflicts` primitive, extended past zero-hop) | ≤ 500 ms |
| **Q6** | *What is the blast radius of this file, historically?* | Union of fault-revealing sets across all past instances that touched it (**RQ9** input) | ≤ 1 s (offline) |
| **Q7** | *Which files co-change with this one?* | `co_changed_with` neighbours ranked by lift | ≤ 20 ms |
| **Q8** | *Which downstream packages does this touch?* | `depends_on` traversal from the changed package node | ≤ 20 ms |
| **Q9** | *How often has this test failed when this file changed?* | Cross-feature lookup in the outcome history | ≤ 20 ms |
| **Q10** | *Should we trust this prediction, or retest all?* | Abstain rule (§18.7 item 4) + calibrated confidence | ≤ 5 ms |

Illustrative form for Q1, written as Cypher for readability even though the implementation is NetworkX + DuckDB (this pseudo-Cypher is the specification, not the code):

```cypher
MATCH (s:Symbol) WHERE s.node_id IN $seeds
MATCH p = (dep)-[:calls|imports|inherits|instantiates*1..4]->(s)
MATCH (t:TestMethod)-[b:tests|tests_by_convention|tests_by_layout]->(dep)
WITH t, min(length(p)) AS d, max(b.confidence) AS c, max(r.weight) AS w
RETURN t.test_id,
       max(pow(0.6, d) * w * c) + 0.3 * t.failure_rate_90d + 0.1 * t.same_community
       AS score
ORDER BY score DESC LIMIT $k
```

### 20.2 API surface, caching, and pagination `[merged v1 T5.2 + new]`

```
POST /predict            {repo, base_sha, head_sha | changed_files[]}
                         → {predictions[], abstained, cutoff_rule, model_version, graph_sha}
GET  /explain/{test_id}  ?instance=  → {paths[], shap[], history, binding_strategy}
GET  /graph/{repo}/{sha} ?focus=&depth=&types=&limit=  → node-link JSON (already filtered)
GET  /impact/files       same input as /predict → ranked files (§18.8)
GET  /gaps/{repo}/{sha}  → Q4 test-gap report
GET  /health             → {status, graph_cache_size, model_version}
```

**Pagination.** `/predict` returns the top 50 by default with a cursor; the full ranking is available at `?limit=`, capped at the §18.7 hard cap. Never return an unbounded impact set over the wire — a 40,000-test repo would produce a payload nobody wants and a UI nobody can render.

**Caching, three layers:**

| Layer | Key | TTL | Store |
| --- | --- | --- | --- |
| Graph | `(repo, sha)` | until eviction (LRU, 20 graphs) | in-process, backed by disk |
| Feature vectors | `(repo, sha, changed_set_hash)` | 24 h | DuckDB |
| Prediction | `(repo, sha, changed_set_hash, model_version)` | 24 h | DuckDB |

`changed_set_hash = sha256(sorted(changed_file_paths + changed_symbol_ids))`. Including `model_version` in the prediction key is what prevents a stale-cache bug from silently invalidating a demo after a retrain — the kind of thing that goes wrong live in front of a viva panel. **No Redis**: an extra service breaks the one-command artifact requirement (§19.2 reason 1).

### 20.3 Interactive visualisation and the hairball problem `[merged v1 T5.3 + v2 A.1 + new]` — see **D-15**

Any force-directed rendering of a real repository graph is an unreadable hairball. Six mechanisms, applied by default rather than offered as options:

1. **Focus + context.** The default view is the ego network at depth 2 around the changed nodes, not the repository. Everything else is available by expansion, never by default.
2. **Community collapsing.** Leiden communities render as single compound nodes until clicked. A 5,000-node graph becomes ~30 visible nodes.
3. **Hard render cap.** At most **300 nodes** on screen. Selection is by impact score, not by degree — the highest-scoring tests and the path nodes that justify them.
4. **Edge-type filter chips.** `calls` / `imports` / `tests` / `co_changes` toggle independently. Turning off `co_changes` alone typically halves visible edge count.
5. **Path-only mode.** For Q2, hide everything except the justification paths. This is the view that actually explains a prediction, and it should be one click from any test.
6. **Semantic zoom.** Package → file → class → method as you zoom, rather than shrinking labels into illegibility.

**Library choice.**

| Library | Compound/community nodes | Layout quality | React integration | Verdict |
| --- | --- | --- | --- | --- |
| **Cytoscape.js** | ✅ native compound nodes | ✅ several layouts incl. fcose | Good | ✅ **Public demo** — compound nodes give mechanism 2 for free |
| **react-force-graph** | ❌ manual | Good force layout, WebGL for large graphs | ✅ native | ⚠️ v1's choice; fine if Prisha already knows it |
| **vis.js** (Graphify's `callflow_html.py`) | Partial (clustering API) | Adequate | Wrapper needed | ✅ **Internal / CLI view** — it already exists and works |
| **D3 force** | ❌ | Full control, most work | Manual | ❌ Not worth the hours here |

**Recommendation:** fork Graphify's vis.js view for the internal and CLI-served view (zero cost, it works today), and use Cytoscape.js for the public demo because compound nodes make community collapsing free. Deviating from v1's `react-force-graph` is a ~1-day two-way door and should be Prisha's call based on what she can build fastest.

### 20.4 Explainability: the contract `[new]`

**Every prediction in the top-k ships a justification.** Not a score — a reason a developer can check.

```jsonc
{
  "test_id": "com.example.OrderServiceTest#testDiscountApplied",
  "score": 0.83,
  "rank": 3,
  "justifications": [
    { "kind": "graph_path",
      "path": ["OrderService.applyDiscount (changed)", "PricingRules.evaluate",
               "OrderServiceTest#testDiscountApplied"],
      "edges": ["calls", "tests"],
      "confidence": [0.95, 1.0],
      "distance": 2,
      "contribution": 0.61 },
    { "kind": "history",
      "detail": "failed on 4 of the last 11 changes to OrderService.java",
      "contribution": 0.17 },
    { "kind": "binding",
      "detail": "bound by naming convention (OrderServiceTest → OrderService)",
      "strategy": "tests_by_convention", "confidence": 0.85 }
  ],
  "shap_top": [["min_dist_to_changed", 0.41], ["failure_rate_90d", 0.19],
               ["same_community", 0.08]],
  "unexplained": false
}
```

**Three rules:**

1. **A prediction with no justification is marked `unexplained` and counted.** Report the unexplained fraction in the paper. *"X% of our top-20 predictions have no graph justification"* is an honest, interesting number, and hiding it would be the kind of omission a careful reviewer finds.
2. **Paths are shown as the actual node sequence with edge types**, not as a score. "Distance 2" tells a developer nothing; `applyDiscount → PricingRules.evaluate → the test` tells them where to look. This is what the approved abstract means by *explainable*.
3. **SHAP and graph paths are complementary, not redundant.** SHAP says which *feature family* drove the score; the path says which *code* did. Show both; they answer different questions and a developer who distrusts one will check the other.

---

# Part V — Dataset & Evaluation: The Research Contribution

`[merged]` — this part carries equal weight to Part IV. It is what makes this an MSR submission rather than a course project, and it is written against what a Data & Tool Showcase reviewer is instructed to look for.

---

## 21. Ground Truth Construction

### 21.1 The definition `[v1]`

For an instance = a `(head_sha, workflow_run)` pair with a resolved base:

$$T_{\text{reveal}} = T_{\text{head\_fail}} \setminus T_{\text{base\_fail}} \setminus T_{\text{flaky}}$$

A test is **fault-revealing** for a change if it failed at head, did not fail at base, and did not flip on an identical SHA. Everything else in this section is the machinery that makes each of those three sets trustworthy.

### 21.2 The GitHub Actions mining pipeline, end to end `[merged v1 T0.3/T1.1/T1.3 + new]`

```
 SEART frame ──▶ CI-liveness filter ──▶ workflow triage ──▶ 300 candidate repos
      │
      ▼
 harvester daemon (T0.3) ── PRs ─▶ commits ─▶ runs ─▶ jobs ─▶ {annotations | artifacts | logs}
      │                                                          gzipped JSONL, immutable
      ▼
 parser suite (T1.1) ── 6 parsers ─▶ TestOutcome records ─▶ normalize_test_id()
      │
      ▼
 labelling engine (T1.3) ── base-run resolution ─▶ T_reveal ─▶ flakiness filters ─▶ 3 splits
      │
      ▼
 instances.parquet + outcomes.parquet ──▶ graph join on test_id ──▶ features ──▶ BR-Bench
```

**Log parsing, specifically.** Source tiers in strict preference order (§5.5): check-run annotations (structured, and they **persist past 90 days**) → workflow artifacts containing JUnit XML (structured, 90-day window) → job logs (regex, 90-day window) → Docker re-execution (gold subset only). `label_source` is a first-class column and per-tier accuracy is reported.

Log-specific handling, because this is where the time goes: strip ANSI escapes and the leading ISO-8601 timestamp *before* any regex; handle grouped output (`::group::` / `::endgroup::`); handle interleaved parallel test output by anchoring on framework-specific line starts rather than assuming contiguity; truncate `failure_message` at 2,000 characters and store it in a separate file (§22.4).

**Rate-limit handling** is §8.2 in full: three fine-grained PATs, quota-aware round-robin from `X-RateLimit-Remaining`/`X-RateLimit-Reset`, `Retry-After` honoured on 429 and on secondary limits, exponential backoff with full jitter to 6 attempts, resumable SQLite cursors, `--dry-run` budget estimation. All HTTP goes through exactly one function.

**Flaky-test filtering** is the four-filter pipeline of §5.3 — same-SHA flip, broken-trunk, rolling flip-rate, coverage-free DeFlaker heuristic — producing three splits (`strict`, `permissive`, `raw`) with headline numbers on `strict` and sensitivity reported (RQ11).

### 21.3 Base-run resolution — the hardest correctness problem `[merged v1 T1.3 + v2 C.3]`

The broken-trunk filter is only as good as the base run behind it, and the base SHA frequently has no run of the same workflow.

```
1. T_head_fail = tests failing at head_sha
2. Base run = most recent run of the SAME workflow_id at base_sha
   ├─ none? walk ancestors of base_sha, max 10, record base_run_distance
   └─ still none? status = "no_base"  →  EMIT NO LABELS for this instance
3. T_base_fail = failing tests in that base run
4. T_reveal = T_head_fail − T_base_fail
5. Remove T_flaky (same-SHA flips)
6. Annotate survivors with flakiness_score
```

**Edge cases that must be handled explicitly and documented in the docstring:**

| Case | Rule | Why it matters |
| --- | --- | --- |
| Head run cancelled or timed out | Exclude; `run_conclusion` recorded | Partial results look like passes |
| **Base run has no parsed test results at all** | **`status="no_base"`, emit nothing.** An empty base failure set must never be read as "base was green" | **The single most dangerous bug in the labelling engine.** It manufactures false positives at scale |
| Test exists at head, not at base | `fault_revealing=False`, `new_test=True` | A new test failing is not a regression |
| Test exists at base, not at head | Excluded entirely | Deleted tests are not evidence |
| Multiple runs at head (matrix builds) | **Union failures across legs; record `n_matrix_legs`** (**D-12**) | A test failing on one OS leg is still fault-revealing |
| `base_run_distance > 0` | Kept, with the distance as a data-quality column | Lets analysts filter to distance-0 for a clean subset |

**Report the distribution of `base_run_distance` and the `no_base` rate.** They are the honest measure of how often the broken-trunk filter actually applied, and a reviewer who wants to check label quality will look for exactly this.

### 21.4 The second ground-truth arm: file-level impact `[new — T1.8]`

For the file-level head (§18.8), "actual impact" is derived from **subsequent modifications**: files modified in later commits of the same PR after the instance's head SHA, plus files touched in the merge commit. This is the CIA literature's native label, it is what makes the results comparable to the seven approved references, and it costs nothing extra because the PR commit list is already harvested.

Record it separately as `actual_changed_files` with a `window` attribute (same-PR / same-PR + 7 days), and be explicit that it is a *different* construct from fault revelation — one measures developer behaviour, the other measures defect propagation. **The divergence between these two labels on the same instances is, in miniature, the paper's whole thesis**, and it is worth a sentence in §V.

### 21.5 The causal anchor `[v1 T1.5]`

The gold subset (§9.5): 300–500 instances re-executed in Docker at base and head, twice each, with pinned image digests and lockfiles. `PASS@base → FAIL@head` is a causal positive. The **agreement rate between observational and causal labels is the credibility anchor of the paper** and belongs in the abstract as the one headline number about label quality.

---

## 22. Dataset Schema & Release

### 22.1 The released artifact `[merged v1 §31 + new]`

BR-Bench ships as partitioned Parquet with a documented schema (full column lists in §31):

| File | Grain | Approx. rows |
| --- | --- | --- |
| `instances.parquet` | one per (head_sha, workflow_run) | ~50k |
| `outcomes.parquet` | one per (instance, test) observation | 10⁷–10⁸ |
| `graph_nodes.parquet` / `graph_edges.parquet` | per (repo, sha) | 10⁷–10⁸ |
| `cochange.parquet` | per (repo, window, file pair) | 10⁶ |
| `gold.parquet` | one per (instance, test) in the causal subset | ~10⁵ |
| `identity_map.parquet` `[new]` | node renames/moves between analysed SHAs | 10⁵ |
| `failure_messages.parquet` | separated, secret-scanned | 10⁶ |

**Size estimate.** With dictionary encoding and ZSTD, expect **8–25 GB** compressed for the full release, dominated by `outcomes` and `graph_edges`. Ship a **`br-bench-lite`** variant — sampled negatives at a documented ratio, no graph tables — at **under 1 GB**, because that is the version people will actually download and try, and adoption is the metric this track cares about.

### 22.2 Format, licensing, hosting `[v1]`

- **Format:** Parquet (analysis) + a HuggingFace `datasets` loader script (accessibility) + `schema.json` with a `validate.py` checker.
- **Licence:** **CC-BY 4.0** for data, **MIT** for code (compatible with the Graphify fork).
- **Hosting:** **Zenodo with a DOI** (mandatory — GitHub alone is explicitly not accepted), mirrored on HuggingFace, code on GitHub with a tagged release and `CITATION.cff`.
- **Datasheet:** Gebru et al. format — motivation, composition, collection process, preprocessing, uses, distribution, maintenance. Reviewers on this track look for it by name.

### 22.3 Versioning and maintenance `[new]`

The dataset is **live**, not a snapshot — the harvester keeps running. State the maintenance plan in the datasheet: semantic versioning (`v1.0` = the submitted snapshot, frozen and DOI-pinned; `v1.x` = additive months of capture; `v2.0` = any schema change), each version with its own DOI, the frozen `v1.0` always resolvable so published results stay reproducible. "The collection tooling is released so anyone can extend it" is the T1-mitigation framing (**"90 days of data"** objection, §45 row 3) and it is only credible if the versioning story is written down.

### 22.4 Release hygiene `[v1]`

- Pseudonymise `author_login` with a salted hash; publish the salt separately or not at all, and document the choice.
- Store `failure_message` in a separate file — it can contain absolute paths and occasionally environment detail. Scan with `gitleaks` before release.
- Ship `schema.json` and `validate.py`.
- `[v2 T11]` Embed a documented **canary string** so future LLM training-data contamination is detectable.
- Public repos only, permissive licences only, GitHub ToS honoured, no personal data beyond public commit authorship. Stated in the paper (**T19**).

---

## 23. Repository Selection

### 23.1 The sampling frame `[v1 T0.1]`

**Source:** SEART GitHub Search (Dabic, Aghajani & Bavota, MSR 2021), not hand-rolled GitHub search. It indexes every repo with ≥10 stars across 25 characteristics and exists precisely for MSR sampling. The exact query string is stored in `data/frame/QUERY.md`.

**Criteria:** language ∈ {Java, Python} · ≥500 stars · ≥1000 commits · not a fork · ≥1 commit in the last 60 days · has a `LICENSE` · ≥50 PRs in the last 90 days · ≥100 workflow runs in the last 90 days · at least one workflow matching test intent (`test|ci|build|pytest|mvn|gradle`) · excluding workflows matching `release|deploy|docker|publish|docs|dependabot|codeql|lint-only`.

**Target: 300 candidates → ~60–100 usable.** Over-sample aggressively; attrition on this pipeline is brutal.

### 23.2 Why this sample is defensible `[new]`

A reviewer will ask why these repos and not others. Four defences, and it is worth having all four ready:

1. **The frame is reproducible.** SEART is a published, citable sampling instrument and the query is released verbatim. This is materially stronger than "we picked popular repos".
2. **The criteria are necessary, not aesthetic.** Each one removes repositories from which the *ground truth cannot be constructed*: no CI liveness → no outcomes; no test workflow → no test verdicts; no licence → cannot redistribute derived data; low PR volume → no instances. Say this explicitly, because it converts what looks like convenience sampling into eligibility criteria.
3. **The bias is named and quantified.** Popular, actively-maintained, CI-using OSS projects are **not** representative of software in general. They are, however, exactly the population the RTS and PTS literature studies, so the results are comparable to that literature. State it in Threats to Validity (§26.2) with the star and age distributions, not as a hedge but as a characterisation.
4. **Attrition is reported per stage** (T0.7), so a reader can see precisely which filter removed what, and re-run with different thresholds.

### 23.3 Attrition funnel — report this as a table `[new]`

| Stage | Filter | Expected survivors |
| --- | --- | --- |
| 0 | SEART query result | ~2,000 |
| 1 | Stars / commits / recency / licence | ~800 |
| 2 | ≥50 PRs in 90 days | ~500 |
| 3 | CI liveness (≥100 runs / 90 d) | ~300 ← **the frame** |
| 4 | Has a test-intent workflow | ~250 |
| 5 | Produces parseable test outcomes | ~150 |
| 6 | Produces ≥1 fault-revealing instance | ~110 |
| 7 | Graph builds within budget (§19.4) | ~95 |
| 8 | Test-node binding rate ≥70% (**T8**) | **~60–100 usable** |

Numbers 4–8 are estimates until measured; the funnel exists so that a shortfall is visible in Week 2 rather than Week 8 (**T14**).

### 23.4 Language and activity distribution `[new]`

Target roughly balanced Java/Python by *instance count*, not by repo count — Java repos tend to have larger suites and produce more (instance, test) pairs. Report both distributions. If instances skew beyond 70/30, either sub-sample the dominant language for the headline analysis or report every metric stratified (which is the plan anyway, §25.4). **Per-repo random-effects analysis** (T3.8 item 4) exists so that no single mega-repo drives the result — check it before believing any aggregate number.

---

## 24. Baselines

`[merged v1 T3.1–T3.7 + new]` — nine baselines across all three camps. The point of the set is that it spans the three camps of §1, so the divergence result is measured rather than asserted.

| # | Baseline | Camp | Input | Effort | Purpose |
| --- | --- | --- | --- | --- | --- |
| B1 | **Retest-All** | — | none | 1 h | The denominator for every cost claim |
| B2 | **Random ranking** | — | test list | 1 h | The floor |
| B3 | **Path similarity** | heuristic | paths | 1 h | Token overlap between changed-file path and test-file path. **Surprisingly hard to beat on small changes** — report honestly |
| B4 | **Static reachability, *k*-hop** | RTS | graph | 4 h | *k* ∈ {1,2,3,∞}. Produces RQ1's *R* set. In-house STARTS-like |
| B5 | **Ekstazi (the real tool)** | RTS | Java build | 6 h | ~50 reproducible-build Java instances. *"We compared against the tool"*, not a re-implementation |
| B6 | **Historical failure frequency** | PTS-lite | outcome history | 2 h | **Startlingly strong. If you cannot beat it you do not have a paper — build it early and know the number** |
| B7 | **Evolutionary coupling / association rules** | IA | git history | 3 h | The IA-camp baseline, standing in for the RIPPLE family. Produces RQ1's *C* set |
| B8 | **GRAPHIFY-COMMUNITY** | tool-in-the-wild | graph | 2 h | Test nodes whose Leiden community is touched, ranked by degree |
| B9 | **GRAPHIFY-DIRECT** | tool-in-the-wild | graph | 1 h | Only tests inside changed files. **Near-zero recall by construction — report it as the floor** |
| B10 | **BLASTRADIUS-HEURISTIC** `[new]` | ours, unlearned | graph + history | included | §18.5 with tuned $\gamma,\beta,\alpha$. Isolates *"how much comes from the model versus the graph?"* |

**On published approaches we could reimplement but will not:** Chianti (Ren et al., OOPSLA 2004) is the closest classical Java CIA tool and requires a build plus a working JVM instrumentation setup at each historical commit — the same barrier as §15.3. Say so explicitly in Related Work rather than leaving the omission for a reviewer to notice; "we could not run it at corpus scale, and here is why, and that limitation is itself part of our motivation" is a strong answer.

**Fairness protocol for B8/B9** `[v2 C.5]`: reimplement `compute_pr_impact`'s *exact* semantics against our graph objects — **do not "improve" it**. Document any difference in a docstring. Record the Graphify commit SHA in the results file so it can be re-pinned and re-run. Produce `reports/graphify_baseline.md` describing precisely what the heuristic computes, so an accurate description can be pasted into Related Work. Frame findings as being about *graph-proximity heuristics in general*, never as an attack on one project.

---

## 25. Metrics

### 25.1 The metrics the approved abstract promises `[v1 + Zeroth Review]`

**Precision, recall, F1** — computed set-wise against the fault-revealing set at the operating point produced by the cutoff rule (§18.7), and against `actual_changed_files` for the file-level head (§18.8). These are non-negotiable: they are in the approved abstract and they are what makes the work comparable to the seven references in §28.

### 25.2 The ranking metrics, and why they are added `[merged v1 §32 + new]`

**Justification, in one sentence for the paper:** impact is consumed as a *ranked shortlist*, so a set-valued metric at one arbitrary cutoff discards most of the information about output quality and cannot express the practitioner's actual question — *"how much of the suite must I run?"*

| Metric | Definition / use | Why it is here |
| --- | --- | --- |
| **Recall@k**, k ∈ {1,5,10,20}% of suite | Fraction of fault-revealing tests in the top k% | **Primary.** Directly comparable to the Meta PTS framing |
| **Precision@k** | Precision in the top k | The reviewer-facing half of the same number |
| **MAP** | Mean average precision over instances | Standard IR ranking measure; handles multiple positives per instance |
| **MRR** | Mean reciprocal rank of the first true positive | *"How far down before I find a real failure?"* — the impatient-developer metric |
| **NDCG@10** | Graded relevance (weight by test cost or severity) | Lets an expensive test outrank a cheap one |
| **APFD / APTF** | Average percentage of faults detected | The RTP literature's native metric; required for comparability with RTPTorrent-style work |
| **Safety violation** | Fraction of instances where a fault-revealing test was excluded | The RTS literature's native metric. **We will violate safety and must report by how much** |
| **Precision violation** | Fraction of selected tests that were not fault-revealing | RTS-native |
| **Suite reduction %** | 1 − (selected / total) | The cost side of the trade |
| **Simulated CI-minutes saved** | Reduction × observed durations | The practitioner headline; feeds T6.10 economics |
| **Brier score / ECE** `[v2 B.1]` | Calibration of the risk score | RQ7. Nobody in CIA/RTS reports this because set-valued output cannot |
| **Abstain rate** `[new]` | Fraction of instances where we defer to retest-all | Selective prediction is only honest if the abstain rate is published |

### 25.3 Dataset-quality metrics `[new]`

These are not model metrics; they are the metrics a Data & Tool reviewer actually assesses, and each has a home in §IV of the paper.

| Metric | Target | Where reported |
| --- | --- | --- |
| Parser precision on the 40-log fixture set | ≥95% | §III |
| Parser coverage (failed jobs yielding ≥1 test name) | 40–70%, **published honestly** | §III |
| **Test-node binding rate** | ≥80% target, **≥70% floor** (**T8**) | §III/IV |
| **Observational-vs-causal agreement rate** | **the headline label-quality number** | Abstract + §IV |
| Flakiness prevalence | reported as a finding in its own right | §IV |
| `no_base` rate, `base_run_distance` distribution | reported | §IV |
| Positive-class prevalence per event type | reported (survivorship, **T2**) | §IV |
| Parse-failure rate per language | reported | §IV |
| Phantom-edge rate per language (T2.8) | reported | §IV |
| `identity_break_rate` (§16.5) | reported | §IV |
| Unexplained-prediction fraction (§20.4) | reported | §V |

### 25.4 Reporting discipline `[merged]`

Every headline number is reported: on the `strict` split (with `permissive`/`raw` in an appendix, RQ11) · stratified by language · with bootstrapped 95% CIs · with Wilcoxon signed-rank plus Holm–Bonferroni and **Cliff's delta effect sizes** · over five seeds, mean ± std · and with a per-repo random-effects check so no single mega-repo drives it.

---

## 26. Threats to Validity

`[new]` — written honestly, in the four standard categories. This section is short in the paper and long here on purpose; the long version is the source for the short one and for the viva.

### 26.1 Internal validity — *are our labels measuring what we think?*

| Threat | Our position |
| --- | --- |
| **Labels are observational, not causal.** A test failing on a run containing a change does not prove the change caused it | The gold subset (§21.5) provides causal labels on 300–500 instances; we report the agreement rate and scope every causal claim to it. **This is the single most important limitation and it leads the section** |
| **Flakiness contaminates positives** | Four filters, three splits, headline on `strict`, sensitivity reported (RQ11). Residual flakiness is acknowledged, not claimed away |
| **Base-run resolution errors** | `base_run_distance` and `no_base` rates published; the "empty base ≠ green base" trap is handled explicitly (§21.3) |
| **Parser errors** | 40-log hand-labelled fixture set; per-parser precision and per-tier accuracy published; parsers open-sourced |
| **Test-ID normalisation errors** | Contract test inherited from Graphify's `ids.py`; binding rate published; round-trip tested across six input formats |
| **Leakage through the time split** | Written leakage audit (T4.7); time-based splits only; `touches_test_file` exclusion rule (§18.2); duplicate-code check (Allamanis 2019) |
| **Matrix-build aggregation choice** | Union rule stated (**D-12**), `n_matrix_legs` published so alternatives are computable from the release |

### 26.2 External validity — *does it generalise?*

| Threat | Our position |
| --- | --- |
| **Popular, CI-heavy OSS is not software in general** | Named, characterised with distributions (§23.2 defence 3), and noted as the same population the RTS/PTS literature studies |
| **Two languages** | Java for baseline comparability, Python for scale, the pair as a research variable (§15.2). Pipeline is language-pluggable |
| **Six-month observation window** | Rolling capture Aug–Nov plus 90-day backfill; window documented; harvester released so anyone can extend it. Framed as a *live* dataset (§22.3) |
| **Cross-project generalisation is poor** | Reported honestly. This is a **finding**: test-failure prediction is strongly project-specific, which motivates per-project fine-tuning and *increases* the value of a multi-project dataset |
| **GitHub Actions only** | Other CI systems differ; the labelling logic is CI-agnostic but the harvester is not. Stated |

### 26.3 Construct validity — *are we measuring the right thing?*

| Threat | Our position |
| --- | --- |
| **"Fault-revealing" ≠ "faulty"** | A test can go red for environment reasons unrelated to correctness. The broken-trunk filter and gold subset bound this; the qualitative taxonomy (RQ8) characterises what the residual actually is |
| **Test failure is a proxy for defect** | True, and the standard proxy in this literature. Undetected defects are invisible to us — which is precisely what the test-gap analysis (RQ6) is designed to surface |
| **Co-change as "the IA camp's ground truth"** | It is our reconstruction of their label, not their tool's output. We reimplement the standard association-rule formulation and say so; we do not claim to have run RIPPLE |
| **Suite composition changes over time** | Tests are added and deleted within the window; the candidate set is a trailing-window observation, and `new_test` / deleted-test rules are explicit (§21.3) |

### 26.4 Conclusion validity — *are the statistics sound?*

| Threat | Our position |
| --- | --- |
| **Multiple comparisons across many baselines** | Holm–Bonferroni across the baseline family |
| **Significance without practical significance** | Cliff's delta reported alongside every *p*-value, with standard interpretation thresholds |
| **Non-independence of instances within a repo** | Per-repo random-effects analysis; per-repo results published so no mega-repo drives the aggregate |
| **Seed variance in learned models** | Five seeds, mean ± std |
| **Extreme class imbalance (1 positive per 200–2,000 candidates)** | Ranking metrics rather than accuracy; `scale_pos_weight` / focal loss; prevalence published |
| **Analysis-plan flexibility** | Pre-registered analysis plan committed before final runs (T6.12) |

---

## 27. Reproducibility & Artifact-Evaluation Readiness

`[merged v1 T5.6 + new]`

| Requirement | How it is met |
| --- | --- |
| One-command reproduction | `docker compose up` / `make all` on a 3-repo mini-corpus, **<15 minutes** (reviewers will not wait longer) |
| Every table regenerable | `analysis/` holds **one script per table or figure**, writing to `paper/generated/`. `make tables` regenerates everything. **If a number cannot be regenerated by a script in `analysis/`, it does not go in the paper** |
| Determinism | Seeds fixed, dependencies pinned, **no LLM calls in the reproducible pipeline**, tree-sitter grammars pinned, Graphify commit SHA recorded in `GRAPHIFY_COMMIT.txt` |
| Environment | `ENVIRONMENT.md` — pinned versions, hardware, wall-clock per stage |
| Instructions | `REPRODUCE.md` — exact commands, expected outputs, runtime estimates |
| Data availability | Zenodo DOI + HuggingFace + `br-bench-lite` under 1 GB |
| Citability | `CITATION.cff`, DOI in the camera-ready |
| Collection tooling | Harvester and parsers open-sourced with re-creation instructions |
| FAIR | Explicit statement in the paper |
| Licences | CC-BY 4.0 data / MIT code, `NOTICE` crediting `safishamsi/graphify` |
| AI-usage disclosure | Acknowledgements, per ACM/IEEE policy, with scope of use stated |

**The bar to design against:** a reviewer should be able to `pip install`, run one command, and see a number from the paper appear on their screen inside ten minutes. On the Data & Tool track, that experience *is* the review.

---

## 28. Novelty Positioning Against the Approved Reference List

`[new]` — the merge brief asks for exactly one paragraph of novelty framed narrowly and defensibly, plus a differentiation against each of the seven approved references. Both are below.

### 28.1 The novelty statement

> Change impact analysis has been evaluated for three decades against labels derived from developer behaviour — files edited together, elements co-changed — or from static reachability, because no public dataset linked a code change to the individual tests that its introduction actually caused to fail. **BlastRadius contributes that dataset.** We mine GitHub Actions at pull-request granularity, resolve per-test verdicts at both head and base commits, filter flakiness through four independent mechanisms, and validate a subset causally by container re-execution, producing the first public, execution-grounded, PR-anchored, multi-language change-impact benchmark. Our claim is not a new impact-analysis algorithm; it is a **measurement**: that co-change sets, static reachability sets, and fault-revealing sets are substantially disjoint, and that this divergence is systematic in the change characteristics practitioners most need help with. The predictor we ship is a demonstration that the dataset supports learning, not a claim of state of the art.

Note what the statement does *not* claim: no novel algorithm, no state-of-the-art model, no soundness guarantee. **A narrow claim that is fully supported beats a broad one that is partially supported**, and this claim is supported by artefacts a reviewer can download.

### 28.2 Differentiation against each approved reference

| # | Reference | What it does | How BlastRadius differs |
| --- | --- | --- | --- |
| 1 | **Borg, Wnuk, Regnell & Runeson (2017)**, *Supporting change impact analysis using a recommendation system: an industrial case study in a safety-critical context*, TSE 43(7) | Recommendation-system CIA validated in one industrial safety-critical setting; ground truth from issue/change-request records | **Different ground truth and different population.** Ours is observed CI test failure, not recorded change requests; public multi-project corpus, not one proprietary system. Their evaluation cannot be reproduced by others; ours ships as a DOI |
| 2 | **Huang, Jiang, Luo, Chen, Zheng, Jia & Huang (2022)**, *Change-patterns mapping: a boosting way for change impact analysis*, TSE 48(7) | Mines change patterns from history to boost CIA accuracy; labels are **co-change** | **Different dependent variable.** They predict which elements change together; we predict which tests go red. Their approach is reimplementable as our B7 baseline, and RQ1 measures exactly how far their label class sits from fault revelation |
| 3 | **Dai, Wang, Jin, Gong & Yang (2022)**, *An improving approach to analyzing change impact of C programs*, Computer Communications 182 | Static CIA for C with improved dependency modelling | **Different language, different validation.** C, static-only, no CI-outcome validation and no test-level output. We are build-free, Java/Python, and validated against execution |
| 4 | **Zhao, Yang, Xiang & Xu (2002)**, *Change impact analysis to support architectural evolution*, JSME 14(5) | Architectural slicing over architecture description; impact at component granularity | **Different granularity and different evidence.** Architecture-level and analytical; we are method-level and empirical. Their work is a conceptual ancestor of our L1/L2 layers and should be cited as such rather than as a competitor |
| 5 | **Hunsen, Lochau, Schaefer & Schulze (2016)**, *Modular change impact analysis for configurable software*, ICSME | Variability-aware CIA for configurable/SPL systems | **Orthogonal.** Their problem is `#ifdef`-style configuration space; ours is configuration-*agnostic* but execution-grounded. Their variability insight is a good lens on our config-change stratum in RQ2 |
| 6 | **Zhang, Gu, Lin & Zhao (2008)**, *Change impact analysis for AspectJ programs*, ICSM | Atomic-change decomposition for aspect-oriented Java | **Language-feature-specific and unvalidated against execution.** Their atomic-change taxonomy is genuinely useful and directly informs our change taxonomy (§18.2) — cite it there, generously |
| 7 | **Gupta & Gupta (2015)**, *Software change impact analysis: an approach to compute and prioritize impacted functions*, IJSSOE 5(2) | Computes and **prioritises** impacted functions | **Closest in output shape** — they also produce a ranking. But the ranking is validated on small examples without CI outcomes, and the unit is functions, not tests. This is the reference to compare *ranking method* against, and a good candidate for reimplementation if Phase 3 has slack |

**The one-line synthesis for Related Work:** *none of these seven validates its impact set against the tests that actually failed in a real continuous-integration pipeline, because until now no public dataset made that possible.*

### 28.3 Positioning against the closest non-approved work

Also required in Related Work, and already argued in §2.1: **RIPPLE** (different dependent variable), **Meta PTS** (proprietary, unreplicable), **RTPTorrent** (Travis-era, pre-2020, single-language, build-job-anchored), **GHALogs** (a log corpus, not a labelled corpus), **SWE-bench family** (agent evaluation, not prediction), and **Graphify** (an unvalidated zero-hop proximity heuristic — turned into our most interesting baseline). Each of the last six is `[unverified]` to the degree noted in §47 and must be checked before it appears in a submitted paper.

---

# Part VI — Engineering Reference

## 29. Graphify Forensic Reuse Map

`[merged v1 §Graphify Reuse Map + v2 Part A]`

**Repo:** `github.com/safishamsi/graphify` (branch `v8`) · **PyPI:** `graphifyy` · **Licence:** MIT · **Language:** Python 100% · **Source of truth:** the repo, its `ARCHITECTURE.md`, and the DeepWiki index of the module tree. **Verify against the live repo before implementing — this project ships fast (150 releases).**

`[unverified]` Volume II describes Graphify as a "75k-star repo". **Check the actual star count before that number appears in a paper, a slide, or a viva answer.** A specific popularity claim is trivially checkable and embarrassing to get wrong; the argument works just as well as "a widely-used open-source tool".

### 29.1 The headline finding — read this first `[v2 A.0]`

You suspected Graphify "also does something like that." It does — **and it does far less than it appears to.** This is the single most important fact in the project.

Graphify's PR impact lives in `graphify/prs.py`:

```
gh pr list --json ...          → PR metadata + statusCheckRollup    [fetch_prs, ~L189-201]
_classify(pr)                  → READY | CI-FAIL | STALE | WRONG-BASE  [~L98-113]
_parse_ci(statusCheckRollup)   → distils CI conclusion               [~L172-186]
compute_pr_impact(G, files)    → THE IMPACT STEP                     [~L348-378]
    for node, data in G.nodes(data=True):
        if _path_match(data["source_file"], changed_file):   [~L330-345]
            nodes_affected.add(node)
            communities_touched.add(data["community"])
build_community_labels(...)    → human-readable summary             [~L381-396]
```

**`compute_pr_impact` is a zero-hop operation.** It iterates the node set, matches `source_file` against the PR's changed paths, and reports which nodes *live inside the changed files* and which Leiden communities those nodes belong to. It does not traverse a single edge. It does not propagate impact. It has no concept of a test node. And it has never been validated against anything.

The `--conflicts` flag is the same primitive applied pairwise: two PRs "conflict" if their `communities_touched` sets intersect.

So what Graphify actually computes is **"which architectural neighbourhoods did you touch?"** — a genuinely useful developer-facing signal, and a completely different thing from **"which tests will go red?"**

| | Graphify `compute_pr_impact` | BlastRadius |
| --- | --- | --- |
| Traversal | Zero-hop (path match only) | k-hop transitive over typed edges |
| Output unit | Nodes in changed files + community IDs | Ranked individual tests |
| Test awareness | None — no test node type exists | Tests are first-class typed nodes |
| Edge semantics | `calls`, `imports`, `inherits`, `contains`, `references`, `mixes_in` | + `tests`, `tests_by_convention`, `tests_by_layout`, `co_changes`, `co_fails` |
| History | None | Evolutionary coupling + failure history |
| Learning | None (pure heuristic) | Learned ranker over execution outcomes |
| Validation | **Never evaluated against anything** | Evaluated against observed CI failures |
| Temporal | Working-tree graph only | Commit-pinned graph at base SHA |

**The reframing this unlocks.** You are not competing with Graphify; you are **completing** it. Their graph answers "what is connected to what." Yours answers "what breaks." The honest framing for the paper — and for a GitHub README their community would actually star:

> Graph-based impact tools tell you which parts of your architecture a change touches. They have never been able to tell you whether that matters, because there was no ground truth. BlastRadius supplies the ground truth and closes the loop.

**The one real danger** `[v1]`: a reviewer who knows the tool could say *"a widely-used open-source tool already does this."* **Your answer, and make sure it appears in Related Work verbatim:** Graphify's impact estimate is an unvalidated graph-proximity heuristic — never evaluated against observed CI outcomes, because no dataset existed to evaluate it with. BlastRadius contributes (a) the dataset that makes such evaluation possible, (b) the first evaluation of graph-proximity heuristics against fault revelation, and (c) a learned model that improves on them. **Turning your closest competitor into your most interesting baseline is the strongest possible move here.** Do it deliberately and generously — cite them well, run their tool fairly, report whatever you find.

### 29.2 Module-by-module verdict `[v2 A.1]`

Verdict: **TAKE** (use nearly as-is) · **ADAPT** (fork and extend) · **LEAVE** (delete from the fork) · **BASELINE** (don't reuse — evaluate) · **PARK** (keep, don't use in v1).

**Core pipeline**

| Module | What it does | Verdict | Your action |
| --- | --- | --- | --- |
| `detect.py` | File discovery + type classification (code/doc/paper/image/video), skips sensitive files | **ADAPT** | Add `test` and `build` classification. The skip-sensitive-files logic is a security freebie when mining 300 untrusted repos |
| `extract.py` | tree-sitter AST extraction dispatcher; `extract_python`, `extract_java`, `extract_js`, … 20+ langs; call-graph second pass emitting `INFERRED` call edges; shebang dispatch for extensionless files | **TAKE** | This is the four weeks you save. **Do not rewrite** |
| `extractors/` | Per-language extractor package (`base.py` defines the pattern, then `csharp.py`, `elixir.py`, `zig.py`, …) | **TAKE + EXTEND** | Follow `base.py` to add test-aware extraction. The package migration makes adding one clean |
| `build.py` | Assembles extraction dicts → NetworkX graph; also `prefix_graph_for_global` for namespaced multi-repo IDs | **ADAPT** | Add commit-SHA pinning to graph metadata. `prefix_graph_for_global` is the cross-repo path later (§44) |
| `cluster.py` | Leiden community detection | **TAKE** | Free `same_community` feature. **Pin `--resolution`; report the value in the paper** |
| `dedup.py` | Ghost-duplicate merging via MinHash/LSH + Jaro-Winkler, same-file partition constraint | **TAKE** | You will hit duplicate nodes; this already solves it. Also the right machinery for §16.5 move detection |
| `analyze.py` | Centrality → "God Nodes"; cross-community "surprising connections" | **TAKE** | God-node indicator and centrality go straight into the feature vector |
| `report.py` | `GRAPH_REPORT.md` generation | **LEAVE** | Human-facing narrative; irrelevant |
| `validate.py` | `validate_extraction` — schema enforcement, confidence-level checks, runs before `build_graph` | **TAKE** | Extend the schema with your node/edge types and let their validator enforce it. Free correctness gate |

**The high-value finds** — the four you would not have guessed were there, solving problems on the critical path.

| Module | Why it matters to you |
| --- | --- |
| **`ids.py`** | Deterministic node-ID normalization using an **NFKC + casefold** recipe, cross-platform stable, single source of truth. `_file_node_id` qualifies a stem with parent-directory context to prevent collisions. There is even a `tests/test_id_normalization_contract.py` enforcing the contract. **Exactly the machinery `normalize_test_id()` needs** (T1.1g), battle-tested across 36 grammars. Do not write your own normalizer — extend theirs and inherit their contract test |
| **`symbol_resolution.py` + `resolver_registry.py`** | A `LanguageResolver` **plugin system** for deterministic cross-file symbol resolution. Language-specific passes register into it (Ruby receiver-type inference, JS/TS import-guarded cross-file calls). **This means test-binding is a registered resolver plugin, not a fork hack** — clean, upstreamable, and Java `FooTest → Foo` binding sits exactly where such logic belongs (§29.6) |
| **`scip_ingest.py`** | Ingests **SCIP** JSON — Sourcegraph's precise code-intelligence format. A serious upgrade path: `scip-java` and `scip-python` produce *compiler-accurate* symbol graphs, not tree-sitter heuristics. For the Java subset this gives precision no AST-only approach can match, and it feeds a graph-quality ablation — *"heuristic AST graph vs precise SCIP graph — how much does graph precision buy you?"* — that nobody has run against CI outcomes (**RQ5**, T2.6) |
| **`security.py`** | `validate_url`, `safe_fetch` with size caps and timeouts, `validate_graph_path` (path-traversal guard), `sanitize_label` (strips control chars, caps at 256, HTML-escapes), SSRF protection. **You are about to clone and parse 300 repositories you did not write.** Adversarial filenames, control characters in identifiers, and XML-entity bombs are real; their `.csproj`/XAML extractors already pre-screen `DOCTYPE`/`ENTITY` for XML DoS. Keep all of it, and cite it in the ethics/threats section |

**Interfaces & integration**

| Module | What it does | Verdict | Your action |
| --- | --- | --- | --- |
| `cache.py` | SHA-256 semantic cache; **zero-node skip** (won't cache a file that produced no nodes, preventing poisoned entries) | **TAKE** | The zero-node skip is subtle bug-avoidance you'd have taken a week to discover. Makes commit-pinned incremental rebuilds viable |
| `watch.py` | Filesystem watcher for live re-sync | **LEAVE** | You rebuild at commits, not on save |
| `serve.py` | MCP server exposing `query_graph`, `get_node`, `get_neighbors`, `shortest_path`, `list_prs`, `get_pr_impact`, `triage_prs`; stdio + HTTP transports, API-key auth, stateless mode | **ADAPT** | Add one tool: `predict_blast_radius`. A Claude-native interface for ~40 lines, plus a demo that runs *inside* Claude Code — memorable for reviewers and viva panels |
| `prs.py` | GitHub PR fetch via `gh` CLI; `_parse_ci` distils `statusCheckRollup` (maps `CANCELLED`/`TIMED_OUT` → `FAILURE`); `_path_match` with path-boundary correctness (`config.py` must not match `g.py`); `compute_pr_impact` | **BASELINE + harvest 2 functions** | Use the *module* as Baseline T3.7. But lift `_parse_ci` and `_path_match` into the harvester — both solve exact problems on the critical path, and `_path_match` has a real test suite behind it (`tests/test_prs.py` L131-149) |
| `global_graph.py` | Cross-repo graph merging at `~/.graphify/global-graph.json`; `prefix_graph_for_global` namespaces IDs as `repoA::node_id` with `local_id` preserved; manifest with SHA-256 change detection; cross-repo library-node dedup by label | **PARK** | Not needed for v1. **This is the cross-repo extension** (§44) — the infrastructure for supply-chain blast radius already exists. Note it and move on |
| `manifest_ingest.py` | Parses `pyproject.toml`, `go.mod`, `pom.xml` → canonical package nodes with `depends_on` edges, one hub node per package | **TAKE** | Dependency bumps are a large, distinctive class of CI failure and one the proxies will be worst at. Package nodes for free (T2.7) |
| `callflow_html.py` / `tree_html.py` / HTML viz | vis.js interactive graph, Mermaid call-flow, D3 collapsible tree | **ADAPT** | Fork the vis.js view for the demo (T5.3) rather than starting from a blank D3 canvas. Recolour for changed / predicted-affected / actually-failed |

### 29.3 Take / Leave / Build summary `[v1]`

**✅ Take — roughly four weeks of engineering for free**

| Component | Why it matters to BlastRadius |
| --- | --- |
| tree-sitter AST extraction, 36 grammars | Multi-language parsing without writing a single parser; directly gives Java + Python + TypeScript coverage |
| Runs fully offline for code-only corpora | Their docs are explicit: code is processed locally via tree-sitter, no API key. A *reproducibility gift* — deterministic and free |
| NetworkX node-link `graph.json` | Standard format, directly loadable into PyTorch Geometric via `from_networkx`. No conversion layer |
| SHA-256 content cache + `--update` | Incremental rebuilds are the difference between 10 s and 10 min per instance |
| Leiden community detection | Free `same_community` feature and a ready-made module-level abstraction |
| Confidence tagging (`EXTRACTED`/`INFERRED`/`AMBIGUOUS`) | Excellent precedent for label-provenance tiers. Mirror the pattern (T1.9) |
| `ProcessPoolExecutor` parallel extraction | Already GIL-free multiprocessing. Do not rewrite it |
| MCP server scaffold | `query_graph`, `get_node`, `get_neighbors`, `shortest_path` already exist. Add one tool for a Claude-native interface |
| `graph.html` visualiser | A working interactive graph view. Fork it rather than starting from a blank D3 canvas |
| `graphify prs` / `get_pr_impact` / `--conflicts` | Not for reuse — **for use as a baseline** (T3.7) |

**❌ Leave**

| Component | Why |
| --- | --- |
| LLM semantic-extraction pass (Pass 3) | Non-deterministic. Fatal for a reproducible artifact and a gift to any reviewer looking for a reason to reject. Rip it out entirely |
| Video/audio/PDF/image/Office extraction | Irrelevant, heavy dependencies |
| Obsidian / wiki / SVG / GraphML exporters | Irrelevant |
| Neo4j / FalkorDB push | NetworkX + DuckDB is enough at this scale; a graph DB is a week you do not have (§19.2) |
| Query logging, `--dedup-llm`, global graph registry | Noise (global graph is PARKed rather than deleted — §44) |

**🔨 Build — the actual research contribution on top**

1. **Commit-pinned graph construction** — graph at an arbitrary SHA via `git worktree`, with incremental reuse across consecutive commits. Graphify has no notion of history; this is the biggest gap.
2. **Test-node typing and canonical `test_id` binding** — the join between graph and CI outcome. Does not exist anywhere in Graphify and is the technical heart of the project.
3. **Historical edge types** — `co_changes`, `co_fails`, weighted by evolutionary coupling.
4. **Label integration** — attaching fault-revelation outcomes to test nodes.
5. **Feature extraction layer** — the graph-distance features that feed the model.
6. **The predictor itself.**

### 29.4 Delete on day one `[v2 A.1]`

`llm.py` · `transcribe.py` · `ingest.py` · `file_slice.py` · `semantic_cleanup.py` · `reflect.py` (work-memory/LESSONS) · `mcp_ingest.py` · `pg_introspect.py` · Obsidian/wiki/SVG/GraphML exporters · Neo4j/FalkorDB push · all cloud backends · query logging.

**Rationale for deleting `llm.py` specifically, in one sentence you can put in the paper:** *"We disable Graphify's LLM semantic-extraction pass and use only its deterministic tree-sitter path, so that every graph in our dataset is exactly reproducible from source."* That converts a deletion into a methodological strength.

### 29.5 Their test suite is a gift `[v2 A.1]`

Keep and extend, do not delete:

- `test_java_type_resolution.py` — Java FQN disambiguation, `_JAVA_BUILTIN_TYPES` noise filtering
- `test_python_import_resolution.py` / `test_js_import_resolution.py`
- `test_symbol_resolution.py`
- `test_id_normalization_contract.py` — **inherit this for your test-ID contract**
- **`test_phantom_cross_package_call.py`** — a regression test against *false-positive cross-package call edges*. Phantom edges are precisely what would inflate the reachability baseline and turn graph features into noise. **Somebody already fought this battle; keep the test** (and see T2.8, which turns it into a measured metric)
- `tests/fixtures/sample.java`, `sample.cs`, `sample.ex`, … — ready-made parser fixtures

Run `uv run pytest tests/ -q` after every strip operation. **If you break `test_phantom_cross_package_call.py`, you have broken graph quality and you will not notice for six weeks.**

### 29.6 Design: the `TestResolver` plugin `[v2 A.3]`

The technical heart of the fork, and it belongs in their plugin system, not bolted on top.

```python
# graphify/test_resolution.py
from graphify.resolver_registry import LanguageResolver, register

class TestResolver(LanguageResolver):
    """Types test nodes and binds them to canonical CI test IDs."""

    def resolve(self, graph, ctx):
        for nid, data in graph.nodes(data=True):
            kind = self._classify(data, ctx)
            if kind:
                data["node_type"] = kind
            if kind == "test":
                data["test_id"] = self._canonical_test_id(data, ctx)
                self._link_to_subject(graph, nid, data, ctx)

    # --- classification -------------------------------------------------
    def _classify(self, data, ctx):
        p = data.get("source_file", "")
        if _PATH_TEST_RE.search(p):            # src/test/java/**, tests/**, *_test.py, *.spec.ts
            return "test"
        if _BUILD_RE.search(p):                # pom.xml, build.gradle, pyproject.toml
            return "build"
        if _CI_RE.search(p):                   # .github/workflows/**, tox.ini, Makefile
            return "config"
        if data.get("file_type") == "code":
            return "source"
        return None
```

**Three binding strategies, in confidence order.** Emit all three with distinct confidence; let the model learn which to trust.

| Strategy | Edge | Confidence | Mechanism |
| --- | --- | --- | --- |
| Direct dependency | `tests` | `EXTRACTED` | The test node has a `calls` or `imports` edge to the subject. Reuse their existing resolvers — for Java this is FQN resolution, already implemented and tested |
| Naming convention | `tests_by_convention` | `INFERRED` @ 0.85 | `FooTest → Foo`, `test_bar.py → bar.py`, `Baz.spec.ts → Baz.ts`. Cheap, high-recall, moderate precision |
| Directory mirroring | `tests_by_layout` | `INFERRED` @ 0.65 | `src/test/java/com/x/FooTest.java ↔ src/main/java/com/x/Foo.java`. Catches what the other two miss in conventional Maven layouts |

**Canonical test ID** — the join key to CI outcomes; it must round-trip both ways.

```
Java:       {package}.{Class}#{method}     →  com.example.FooTest#testBar
Python:     {module_path}::{Class}::{func} →  tests/test_foo.py::TestFoo::test_bar
TypeScript: {spec_path}::{describe}::{it}  →  src/foo.spec.ts::Foo::renders
```

Then run it through Graphify's `ids.py` NFKC + casefold normalizer to inherit their cross-platform stability guarantees.

**The metric that decides whether the project works: binding rate.** For every `test_id` observed in CI outcomes, does a graph node exist with that ID? **Measure it in Week 5** and put it on the dashboard. Below ~70% and graph features are mostly missing data — at which point you widen the conventions or drop the affected repos. **Do not discover this in October.**

### 29.7 The surgical fork plan `[v2 A.2]`

Carried in full at **§10.1 (T2.1)**, including the bash sequence, the ordered ten-step edit list, and the **1,200–2,000 LOC added against ~15,000+ inherited** ratio that is the whole argument for forking rather than building.

---

## 30. Full Tech Stack

`[v1]`

| Layer | Choice | Notes |
| --- | --- | --- |
| Language | Python 3.11 | 3.12 breaks Graphify's `leiden` extra |
| Package manager | `uv` | Graphify's own toolchain; fast, lockfile-based |
| Mining | `requests` + custom rate governor, `PyDriller` | PyDriller for Git history; raw REST for GHA |
| Parsing | `tree-sitter` (via Graphify fork), `lxml`, `javalang`, `ast` | JUnit XML via lxml |
| Graph | `NetworkX` 3.x, `igraph` (Leiden) | Node-link JSON for interchange |
| Storage | **DuckDB + Parquet** | Do not use MongoDB or Postgres here. DuckDB gives SQL over Parquet with zero server, handles tens of millions of rows on a laptop, and is what the MSR community increasingly ships (§19.2) |
| ML (tabular) | `LightGBM`, `Optuna`, `SHAP` | Primary model |
| ML (graph) | `PyTorch` 2.x, `PyTorch Geometric` | R-GCN / HGT |
| Stats | `scipy`, `statsmodels`, `cliffs-delta` | Wilcoxon, Holm–Bonferroni, effect sizes |
| Re-execution | `Docker`, `docker-py` | Gold subset |
| API | `FastAPI` + `uvicorn` | |
| CLI | `Typer` + `Rich` | |
| Frontend | Next.js 15, TypeScript, Tailwind, `react-force-graph` | Vercel deploy. Library choice revisited in **D-15** |
| Dashboard | `Streamlit` | Internal corpus monitoring only |
| Figures | `matplotlib` + `seaborn`, vector PDF | No screenshots in the paper |
| Paper | LaTeX, `IEEEtran` 10pt conference | Overleaf, shared across the team |
| Artifact | Zenodo (DOI), HuggingFace Datasets, GitHub | CC-BY 4.0 data / MIT code |
| Dev | Claude Code, Git, GitHub Projects, WSL2 | |
| `[new]` Optional precision tier | `scip-java` / `scip-python` via Graphify's `scip_ingest.py` | Java subset only, for RQ5 |
| `[new]` AST differencing (gold only) | GumTree | Validation of the Tier-1 change taxonomy (§18.1) |

### 30.1 Hard constraints to design around `[v1]`

- **Storage:** budget 200–500 GB for raw logs. Compress aggressively, prune success-run logs after parsing, keep only failure logs long-term. `[new]` Plus 60–120 GB of repo mirrors and ≤150 GB of graph store (§19.4).
- **Compute:** everything except the GNN and the gold re-execution runs on a laptop. The GNN needs a GPU — use Colab or Kaggle free tiers with checkpointing to Drive.
- **Rate limits:** 5,000 req/hr/token. Three tokens. Plan the harvest schedule around it.
- **Network:** the harvester must survive hostel Wi-Fi. Resumable cursors, aggressive retry, nightly mirror.

---

## 31. Data Schemas

`[v1]` — **freeze these in Week 2.** Schema churn after Phase 1 will cost you a week (**T18**).

### `instances.parquet` — one row per (head_sha, workflow_run)

```
instance_id            string   PK, sha256(repo|head_sha|run_id)
repo                   string   "owner/name"
language               string   java | python | typescript
pr_number              int64    null for push events
head_sha               string
base_sha               string
base_run_id            int64    null if no base run found
base_run_distance      int32    commits between base_sha and the run actually used
run_id                 int64
workflow_id            int64
workflow_name          string
run_conclusion         string   success | failure | cancelled | ...
run_started_at         timestamp
changed_files          list<struct<path:string, status:string, additions:int32,
                                   deletions:int32, hunks:list<struct<start:int32,end:int32>>>>
changed_symbols        list<string>
n_files_changed        int32
n_lines_changed        int32
touches_test_file      bool
touches_build_config   bool
touches_ci_config      bool
is_dependency_bump     bool
is_docs_only           bool
is_formatting_only     bool
author_login           string   pseudonymised on release
```

`[new]` **Added columns** (all additive, agreed at the Week 2 freeze):
```
n_matrix_legs          int32    matrix-build aggregation (D-12)
frontier_truncated     bool     §18.4 explosion guard fired
is_bot_pr              bool     Dependabot / Renovate (T0.6)
bot_name               string   null unless is_bot_pr
event_type             string   pull_request | push | pull_request_target
is_default_branch      bool     survivorship analysis (T2)
graph_sha              string   the SHA the graph was built at (= base_sha normally)
parse_failure_rate     float32  per (repo, sha) at graph build time
frame_version          string   which frozen frame this instance belongs to (T0.8)
actual_changed_files   list<string>   file-level ground truth (T1.8, §21.4)
```

### `outcomes.parquet` — one row per (instance, test) observation

```
instance_id            string   FK
test_id                string   canonical "module::class::method"
test_file              string   repo-relative, null if unresolved
status_head            string   pass | fail | error | skip | absent
status_base            string   pass | fail | error | skip | absent
is_fault_revealing     bool     status_base != fail AND status_head in (fail, error)
flakiness_score        float32  trailing 30d flip rate
same_sha_flip          bool
label_source           string   annotation | artifact | log | reexec
parser_confidence      float32
duration_s             float32
failure_message_hash   string   sha256, message stored separately
split_strict           bool
split_permissive       bool
```

`[new]` **Added columns:**
```
new_test               bool     exists at head, not at base (§21.3)
suspect_unrelated      bool     coverage-free DeFlaker heuristic (T3 filter 4)
excluded_own_file      bool     test's own file was in the changed set (§18.2 leakage rule)
binding_strategy       string   tests | tests_by_convention | tests_by_layout | unbound
```

### `graph_nodes.parquet` / `graph_edges.parquet` — per (repo, sha)

```
# nodes
repo, sha, node_id, label, node_type {source|test|config|build},
source_file, test_id (nullable), loc, complexity, churn_90d, age_days,
community_id, pagerank, degree
```
`[new]` extended per §16.2: `+ kind, fqn, body_sha, content_sha, parse_status, is_generated, is_vendored, annotations, has_dynamic_boundary, n_dynamic_sites, start_line, end_line`

```
# edges
repo, sha, src, dst, edge_type {imports|calls|inherits|tests|
tests_by_convention|co_changes|config_of}, confidence, confidence_score, weight
```
`[new]` extended edge_type domain per §16.3: `+ contains, implements, overrides, instantiates, reads_field, writes_field, throws, tests_by_layout, co_fails, covered_by, configured_by, depends_on, wires, runs_in`

### `cochange.parquet` — the comparison arm

```
repo, window_end, file_a, file_b, support, confidence, lift, n_cochanges
```

### `gold.parquet` — causal subset

```
instance_id, test_id, verdict_base_run1, verdict_base_run2,
verdict_head_run1, verdict_head_run2, causal_label, env_digest, notes
```

### `[new]` `identity_map.parquet` — node identity across SHAs (§16.5)

```
repo, from_sha, to_sha, old_node_id, new_node_id,
kind {renamed|moved|split|merged}, confidence, evidence
```

### `[new]` `graph_index.parquet` — snapshot/delta index (§19.3)

```
repo, sha, snapshot_path, delta_paths list<string>, n_nodes, n_edges,
built_at, incremental_from, communities_inherited, graphify_commit
```

### Release hygiene `[v1]`

- Pseudonymise `author_login` with a salted hash; publish the salt separately or not at all. Document the choice.
- Store `failure_message` in a separate file — it can contain absolute paths and occasionally environment detail. Scan for secrets with `gitleaks` before release.
- Ship a `schema.json` and a `validate.py` that checks any Parquet file against it.

---

## 32. Evaluation Protocol

`[v1]` — **freeze before Phase 4.**

**Splits.** Time-based. Train ≤ 2026-08-31, validate 2026-09-01 → 2026-09-30, test ≥ 2026-10-01. Additionally, leave-one-project-out for the cross-project regime. **Never random-split.**

**Primary metric.** Recall@k where k ∈ {1%, 5%, 10%, 20%} of the test suite — the practitioner-facing framing.

**Secondary.** APFD/APTF, MAP, NDCG@10, safety violation, precision violation, suite reduction %, simulated CI-minutes saved. `[new]` Plus MRR, Precision@k, Brier/ECE, and abstain rate (§25.2).

**Statistics.** Five seeds. Wilcoxon signed-rank on paired per-instance scores. Holm–Bonferroni across the baseline family. Cliff's delta for effect size, interpreted with the standard thresholds. Bootstrap 95% CIs on all headline numbers.

**Robustness.** Every headline result reported on `strict`, with `permissive` and `raw` in an appendix table. **If the finding flips between splits, that is the finding — report it.**

**Negative controls.** Docs-only and formatting-only changes should yield near-zero predicted failures. Report this; it is a cheap, convincing sanity check.

`[new]` **Two additional protocol commitments:**
- **Hyperparameters are tuned on validation only**, never on test. This includes $\gamma,\beta,\alpha$ in the heuristic scorer (§18.5) and every LightGBM/Optuna sweep.
- **The analysis plan is pre-registered** in a dated repo file before final runs (T6.12).

---

## 33. Repository Layout

`[v2 Part D]`

```
blastradius/
├── README.md                  # the paper's shop window — write it early
├── CITATION.cff               # required for the DOI citation
├── LICENSE                    # MIT (code)
├── NOTICE                     # graphify attribution + pinned commit
├── ENVIRONMENT.md             # pinned versions, hardware, runtimes
├── REPRODUCE.md               # exact commands, expected outputs, runtimes
├── DATASHEET.md               # Datasheets-for-Datasets
├── Makefile                   # make all / make tables / make figures
├── pyproject.toml
├── docker/
│   ├── Dockerfile
│   └── compose.yml
├── vendor/
│   └── graphify-br/           # the fork (git submodule or vendored)
├── src/
│   ├── harvest/  ratelimit.py daemon.py liveness.py workflow_triage.py
│   ├── parse/    test_ids.py junit_xml.py annotations.py log_*.py changeset.py
│   ├── label/    faults.py flaky.py cochange.py splits.py
│   ├── graph/    commit_graph.py test_resolution.py query.py enrich.py
│   ├── features/ graph_feats.py change_feats.py history_feats.py
│   ├── models/   lgbm.py gnn.py rerank.py
│   ├── eval/     baselines/ metrics.py stats.py
│   ├── gold/     reexec.py
│   └── api/      main.py cli.py
├── analysis/                  # ONE script per paper table/figure
│   ├── table1_corpus.py
│   ├── table2_divergence.py
│   ├── fig1_teaser.py
│   └── ...
├── tests/
│   └── fixtures/              # real logs, real XML, hand-labelled
├── data/                      # gitignored
│   ├── raw/ interim/ processed/ gold/ graphs/
├── paper/                     # Overleaf mirror
└── web/                       # Next.js demo
```

`[new]` Additions implied by this document: `src/harvest/attrition.py` (T0.7) · `src/graph/identity.py` (§16.5) · `analysis/leakage_audit.py` (T4.7) · `reports/graphify_baseline.md` (T3.7) · `PREREGISTRATION.md` (T6.12) · `corpus/` (bare mirrors, gitignored, §15.1).

**The `analysis/` convention matters more than it looks.** One script per table or figure, each writing to `paper/generated/`. `make tables` regenerates everything. **If a number is in the paper and cannot be regenerated by a script in `analysis/`, it does not go in the paper.** This is what makes the artifact credible and what saves you during the rebuttal period when a reviewer asks "what if you exclude repo X?"

---

## 34. Claude Code Working Protocol & Prompt Library

### 34.1 The nine rules `[v1]`

You are the systems designer. Claude Code is the implementer. This protocol is what keeps that relationship productive over three months.

**Rule 1 — One task, one session, one file (or one tightly-coupled pair).** Never hand Claude Code "build the harvester." Hand it "implement `TokenPool` in `src/harvest/ratelimit.py` with quota-aware round-robin selection, honouring `X-RateLimit-Remaining` and `Retry-After`; write pytest tests against a mocked session." **Task granularity is the single biggest determinant of output quality.**

**Rule 2 — Context injection at the top of every prompt.** Every task prompt starts with: project one-liner, the file being modified, the relevant schema fragment, and the acceptance criterion. Do not assume continuity across sessions.

**Rule 3 — Schema first, code second.** Write the Parquet/dataclass schema, get it reviewed by all three of you, *then* write the code that produces it. Retrofitting a schema across 40 files is a week you cannot afford.

**Rule 4 — Every data-touching function gets a test with a real fixture.** Not a mock. A real, checked-in, 200-line log file with a hand-written expected output. Your parsers are the foundation of the dataset's credibility; parser bugs are silent and poison everything downstream.

**Rule 5 — Never let Claude invent data.** Especially in the paper. Every number in every table traces to a script in `analysis/` that regenerates it. If a number cannot be regenerated by `make tables`, it does not go in the paper. **Extend this to the roadmap itself: verify anything Claude asserts about a repo, a deadline, or a related paper before it reaches a submission.** (Everything tagged `[unverified]` in this document is an instance of that rule.)

**Rule 6 — Determinism is a requirement, not a preference.** Seed everything. Pin every dependency. No LLM calls in the reproducible pipeline. If a stage is not deterministic, it is not in the artifact.

**Rule 7 — PowerShell vs WSL.** Do the harvesting and ML in WSL2 (Docker, long-running daemons, POSIX paths). Use PowerShell only for Windows-side tooling. **Tell Claude Code which shell you are in at the top of the prompt** — mixed-shell confusion wastes real time.

**Rule 8 — Commit at every green test.** Small commits, conventional messages (`feat:`, `fix:`, `data:`, `paper:`). You will need `git bisect` when a parser change silently shifts your label counts.

**Rule 9 — Weekly integration checkpoint.** Every Sunday: all three branches merged, full pipeline run on the 3-repo mini-corpus, dashboard reviewed, next week's tasks assigned. **Non-negotiable. Three-person research projects fail at integration, not at implementation.** `[v2 T12]` Add: no branch lives longer than 5 days; the `test_id` contract test must pass on every merge.

### 34.2 The build sequence rule `[v1]`

> Harvester → parsers → labels → graph → features → baselines → model → demo → paper.

**Never work more than one stage ahead of validated data.** Building a GNN before you trust your labels is how projects die in October.

### 34.3 The context header `[v2 C.0]`

Paste at the top of every session. It never changes.

```
PROJECT: BlastRadius — execution-grounded change impact prediction for CI.
We mine GitHub Actions runs to build a dataset linking code changes to the
individual tests that actually failed, then predict that from a code graph.
Target: MSR 2027 Data & Tool Showcase, deadline 10 Nov 2026.

REPO LAYOUT:
  src/harvest/   GitHub API capture (raw → data/raw/*.jsonl.gz)
  src/parse/     Test-result parsers (→ TestOutcome records)
  src/label/     Labelling engine (→ instances/outcomes parquet)
  src/graph/     Commit-pinned graph builder over vendor/graphify-br
  src/features/  Feature extraction
  src/models/    LightGBM + PyG
  src/eval/      Baselines, metrics, statistics
  vendor/graphify-br/  Forked graphify (MIT), LLM pass removed

ENVIRONMENT: Python 3.11, uv, WSL2 Ubuntu (NOT PowerShell for this task),
DuckDB + Parquet for storage, pytest for tests.

HARD RULES:
- Determinism: seed everything, no LLM calls in the pipeline.
- Every data-touching function gets a pytest test against a REAL fixture
  file in tests/fixtures/, not a mock.
- Type hints everywhere. Google-style docstrings.
- No new dependencies without asking me first.
- If a schema is involved, show me the schema and STOP for approval before
  writing implementation code.

TASK: <paste one task below>
```

### 34.4 The prompt library `[v2 Part C]`

**C.1 — `T0.2a` Token pool**

```
TASK: Implement src/harvest/ratelimit.py.

Requirements:
- class TokenPool(tokens: list[str]) with round-robin selection weighted by
  remaining quota, read from X-RateLimit-Remaining / X-RateLimit-Reset.
- Function get_with_backoff(url, params=None, pool=...) -> requests.Response.
  This must be the ONLY place in the codebase that issues an HTTP request.
- Honour Retry-After on 429 and on GitHub secondary rate limits.
- Exponential backoff with full jitter, max 6 attempts, then raise.
- If all tokens are exhausted, sleep until the earliest reset, don't spin.
- Log every request as one JSON line to logs/requests.jsonl:
  {ts, url, status, token_idx, remaining, duration_ms, attempt}

Tests (tests/test_ratelimit.py, using responses or requests-mock):
- selects the token with the most remaining quota
- retries on 429 and succeeds on attempt 3
- raises after 6 failed attempts
- sleeps rather than spinning when all tokens are exhausted

Show me the TokenPool interface first, then wait for my approval.
```

**C.2 — `T1.1g` Test ID normalization** ⭐

```
TASK: Implement normalize_test_id() in src/parse/test_ids.py.

This is the join key between CI outcomes and graph nodes. It must be exact.

Canonical forms:
  Java:       {package}.{Class}#{method}      com.example.FooTest#testBar
  Python:     {path}::{Class}::{func}         tests/test_foo.py::TestFoo::test_bar
  TypeScript: {path}::{describe}::{it}        src/foo.spec.ts::Foo::renders

Input sources that must all normalize to the same string:
  - Maven Surefire XML:  <testcase classname="com.example.FooTest" name="testBar"/>
  - Maven console:       [ERROR] com.example.FooTest.testBar:42 expected...
  - pytest junit XML:    <testcase classname="tests.test_foo.TestFoo" name="test_bar"/>
  - pytest console:      FAILED tests/test_foo.py::TestFoo::test_bar - AssertionError
  - GH check annotation: path="tests/test_foo.py" title="TestFoo.test_bar"

Handle: parameterized tests (strip [0], [param=x] into a `params` field),
nested classes ($ in Java), pytest fixtures/subtests, ANSI escapes,
leading ISO-8601 timestamps from GH log lines.

Return a TestId dataclass with .canonical(), .params, .raw, .lang.
Reuse the NFKC+casefold normalization recipe from
vendor/graphify-br/graphify/ids.py — read that file first and match its
approach exactly so our IDs are consistent with graph node IDs.

Write a table-driven test with at least 30 (raw_input, expected_canonical)
pairs covering all six sources above.

Show me the TestId dataclass and 5 example normalizations before implementing.
```

**C.3 — `T1.3b` Fault-revealing set** ⭐

```
TASK: Implement compute_fault_revealing_set() in src/label/faults.py.

Given a workflow run at head_sha with base_sha, produce the set of tests
that this change caused to fail.

Algorithm:
1. T_head_fail = tests with status in {fail, error} at head_sha
2. Resolve the base run: the most recent run of the SAME workflow_id on
   base_sha. If none exists, walk ancestors of base_sha (max 10) and record
   base_run_distance. If still none, return status="no_base" and DO NOT
   emit labels for this instance.
3. T_base_fail = failing tests in that base run
4. T_reveal = T_head_fail - T_base_fail   # broken-trunk filter
5. Remove tests appearing in T_flaky (from detect_same_sha_flips)
6. Annotate each survivor with flakiness_score from the rolling window

Return FaultRevealingResult(reveal, base_fail, flaky, base_run_distance,
status, n_candidates).

Edge cases to handle explicitly and document in the docstring:
- head run was cancelled or timed out
- base run has no parsed test results at all (partial data — do NOT treat
  an empty base failure set as "base was green")
- test exists at head but not at base (newly added test) — label as
  fault_revealing=False, flag as new_test=True
- test exists at base but not head (deleted test) — exclude entirely
- multiple runs of the same workflow at head (matrix builds) — union the
  failures across matrix legs, but record n_matrix_legs

Test against tests/fixtures/label_cases/*.json — I will hand-construct
8 cases covering each edge case. Write the code so I can add cases as
plain JSON without touching the test file.
```

**C.4 — `T2.2c` Incremental commit-pinned graphs**

```
TASK: Implement src/graph/commit_graph.py.

Goal: build a code graph at an arbitrary commit SHA, fast enough to do it
for thousands of commits.

API:
  build_graph_at(repo_path, sha, cache_dir) -> Path   # returns graph json

Approach:
1. Use `git worktree add --detach {tmpdir} {sha}` — NOT clone-per-commit.
   Reuse a pool of worktrees; clean up with `git worktree remove`.
2. Look up the nearest previously-built graph for this repo by walking
   git ancestry (git merge-base --is-ancestor). If found within N=50
   commits, do an incremental build.
3. Incremental: `git diff --name-only {prev_sha} {sha}` gives changed files.
   Re-extract ONLY those via vendor/graphify-br's extract path, then splice
   into the cached graph: remove all nodes whose source_file is in the
   changed set, remove their incident edges, merge in the new subgraph,
   re-run symbol resolution ONLY for affected files.
4. Re-run clustering only if >5% of nodes changed; otherwise inherit
   community assignments.
5. Store graph metadata: {repo, sha, built_at, graphify_commit,
   n_nodes, n_edges, parse_failures, incremental_from}

Performance target: <10s per incremental build on a repo of ~2000 files.
Cold build may take minutes.

Correctness requirement: assert that an incremental build at sha X produces
the SAME graph as a cold build at sha X. Write this as a test over 5 real
commits of a small repo. If they diverge, the whole dataset is untrustworthy
— treat any divergence as a blocking bug.

Read vendor/graphify-br/graphify/cache.py and build.py first and reuse their
SHA256 cache rather than adding a second caching layer.
```

**C.5 — `T3.7` Graphify baseline**

```
TASK: Implement src/eval/baseline_graphify.py.

We evaluate stock graphify's PR impact heuristic against our CI-outcome
labels. Be scrupulously fair — this is a published tool and we report the
result neutrally.

1. Read vendor/graphify-br/graphify/prs.py, specifically compute_pr_impact
   (~L348-378) and _path_match (~L330-345). Reimplement its EXACT semantics
   against our graph objects — do not "improve" it. If our reimplementation
   differs from theirs in any way, document the difference in a docstring.

2. Its output is (nodes_affected, communities_touched). Derive two test
   rankings from it, since it doesn't rank tests directly:
   - GRAPHIFY-COMMUNITY: all test nodes whose community is in
     communities_touched, ranked by node degree
   - GRAPHIFY-DIRECT: only test nodes that are themselves in changed files
     (this will have near-zero recall; report it anyway as the floor)

3. Evaluate both with the same metrics as every other baseline:
   Recall@{1,5,10,20}%, APFD, MAP, safety violation, precision violation.

4. Produce a short markdown note in reports/graphify_baseline.md describing
   exactly what the heuristic computes, so I can paste an accurate
   description into Related Work.

Write it so that if graphify changes upstream, we can re-pin and re-run:
record the graphify commit SHA in the results file.
```

**C.6 — Reusable prompt template for any new task**

```
TASK: <one sentence goal>

FILE: <exact path>

INTERFACE:
  <function/class signatures you want>

BEHAVIOUR:
  <numbered algorithm steps>

EDGE CASES (handle explicitly, document in docstring):
  - <case 1>
  - <case 2>

TESTS (<path>):
  - <assertion 1>
  - <assertion 2>
  Use real fixtures in tests/fixtures/, not mocks.

ACCEPTANCE: <the one measurable thing that means this is done>

Before implementing, show me <the interface / the schema / 3 examples>
and wait for approval.
```

### 34.5 Prompt Library Expansion `[new]`

**C.7 — `T2.3b` TestResolver plugin + binding-rate metric** ⭐

```
TASK: Implement graphify/test_resolution.py in vendor/graphify-br as a
registered LanguageResolver, plus src/graph/binding_report.py.

Read vendor/graphify-br/graphify/resolver_registry.py and
symbol_resolution.py FIRST and follow their plugin contract exactly.

TestResolver.resolve(graph, ctx) must:
1. Classify every node as test | source | config | build (see §16.2 tiers).
2. For test nodes, set data["test_id"] via the canonical forms in §29.6,
   normalized through graphify/ids.py (NFKC + casefold).
3. Emit three binding edge types with fixed confidences:
   tests (1.0) / tests_by_convention (0.85) / tests_by_layout (0.65).
   Emit ALL applicable strategies, not just the highest — the model needs
   to see which fired.

binding_report.py must emit, per (repo, sha):
  {n_ci_test_ids, n_bound, binding_rate, by_strategy{}, unbound_sample[20]}

ACCEPTANCE: binding_rate computed and written to the dashboard for the
3-repo mini-corpus, plus 20 sampled unbound test_ids I can eyeball to
diagnose the failure mode.

This is threat T8. Show me the classification regexes before implementing.
```

**C.8 — `T3.8a` Divergence analysis**

```
TASK: Implement analysis/table2_divergence.py.

For each instance compute three sets at FILE granularity:
  C = co-change predicted set (top-k by confidence, cochange.parquet)
  R = static reachability set (k-hop over the graph, k=2 default)
  F = fault-revealing set (tests → their source files via bindings)

Report, with bootstrapped 95% CIs (10k resamples):
  |C∩F|/|C∪F|, |R∩F|/|R∪F|, precision/recall/F1 of C and R against F
Stratified by: language, n_files_changed bucket, change type, repo.
Significance: Wilcoxon signed-rank paired across instances,
Holm-Bonferroni across the comparison family, Cliff's delta.
Per-repo random effects so no single repo drives the result.

Writes ONE csv to paper/generated/table2_divergence.csv and ONE
LaTeX table. No numbers printed to stdout that aren't in the file.

ACCEPTANCE: `make tables` regenerates it from parquet with no manual steps.
```

**C.9 — `T4.7` Leakage audit**

```
TASK: Implement analysis/leakage_audit.py.

For every feature in src/features/, answer in a generated table:
  feature | uses_future_info? | window_respects_split? | evidence

Checks to implement:
1. Every trailing-window statistic must be computed with a cutoff at the
   instance's own run_started_at, NOT over the whole corpus.
2. Cross features (test failure rate GIVEN this file changed) must use only
   training-period instances.
3. Tests whose own source file is in changed_files must be excluded from
   the candidate set (excluded_own_file flag) — assert the flag is honoured
   everywhere downstream.
4. Duplicate-code check: near-duplicate files across train/test repos
   (MinHash, threshold 0.8) — report the overlap rate.

ACCEPTANCE: a generated markdown table I can paste into the paper appendix,
plus a hard pytest assertion that fails CI if check 3 is violated.
```

---

# Part VII — Delivery & Team

## 35. Master Task Graph

`[merged v1 + v2 Part G]` — each line is a self-contained micro-task. Copy one, add the §34.3 context header, hand it to Claude Code. ⭐ marks a task where getting it wrong invalidates downstream work.

### Week 0 — Harvester (Aug 4–10) 🔴
- [ ] `T0.1a` Export SEART query → `data/frame/repos_raw.csv`; document query in `QUERY.md`
- [ ] `T0.1b` Implement `src/harvest/liveness.py` — CI-liveness filter via `total_count`
- [ ] `T0.1c` Implement `src/harvest/workflow_triage.py` — classify workflows test/build/deploy
- [ ] `T0.1d` Produce `repos.csv` (300 candidates); manual review of top 50
- [ ] `T0.2a` Implement `TokenPool` with quota-aware round-robin
- [ ] `T0.2b` Implement `get_with_backoff()` — sole HTTP entry point
- [ ] `T0.2c` Add request logging + `--dry-run` budget estimator
- [ ] `T0.3a` SQLite cursor store + resume logic
- [ ] `T0.3b` PR + commits + runs capture loop → gzipped JSONL
- [ ] `T0.3c` Check-run annotations capture (priority: persists >90d)
- [ ] `T0.3d` Artifact capture with name/size filter
- [ ] `T0.3e` Job-log capture, failures prioritised
- [ ] `T0.3f` SIGTERM flush + daily MANIFEST.json
- [ ] `T0.3g` Deploy as cron daemon in WSL2 + redundant GHA scheduled harvester
- [ ] `T0.3h` `[v2]` Lift `_parse_ci` + `_path_match` from graphify `prs.py`
- [ ] `T0.4a` Directory contract + CHECKSUMS
- [ ] `T0.4b` Nightly rclone/rsync mirror; verify by restoring one file
- [ ] `T0.5a` Streamlit corpus dashboard
- [ ] `T0.6` `[v2]` Dependabot / bot-PR capture with `is_bot_pr` tagging
- [ ] `T0.7` `[new]` Attrition funnel instrumentation → `ATTRITION.json` + dashboard
- [ ] `T0.8` `[new]` Frame freeze + version tag before Phase 1

### Weeks 1–4 — Corpus & Ground Truth (Aug 10–Sep 6)
- [ ] `T1.1a` Build 40-log fixture corpus with hand-labelled expected output
- [ ] `T1.1b` `annotations.py` parser
- [ ] `T1.1c` `junit_xml.py` parser (Surefire + pytest)
- [ ] `T1.1d` `log_pytest.py` parser
- [ ] `T1.1e` `log_maven.py` parser
- [ ] `T1.1f` `log_gradle.py` parser
- [ ] `T1.1g` `normalize_test_id()` extending graphify `ids.py` + contract test ⭐
- [ ] `T1.1h` `resolve_test_file()` + binding-rate report ⭐
- [ ] `T1.1i` Per-parser coverage + precision report
- [ ] `T1.2a` Changed-file extraction with hunks
- [ ] `T1.2b` tree-sitter symbol-level change extraction
- [ ] `T1.2c` Change taxonomy flags (full taxonomy §18.2)
- [ ] `T1.3a` Base-run resolution with `base_run_distance` ⭐
- [ ] `T1.3b` Fault-revealing set computation (broken-trunk filter) ⭐
- [ ] `T1.3c` Same-SHA flip detection
- [ ] `T1.3d` Rolling flip-rate flakiness scoring
- [ ] `T1.3e` Three splits: strict / permissive / raw
- [ ] `T1.3f` Emit `instances.parquet` + `outcomes.parquet`
- [ ] `T1.4a` PyDriller co-change mining
- [ ] `T1.4b` Evolutionary coupling (support/confidence/lift)
- [ ] `T1.5a` Docker re-execution harness
- [ ] `T1.5b` Base/head double-run protocol + causal labelling
- [ ] `T1.5c` Observational-vs-causal agreement report ⭐
- [ ] `T1.6a` Schema validator + `schema.json`
- [ ] `T1.6b` Secret scan + pseudonymisation
- [ ] `T1.6c` HuggingFace dataset card + loader
- [ ] `T1.6d` Datasheet for Datasets
- [ ] `T1.7` `[v2]` Canary string + datasheet note
- [ ] `T1.8` `[new]` File-level ground-truth arm (`actual_changed_files`) ⭐
- [ ] `T1.9` `[new]` Label-provenance tiers mirroring graphify confidence vocabulary

### Weeks 3–7 — Graph Layer (Aug 24–Sep 20)
- [ ] `T2.1a` Fork Graphify v8 → `vendor/graphify-br/`, preserve LICENSE + NOTICE
- [ ] `T2.1b` Strip LLM pass and non-code extractors
- [ ] `T2.1c` Pin versions; re-run their test suite
- [ ] `T2.1d` `[v2]` Record `GRAPHIFY_COMMIT.txt`; follow the ordered fork sequence §10.1
- [ ] `T2.2a` `git worktree` commit-pinned checkout manager
- [ ] `T2.2b` Graph build at SHA → `graph_{repo}_{sha}.json`
- [ ] `T2.2c` Incremental rebuild via content hashing ⭐
- [ ] `T2.2d` Graph validation + parse-failure-rate gate
- [ ] `T2.2e` `[v2]` Incremental-vs-cold equivalence assertion (blocking) ⭐
- [ ] `T2.2f` `[new]` Snapshot + delta storage and `graph_index.parquet` (§19.3)
- [ ] `T2.3a` Node type classification (test/source/config/build)
- [ ] `T2.3b` `test_id` ↔ test-node binding as a registered `LanguageResolver` ⭐
- [ ] `T2.3c` `tests` / `tests_by_convention` / `tests_by_layout` edges
- [ ] `T2.3d` Extended edge-type schema (§16.3)
- [ ] `T2.3e` `[new]` Binding-rate report + dashboard tile ⭐ (**Gate 1.5**)
- [ ] `T2.4a` `co_changes` weighted edges
- [ ] `T2.4b` `co_fails` edges
- [ ] `T2.4c` Node attributes (churn, complexity, age, failure rate)
- [ ] `T2.5a` Query API primitives (§20.1 Q1–Q10)
- [ ] `T2.5b` DuckDB feature cache + benchmark
- [ ] `T2.6` `[v2]` SCIP precision tier on the Java subset (RQ5, optional)
- [ ] `T2.7` `[v2]` `manifest_ingest` package layer + `depends_on` edges
- [ ] `T2.8` `[new]` Phantom-edge rate measurement, 100 hand-checked edges/language
- [ ] `T2.9` `[new]` Graph-quality dashboard tiles (binding / parse-fail / orphan / phantom)
- [ ] `T2.10` `[new]` Node identity map (`identity_map.parquet`, §16.5)
- [ ] `T2.11` `[new]` Dynamic-boundary flagging (§17.3)

### Weeks 6–10 — Measurement (Sep 14–Oct 11)
- [ ] `T3.1` Retest-all baseline
- [ ] `T3.2` Random + path-similarity baselines
- [ ] `T3.3` Static k-hop reachability baseline (k ∈ {1,2,3,∞})
- [ ] `T3.4` Ekstazi on Java gold subset
- [ ] `T3.5` Historical-failure-frequency baseline — **build early, know the number**
- [ ] `T3.6` Co-change association-rule baseline
- [ ] `T3.7a` `[v2]` GRAPHIFY-COMMUNITY baseline ⭐
- [ ] `T3.7b` `[v2]` GRAPHIFY-DIRECT baseline (the floor)
- [ ] `T3.7c` `[v2]` `reports/graphify_baseline.md` accurate description for Related Work
- [ ] `T3.7d` `[new]` BLASTRADIUS-HEURISTIC baseline (§18.5, unlearned)
- [ ] `T3.8a` Jaccard / P / R / F1 of each proxy vs fault-revealing set
- [ ] `T3.8b` Stratified analysis (language, change size, change type)
- [ ] `T3.8c` Wilcoxon + Holm–Bonferroni + Cliff's delta
- [ ] `T3.8d` Per-repo random-effects check
- [ ] `T3.8e` `[new]` Reach-curve figure justifying the depth cap (§18.4)
- [ ] `T3.9a` Teaser figure ⭐
- [ ] `T3.9b` Pipeline figure
- [ ] `T3.9c` UpSet/Venn overlap plot
- [ ] `T3.9d` Recall@k curves
- [ ] `T3.9e` Cost curve (regressions caught vs % suite run)
- [ ] `T3.10` `[v2]` Qualitative failure taxonomy, ~100 cases, 2 coders, Cohen's κ (RQ8) ⭐
- [ ] `T3.11` `[v2]` Impact half-life analysis (RQ9)
- [ ] `T3.12` `[v2]` Dependency-bump stratum (RQ10)
- [ ] `T3.13` `[v2]` Test-gap detection (RQ6)
- [ ] `T3.14` `[v2]` Flakiness-split sensitivity (RQ11)

### Weeks 8–12 — Predictor (Sep 28–Oct 25)
- [ ] `T4.1a` Graph feature extraction
- [ ] `T4.1b` Change feature extraction
- [ ] `T4.1c` Test-history feature extraction
- [ ] `T4.1d` Cross features + leakage audit ⭐
- [ ] `T4.1e` `[new]` Dynamic-boundary features
- [ ] `T4.2a` LightGBM lambdarank + Optuna sweep
- [ ] `T4.2b` SHAP attribution
- [ ] `T4.3a` PyG heterogeneous graph construction
- [ ] `T4.3b` Neighbour-sampled R-GCN training loop
- [ ] `T4.3c` Focal loss + early stopping on Recall@20%
- [ ] `T4.4` (optional) Claude re-ranker over top-50
- [ ] `T4.5a` 5-seed runs, mean ± std
- [ ] `T4.5b` Ablation table (graph/history/change/all)
- [ ] `T4.5c` Learning curve vs training-set size
- [ ] `T4.5d` Cross-project LOPO evaluation
- [ ] `T4.6` `[v2]` Calibration: reliability diagram, Brier, cost-optimal threshold (RQ7)
- [ ] `T4.7` `[new]` Written leakage audit + CI assertion ⭐
- [ ] `T4.8` `[new]` File-level prediction head (§18.8)

### Weeks 10–13 — Tool & Demo (Oct 12–Nov 2)
- [ ] `T5.1` `blastradius` CLI (init/predict/explain/serve/gaps)
- [ ] `T5.2` FastAPI service + OpenAPI + caching layers (§20.2)
- [ ] `T5.3a` Next.js shell + PR URL input
- [ ] `T5.3b` Interactive graph with impact highlighting + hairball controls (§20.3)
- [ ] `T5.3c` Cost-saved panel
- [ ] `T5.3d` Four-way comparison panel (co-change / reachability / model / truth) ⭐
- [ ] `T5.3e` Vercel deploy with pre-computed examples
- [ ] `T5.4` GitHub Action + marketplace listing
- [ ] `T5.5` MCP `predict_blast_radius` tool in the fork's `serve.py`
- [ ] `T5.6a` Dockerfile + compose
- [ ] `T5.6b` `make all` mini-corpus reproduction <15 min
- [ ] `T5.6c` `REPRODUCE.md`
- [ ] `T5.7` `[new]` Explainability contract + unexplained-fraction metric (§20.4)
- [ ] `T5.8` `[new]` Demo degradation plan (static-example fallback)

### Weeks 11–14 — Paper (Oct 19–Nov 10)
- [ ] `T6.1` Story lock + outline + figure list
- [ ] `T6.2` Draft §III Construction + §IV Description
- [ ] `T6.3` Draft §I Introduction + §II Related Datasets (comparison table)
- [ ] `T6.4` Draft §V Use Cases + §VI Limitations + §VII Availability
- [ ] `T6.5` Abstract (last)
- [ ] `T6.6` Claim–evidence audit table ⭐
- [ ] `T6.7` Three independent adversarial self-reviews, merged
- [ ] `T6.8a` Zenodo deposit + DOI
- [ ] `T6.8b` HuggingFace public + GitHub release tag + CITATION.cff
- [ ] `T6.8c` IEEEtran format check + page count + ORCIDs
- [ ] `T6.8d` AI-usage disclosure in Acknowledgements ⭐
- [ ] `T6.8e` Abstract submitted by **5 Nov**; paper by **10 Nov**
- [ ] `T6.9` `[v2]` Upstream PR to `safishamsi/graphify` (**November, after submission**)
- [ ] `T6.10` `[v2]` Economics subsection (CI minutes, cost, CO₂ estimate)
- [ ] `T6.11` `[v2]` VIT final report as the overflow buffer
- [ ] `T6.12` `[new]` Pre-register the analysis plan before final runs

---

## 36. Team Split & Workstream Interfaces

`[v1, backups new]` — three people, ~14 weeks. Ownership must be unambiguous or integration will eat you.

| Owner | Primary domain | Phases | Deliverables | Backup |
| --- | --- | --- | --- | --- |
| **Deepanshu (23BIT0264)** | Data engineering + ML | 0, 1, 4 | Harvester, labelling engine, predictor, paper integration | Sanskriti (labelling), Prisha (features) |
| **Prisha Vadhavkar (23BIT0010)** | Graph + tool | 2, 5 | Graphify fork, commit-pinned graphs, CLI, demo UI | Deepanshu |
| **Sanskriti Singh (23BIT0256)** | Parsers + measurement | 1, 3 | Test-result parsers, baselines, statistical analysis, figures | Prisha |

**Shared:** Phase 6 (paper), weekly integration, and the gold subset re-execution — parallelise across all three machines; it is embarrassingly parallel and **nobody should own it alone**.

**Interface contracts — agree in Week 1, do not change afterwards:**

| Producer | Artifact | Consumer | Frozen by |
| --- | --- | --- | --- |
| Sanskriti's parsers | `TestOutcome` records | Deepanshu's labelling engine | Week 1 |
| Prisha's graph builder | `graph_nodes/edges.parquet` keyed by `(repo, sha)` | Deepanshu's feature extractor | Week 2 |
| **All three** | **`test_id` canonical format** | **Everything** | **Week 1 ⭐** |
| Deepanshu's labelling engine | `instances/outcomes.parquet` | Sanskriti's baselines, Deepanshu's model | Week 2 |
| Prisha's query API | feature primitives (§20.1) | Deepanshu's feature extractor | Week 5 |

**`test_id` is the join key for the entire project. Get it wrong and nothing connects.** It has its own contract test, inherited from Graphify (§29.6), and that test must pass on every merge (**T12**).

`[new]` **The backup column is not decoration.** T13 (placement collision) is a 🔴 risk specifically because Deepanshu owns Phases 0, 1, and 4 — the critical path. Each backup must have read the code and run it once, before the blackout window, not during it.

---

## 37. Week-by-Week Timeline

`[v1]`

| Week | Dates | Deepanshu | Prisha | Sanskriti | Milestone |
| --- | --- | --- | --- | --- | --- |
| **0** | Aug 4–9 | 🔴 Harvester live | Repo frame + SEART | Fixture corpus (40 logs) | **Data flowing** |
| 1 | Aug 10–16 | Cursor/resume, artifact capture | Graphify fork + strip | JUnit XML parsers | `test_id` format frozen |
| 2 | Aug 17–23 | Change-set extraction | tree-sitter pinning | Log parsers (pytest/maven) | Schemas frozen |
| 3 | Aug 24–30 | Base-run resolution | Commit-pinned graphs | Parser precision report | 20k instances |
| 4 | Aug 31–Sep 6 | Labelling engine + splits | Incremental rebuild | Co-change mining | **BR-Bench v0.1** |
| 5 | Sep 7–13 | Docker re-exec harness | Test-node typing ⭐ | Baselines 1–3 | Gold subset starts · **binding rate measured** |
| 6 | Sep 14–20 | Gold re-execution runs | Graph enrichment + query API | Baselines 4–6 | Graph↔label join works |
| 7 | Sep 21–27 | Feature extraction | Graphify baseline (T3.7) | Divergence analysis | **RQ1 answered** |
| 8 | Sep 28–Oct 4 | LightGBM + Optuna | CLI scaffold | Stratified analysis + stats | Model beats baselines? |
| 9 | Oct 5–11 | GNN training | FastAPI service | Figures 1–3 | **Go/no-go on Technical Track** |
| 10 | Oct 12–18 | Ablations + LOPO | Demo UI | Figures 4–5 | Results frozen |
| 11 | Oct 19–25 | Paper §III–IV | Demo deploy | Paper §V–VI | *(Technical deadline Oct 23)* |
| 12 | Oct 26–Nov 1 | Paper §I–II | GH Action + MCP | Claim–evidence audit | Full draft |
| 13 | Nov 2–8 | Abstract + revisions | Repro package | Adversarial review ×3 | **Abstract due Nov 5** |
| 14 | Nov 9–10 | Zenodo DOI, submit | Final artifact check | Final proofread | **🎯 Submitted Nov 10** |

### 37.1 The go/no-go gates `[merged v1 + v2 G.11]`

**Gate 1 — end of Week 4:** ≥5,000 positive instances in the `strict` split.
*If missed:* widen the repo frame, drop to `permissive` as primary, extend the harvest window. **Do not proceed to modelling on a thin positive class.**

**Gate 1.5 — end of Week 5** `[v2]`**:** test-node binding rate ≥70%.
*If missed:* remediate immediately — widen conventions, add `tests_by_layout`, apply SCIP to Java, or drop low-binding repos. This gate did not exist in v1 and it is the one most likely to save the project, because a low binding rate is silent and everything downstream still "works" while producing noise.

**Gate 2 — end of Week 7:** RQ1 divergence result is statistically solid.
*If missed:* you still have a dataset paper. Drop the measurement framing, go pure Data & Tool Showcase. **A perfectly good outcome.**

**Gate 3 — end of Week 9:** model beats the best baseline, within-project, *p* < 0.05.
*If missed:* report the negative result honestly in §V — *"we find that graph-based prediction does not substantially outperform historical failure frequency, suggesting…"* That is a legitimate, citable, publishable finding on this track, and reviewers respect teams who report it rather than torturing the numbers.

**Notice that all gate failures still produce a submittable paper.** That is deliberate. Design the project so that no single failure is fatal.

### 37.2 Where the two clocks collide `[new]`

Both calendars on one line, with the collisions marked:

```
Aug        Sep                Oct                          Nov
 │          │                  │                            │
 W0──W1──W2─W3──W4──W5──W6──W7─W8──W9──W10──W11──W12──W13──W14
 ▲              ▲                   ▲     ▲    ▲         ▲   ▲
 │              │                   │     │    │         │   │
 harvester   Review 1           Review 2  │  MSR Tech   MSR  MSR
 must ship  (late Aug/          (late Sep │  paper      D&T  D&T
 (T1 clock)  early Sep)          early Oct)│  Oct 23     abs  paper
                                           │             Nov 5 Nov 10
                                     Review 3 / Final
                                       (late Oct)
```

| Collision | Weeks | Severity | Mitigation |
| --- | --- | --- | --- |
| **Review 2 ∥ Technical-Track deadline** | 10–11 | 🟠 | Review 2 slides are paper figures. Build the figure once, use it twice (**§38**). Skip the Technical Track by default (**D-01**) |
| **Review 3 / Final ∥ MSR D&T abstract** | 12–13 | 🔴 | Review 3 demo = the Phase 5 demo, no separate build. Abstract is 150 words drafted in Week 12, not Week 13 |
| **Placement season ∥ Weeks 8–13** | 8–13 | 🔴 | **T13.** Blackout declared in Week 1; Deepanshu's irreversible work front-loaded into Aug; named backups per task |
| **Gold re-execution ∥ everything** | 6–8 | 🟡 | Runs overnight on three machines; costs attention, not hours |

---

## 38. Course Deliverable Mapping

`[v2 Part E]` — you have to satisfy BITE497J *and* MSR. They are not in conflict if you plan the mapping now.

| Course milestone | Approx. timing | What you present | Reuses |
| --- | --- | --- | --- |
| **Zeroth Review** | ✅ Done (16 Jul 2026, approved) | Abstract, approved | — |
| **Review 1** | ~Late Aug / early Sep | Problem, literature, architecture, corpus statistics, harvester demo | §2 Novelty + Phase 0/1 outputs; **the corpus dashboard makes an excellent live demo** |
| **Review 2** | ~Late Sep / early Oct | Graph layer, baselines, RQ1 divergence result | Paper §II + §III, teaser figure, baseline table |
| **Review 3 / Final** | ~Late Oct | Full system, model results, web demo, paper draft | Everything; demo the web UI live |
| **Final report** | ~Nov | Expanded version of the paper | Paper + appendices — **the report can be longer than the paper; put the material you had to cut here** (T6.11) |
| **Viva** | ~Nov/Dec | Live demo + defence | Demo + **the Reviewer Pre-Mortem table (§45) answers most viva questions verbatim** |

**Two practical notes.** First, the VIT report format wants far more length than a 4-page paper — so write the paper tight and let the report absorb the overflow (extended related work, full baseline descriptions, all ablations, the qualitative taxonomy). Nothing is wasted. Second, **tell your guide about the MSR target early.** Guides advocate harder for students with an external deadline and a real venue, and Dr. Yoga Raja C A's name goes on the paper. Use the §4.5 one-paragraph script.

---

## 39. Prioritization Pass & the Review 1 MVP Cut Line

`[new]` — score = (Impact × Confidence) ÷ Effort-days. Impact and Confidence on 1–5. This is a ranking instrument, not an oracle; use it to argue, not to obey.

| Rank | Item | Impact | Conf | Effort (d) | Score | Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | **T0.3 Harvester daemon** | 5 | 5 | 1.0 | **25.0** | 🔴 Week 0. Irreversible clock |
| 2 | T0.1 Repo frame | 5 | 5 | 0.5 | 50.0* | 🔴 Week 0 (*trivially cheap, ranked by necessity not score) |
| 3 | **T1.1g `normalize_test_id`** | 5 | 4 | 0.5 | 40.0 | 🔴 The join key |
| 4 | **T1.3b Fault-revealing set** | 5 | 4 | 0.8 | 25.0 | 🔴 The label |
| 5 | **T2.3b Test-node binding** | 5 | 3 | 0.7 | 21.4 | 🔴 Gate 1.5 |
| 6 | T3.5 Historical-frequency baseline | 4 | 5 | 0.3 | 66.7 | 🔴 Build early — it is the bar |
| 7 | T0.5 Corpus dashboard | 4 | 5 | 0.3 | 66.7 | 🔴 Review 1 demo + Fig. 1 |
| 8 | T1.1 Parser suite | 5 | 4 | 1.0 | 20.0 | 🔴 |
| 9 | T2.2 Commit-pinned graphs | 5 | 3 | 0.8 | 18.8 | 🔴 |
| 10 | **T3.10 Qualitative taxonomy** | 4 | 5 | 1.0 | **20.0** | ✅ Best effort-to-value in the doc |
| 11 | T4.6 Calibration (RQ7) | 4 | 5 | 0.4 | 50.0 | ✅ Nearly free |
| 12 | T3.8 Divergence analysis | 5 | 4 | 1.0 | 20.0 | ✅ The headline |
| 13 | T1.5 Gold subset | 5 | 3 | 1.2 | 12.5 | ✅ Credibility anchor |
| 14 | T4.2 LightGBM | 4 | 5 | 0.6 | 33.3 | ✅ |
| 15 | T1.8 File-level ground truth | 3 | 5 | 0.3 | 50.0 | ✅ Approved-scope commitment |
| 16 | T3.7 Graphify baselines | 4 | 4 | 0.4 | 40.0 | ✅ Quotable finding |
| 17 | T5.6 Repro package | 4 | 5 | 0.6 | 33.3 | ✅ Scored by reviewers |
| 18 | T5.1/T5.2 CLI + API | 3 | 5 | 1.1 | 13.6 | ✅ |
| 19 | T5.3 Demo UI | 3 | 4 | 1.3 | 9.2 | ✅ Course requirement |
| 20 | T3.4 Ekstazi (real tool) | 3 | 2 | 0.8 | 7.5 | ⚠️ Painful; do it anyway — reviewers ask |
| 21 | T4.3 GNN | 2 | 3 | 1.3 | 4.6 | ⚠️ One week, then ship as ablation |
| 22 | T2.6 SCIP tier (RQ5) | 3 | 3 | 0.8 | 11.3 | ⚠️ Stretch |
| 23 | T3.13 Test-gap (RQ6) | 4 | 2 | 0.7 | 11.4 | ⚠️ Future work, prototype only |
| 24 | T5.4 GitHub Action | 2 | 4 | 0.5 | 16.0 | ⚠️ Half a day, ship it |
| 25 | T5.5 MCP tool | 2 | 5 | 0.4 | 25.0 | ⚠️ Nearly free given the scaffold |
| 26 | T4.4 LLM re-ranker | 2 | 3 | 0.8 | 7.5 | ⚠️ Strictly optional, outside the core |
| 27 | TypeScript support | 1 | 3 | 1.5 | 2.0 | ❌ **Cut** (D-03) |
| 28 | Cross-repo blast radius | 4 | 1 | 5.0 | 0.8 | ❌ Deferred (§44) |
| 29 | IDE plugin | 2 | 2 | 3.0 | 1.3 | ❌ Deferred |
| 30 | Learned ranking beyond LightGBM/R-GCN | 2 | 2 | 3.0 | 1.3 | ❌ Deferred |

### 39.1 The Review 1 MVP cut line

**Review 1 is late August / early September — roughly Week 3–4.** Everything above this line must exist and be demonstrable by then; everything below must not be started.

**✅ Above the line — must exist for Review 1:**

1. **Harvester running for ≥2 weeks** with the corpus dashboard live. *This is the demo.* A live counter of captured runs is more convincing than any slide.
2. **Attrition funnel** showing frame → usable repos, with real numbers.
3. **Parser suite** for JUnit XML + pytest, with the precision number on the 40-log fixture set.
4. **`normalize_test_id()`** with its contract test passing.
5. **Labelling engine v0** producing `instances.parquet` on at least 20 repos, even if splits are not final.
6. **Commit-pinned graph** building for the 3-repo mini-corpus, with node/edge counts.
7. **Architecture diagram** and the literature positioning from §2 and §28.
8. **The scope-drift conversation with the guide** (§4.5) — done, not pending.

**❌ Below the line — explicitly not started before Review 1:**

Predictor, GNN, demo UI, GitHub Action, MCP tool, SCIP tier, LLM re-ranker, test-gap detection, calibration, cross-repo anything, TypeScript.

**Why this cut line and not a more impressive one.** Review 1 asks for problem, literature, architecture, and evidence of progress. A live harvester with real numbers is *stronger* evidence of progress than a half-working predictor, and it is on the critical path anyway. Every hour spent on a demo UI in August is an hour not spent on the only thing with an expiry date (**T1**). **Build the thing that expires first.**

---

## 40. Workstream Dependency Graph

`[new]` — what blocks what. An arrow means "must be validated before".

```
                    ┌─────────────────────┐
                    │ test_id CONTRACT    │  ← Week 1, all three, frozen
                    └──────────┬──────────┘
                         ┌─────┴──────┐
                         ▼            ▼
              ┌──────────────┐  ┌──────────────────┐
   T0.1 ─────▶│ HARVESTER    │  │ TEST-NODE BINDING│◀── T2.2 graphs
   frame      │ T0.3 (S)     │  │ T2.3b (P)        │
              └──────┬───────┘  └────────┬─────────┘
                     ▼                   │
              ┌──────────────┐           │
              │ PARSERS      │           │
              │ T1.1 (S)     │           │
              └──────┬───────┘           │
                     ▼                   │
              ┌──────────────┐           │
              │ LABELS       │           │
              │ T1.3 (D)     │           │
              └──┬────────┬──┘           │
                 │        └──────────────┼────────────┐
                 ▼                       ▼            ▼
        ┌────────────────┐       ┌──────────────┐  ┌────────────┐
        │ BASELINES      │       │ FEATURES     │  │ CO-CHANGE  │
        │ T3.1–T3.7 (S)  │       │ T4.1 (D)     │  │ T1.4 (S)   │
        └────────┬───────┘       └──────┬───────┘  └─────┬──────┘
                 │                      ▼                │
                 │              ┌──────────────┐         │
                 │              │ MODEL T4.2/3 │         │
                 │              └──────┬───────┘         │
                 ▼                     ▼                 ▼
        ┌────────────────────────────────────────────────────┐
        │ RQ1 DIVERGENCE  T3.8   ← the paper's headline      │
        └───────────────────────────┬────────────────────────┘
                                    ▼
                  ┌─────────────────────────────────┐
                  │ FIGURES T3.9  →  PAPER  T6      │
                  └─────────────────────────────────┘
        ┌──────────────┐        ┌──────────────┐
        │ GOLD SUBSET  │───────▶│ AGREEMENT r  │──▶ paper §IV
        │ T1.5 (all)   │        └──────────────┘
        └──────────────┘
        ┌──────────────┐        ┌──────────────┐
        │ QUERY API    │───────▶│ CLI/API/DEMO │──▶ Review 3 + artifact
        │ T2.5 (P)     │        │ T5.x (P)     │
        └──────────────┘        └──────────────┘
```

(D) Deepanshu · (P) Prisha · (S) Sanskriti

**The five hard blocking edges — the ones where a slip propagates:**

| # | Blocker | Blocks | Slack | Why it is hard |
| --- | --- | --- | --- | --- |
| 1 | `test_id` contract | **Everything** | **Zero** | Parsers and graph nodes must agree on one string. Freeze Week 1 |
| 2 | Parsers → labels | Baselines, model, RQ1 | ~3 days | Labels cannot be built from unparsed logs |
| 3 | Graph + labels → features | Model, RQ1 | ~5 days | The join is the binding rate; below 70% this edge silently degrades |
| 4 | Baselines → RQ1 | Paper §V, Gate 2 | ~1 week | RQ1 is comparative; one missing baseline is a hole in the table |
| 5 | Everything → artifact freeze | Submission | **Zero after Nov 8** | DOI minting and link verification cannot be compressed |

**The one genuinely parallel path:** the harvester (Deepanshu) and the Graphify fork (Prisha) share no dependency and both start in Week 0–1. That parallelism is what makes the timeline fit; protect it by not asking Prisha to help with the harvester.

---

## 41. Metrics — Research, Engineering SLOs, Project Health

`[new]`

### 41.1 Research metrics
Defined in §25 (model, ranking, and dataset-quality metrics). The four to put on a slide: **Recall@20%**, **observational-vs-causal agreement rate**, **binding rate**, **RQ1 Jaccard(C, F)**.

### 41.2 Engineering SLOs

| Component | SLO | Measured by |
| --- | --- | --- |
| Harvester uptime | ≥95% of hours in the window | daily `MANIFEST.json` gaps |
| Harvest throughput | ≥3,000 runs/hour sustained | `logs/requests.jsonl` |
| Rate-limit 403s | 0 (backoff should prevent all) | request log |
| Cold graph build | ≤10 min (p50 ≤3 min) | `graph_index.parquet` |
| Incremental graph build | ≤10 s (p95 ≤30 s) | `graph_index.parquet` |
| Feature extraction | ≤100 ms per instance | CI benchmark on mini-corpus |
| API p95 latency | ≤500 ms warm, ≤3 s cold | FastAPI middleware |
| `make all` mini-corpus | ≤15 min | CI |
| Demo cold start | ≤3 s | Vercel analytics |
| Test suite runtime | ≤3 min | CI |

### 41.3 Project-health indicators

| Indicator | Green | Amber | Red |
| --- | --- | --- | --- |
| Sunday integration completed | every week | 1 missed | 2 consecutive missed |
| Oldest open branch | ≤3 days | 4–5 days | >5 days (**T12**) |
| Master Task Graph burn-down vs plan | ≥90% | 70–90% | <70% |
| Dashboard freshness | <24 h | 24–72 h | >72 h |
| Backup restore test | monthly, verified | overdue | never done |
| WIP per person | ≤3 tasks | 4–5 | >5 |
| `[unverified]` claims remaining in paper-facing text | 0 | 1–3 | >3 at Week 12 |
| Named backup has run the critical component | all three | two | fewer (**T13**) |

**Review these eight in the Sunday checkpoint.** They take four minutes and they are the difference between discovering a problem in week 6 and discovering it in week 12.

---

# Part VIII — Decisions, Questions, Deferred Work

## 42. Decision Register

`[new]` — every conflict between the sources, and every choice this pass had to make, is here. Nothing was resolved silently. **Two-way door** = cheap to reverse. **One-way door** = expensive or impossible to reverse once built on.

---

**Decision D-01: Which MSR 2027 track is the primary target**
- **Option A (v1):** Data & Tool Showcase — abstract 5 Nov, paper 10 Nov, 4pp, single-anonymous.
- **Option B (the merge brief's framing):** "MSR 2027, abstract deadline ~October 2026" — which corresponds to the **Technical Track**, abstract 20 Oct, paper 23 Oct, 10pp, double-anonymous.
- **Recommendation: A**, because the 18 extra days sit exactly where the course calendar is heaviest, 4 pages is achievable for three undergraduates while 10 pages of ACM two-column empirical work is not, the track exists precisely for reusable datasets and tools, it offers a Distinguished Paper Award, and single-anonymous review removes artifact-anonymisation friction. Dates re-verified against the live MSR 2027 site on 4 Aug 2026.
- **Reversibility:** two-way until ~12 Oct; **one-way after 20 Oct** (the Technical abstract deadline passes).
- **Revisit trigger:** Gate 3 passes by Week 9 **and** the full baseline table is complete by 5 Oct **and** all three team members agree the measurement story is strong enough to carry 10 pages. Absent all three, do not attempt it.

---

**Decision D-02: "Novel predictor" versus "dataset + honest evaluation" as the claimed contribution**
- **Option A (v1's phase structure):** Phase 4 has a hard gate — "model beats all baselines, *p* < 0.05" — which reads as a claim of a better predictor.
- **Option B (the merge brief):** the scientific contribution is the dataset plus honest empirical evaluation, explicitly *not* a claim of a novel state-of-the-art predictor.
- **Recommendation: B, with A retained as a phase gate rather than a project gate.** The novelty statement (§28.1) claims a measurement, not an algorithm. Phase 4 still runs and still has its gate, because a working predictor demonstrates the dataset supports learning — but Gate 3's failure branch already says the negative result is publishable, which is only coherent under B. v1 and the brief actually agree on the substance ("even if our predictor loses, the measurement wins"); the phase gate wording was the only thing pulling the other way.
- **Reversibility:** two-way (it is a framing choice, revisable until the abstract is written).
- **Revisit trigger:** if the model beats the best baseline by a large, robust margin cross-project as well as within-project, upgrade the claim — but only then.

---

**Decision D-03: Language scope**
- **Option A (v1 T4):** Java + Python + TypeScript-as-stretch.
- **Option B (implied by the brief's "single-language depth vs multi-language breadth — pick and defend"):** pick one and go deep.
- **Recommendation: A minus TypeScript — Java and Python, two languages, TS cut.** Full defence in §15.2: Java is required for baseline comparability, Python is required for corpus scale and cheap re-execution, and the static/dynamic contrast is itself a research variable that single-language depth would forfeit. TypeScript adds a third of everything and buys neither comparability nor a new variable.
- **Reversibility:** two-way for *adding* TS later (one extractor + one ID rule + one log parser); **effectively one-way for dropping Java**, since the RTS baselines depend on it.
- **Revisit trigger:** add TypeScript only if Phase 2 exits a full week early *and* Gate 1 is comfortably passed.

---

**Decision D-04: Parser strategy**
- **Option A (v1/v2):** tree-sitter via the Graphify fork, everywhere.
- **Option B (brief's option set):** native frontends (Eclipse JDT, javalang, Python `ast`, Soot, WALA) or LSP-based extraction.
- **Recommendation: A as the universal spine, plus SCIP (`scip-java`) as an optional precision tier on the reproducible-build Java subset.** The deciding constraint is that every high-precision option requires a successful build at the commit under analysis, which we cannot guarantee across hundreds of untrusted repos at historical SHAs. Build-independence is what buys the scale that makes the dataset a contribution (§15.3), and RQ5 measures what that costs us.
- **Reversibility:** two-way for adding SCIP; **one-way for the spine** — switching the primary extractor invalidates every built graph.
- **Revisit trigger:** if the Java phantom-edge rate (T2.8) exceeds ~25%, promote SCIP from optional to required for Java.

---

**Decision D-05: What kind of graph**
- **Option A:** AST + call graph + dependency graph (implied by v1 and by the approved abstract).
- **Option B:** Program Dependence Graph / System Dependence Graph.
- **Option C:** Code Property Graph.
- **Option D (recommended):** a **multi-layer typed property graph** — structural + symbolic + test + historical + configuration layers — with no data-flow analysis (§16.1).
- **Recommendation: D.** It is a superset of A, it is honest about the historical and test layers that A does not name, and it rejects B and C for a stated reason: both need data-flow, which needs types, which needs a build (D-04), and both buy slicing precision we would discard when ranking. D is also exactly what the approved abstract describes, plus two layers.
- **Reversibility:** **one-way** in practice — a schema change here invalidates the corpus of built graphs and every downstream feature.
- **Revisit trigger:** none within this project. Adding a data-flow layer is a v2 upgrade path (§44).

---

**Decision D-06: Storage backend**
- **Option A (v1):** NetworkX + DuckDB/Parquet; v1 explicitly leaves Neo4j/FalkorDB.
- **Option B (brief's option set):** Neo4j, Memgraph, KuzuDB, or Postgres with recursive CTEs.
- **Recommendation: A** — NetworkX for in-process traversal, DuckDB + Parquet as the system of record and feature cache. The deciding reason is the artifact requirement: a Data & Tool reviewer must reproduce with one command, and every server-based option adds a service that can fail on their machine. The access pattern (load a small graph, run one bounded traversal, discard) is an in-memory workload, not a graph-database workload. Full evaluation table in §19.2.
- **Reversibility:** two-way — Parquet is the source of truth, so a graph DB can be loaded from it later.
- **Revisit trigger:** a single repo graph exceeding ~2M nodes, or building the cross-repo global graph (§44). Then evaluate **KuzuDB** first (embedded, no server, keeps the one-command property).

---

**Decision D-07: Diff extraction method**
- **Option A (v1 T1.2):** symbol-table differencing via tree-sitter — parse base and head, diff the symbol maps.
- **Option B (brief):** AST-level tree differencing (GumTree / ChangeDistiller) with a full edit script.
- **Recommendation: A corpus-wide, B on the gold subset as validation.** Tier 1 costs milliseconds and runs on all ~50k instances; Tier 2 costs seconds plus a JVM dependency and runs on 300–500. The agreement rate between them is reported, which answers "you used a heuristic differ" rigorously without paying tree-differencing cost at scale. This mirrors the cheap-observational + expensive-causal pattern already used for labels, and consistency of method is itself worth something in review.
- **Reversibility:** two-way.
- **Revisit trigger:** if the Tier-1/Tier-2 agreement rate on the gold subset falls below ~85%, escalate Tier 2 to a larger sample and report the taxonomy from it instead.

---

**Decision D-08: Project and artifact naming**
- **Option A (v2):** keep `BlastRadius` — approved title, evocative, and Graphify's collision is with a phrase, not a product.
- **Option B (v2):** keep the project name, name the dataset distinctly (`BR-Bench`).
- **Option C:** rename entirely.
- **Recommendation: B.** Datasets are cited independently of tools, so distinct naming actively helps; and one sentence in Related Work acknowledging that Graphify uses the same phrase for a different quantity pre-empts the observation at negligible cost. C would require re-approval for no benefit.
- **Reversibility:** two-way now, **one-way after the Zenodo DOI is minted**.
- **Revisit trigger:** decide in Week 1 and stop discussing it.

---

**Decision D-09: Test-ID normalizer**
- **Option A (v1 T1.1g):** write `normalize_test_id()` from scratch.
- **Option B (v2 G.1):** extend `vendor/graphify-br/graphify/ids.py` and inherit its NFKC + casefold contract test.
- **Recommendation: B.** Their normalizer is battle-tested across 36 grammars, is cross-platform stable, and has an enforcing contract test. More importantly, using the *same* normalizer for test IDs and graph node IDs is what makes the join work at all — two independently-correct normalizers that disagree on one Unicode edge case would silently drop bindings.
- **Reversibility:** two-way but painful (it would invalidate stored IDs).
- **Revisit trigger:** none expected.

---

**Decision D-10: How test-node typing is implemented**
- **Option A (v1 T2.3):** extend the fork directly.
- **Option B (v2 G.2):** implement as a registered `LanguageResolver` plugin in Graphify's `resolver_registry`.
- **Recommendation: B.** Cleaner, upstreamable (T6.9), places Java FQN test binding where such logic belongs, and inherits their validation. Also adds `tests_by_layout` as a third binding strategy, which is free recall.
- **Reversibility:** two-way.
- **Revisit trigger:** none.

---

**Decision D-11: Graphify baseline granularity**
- **Option A (v1 T3.7):** one `graphify` baseline.
- **Option B (v2 G.5):** split into `GRAPHIFY-COMMUNITY` and `GRAPHIFY-DIRECT`, noting that its impact computation is zero-hop.
- **Recommendation: B.** Its output is not a test ranking, so any single-number comparison would be a strawman. Two derived rankings — one generous, one floor — is the fair treatment, and fairness here is both ethically right and rhetorically strong.
- **Reversibility:** two-way.
- **Revisit trigger:** none.

---

**Decision D-12: Matrix-build aggregation**
- **Option A:** treat each matrix leg as a separate instance.
- **Option B (v2 T9):** union failures across legs, record `n_matrix_legs`.
- **Recommendation: B.** A test failing on one OS leg is still fault-revealing; treating legs separately would multiply instances, correlate them heavily, and break the independence assumption in the statistics. Publishing `n_matrix_legs` means anyone can recompute under option A from the release.
- **Reversibility:** two-way (both are derivable from the release).
- **Revisit trigger:** if >20% of instances have `n_matrix_legs > 1`, report a sensitivity analysis under both rules. **Decide in Week 2, before labelling.**

---

**Decision D-13: Monorepo policy**
- **Option A (v2 T10):** exclude monorepos from the v1 frame.
- **Option B:** scope one graph per module with cross-module edges through package nodes.
- **Recommendation: A**, with the exclusion counted and reported. B is correct and is the documented upgrade path, but it multiplies the graph-versioning problem by the module count and is not a week that exists here.
- **Reversibility:** two-way (repos can be re-admitted).
- **Revisit trigger:** if exclusion removes more than ~15% of otherwise-usable repos, reconsider — that would be a material sample-representativeness problem, not just a convenience. **Decide in Week 3.**

---

**Decision D-14: Graph versioning strategy**
- **Option A:** one full graph per analysed commit.
- **Option B (recommended):** materialise at instance base SHAs only, with snapshot-every-50 + deltas.
- **Option C:** one temporal graph with per-node/edge validity intervals.
- **Recommendation: B** (§19.3). A is simple but wasteful; C is elegant, requires a time predicate on every query, turns incremental builds into mutations, and is a research project of its own. B composes naturally with the incremental builder, because a delta is exactly what an incremental build already computes.
- **Reversibility:** two-way (deltas can be expanded to full graphs).
- **Revisit trigger:** graph store exceeding 150 GB.

---

**Decision D-15: Graph visualisation library**
- **Option A (v1 T5.3):** `react-force-graph`.
- **Option B (v2 A.1):** fork Graphify's vis.js view.
- **Option C (brief):** Cytoscape.js.
- **Recommendation: B for the internal/CLI-served view** (it already exists and works, zero cost) **and C for the public demo** (native compound nodes give community-collapsing, which is the single most effective hairball defence, for free). A remains perfectly acceptable if Prisha can build it faster — the deciding factor should be who can ship in three days, not library taxonomy.
- **Reversibility:** two-way, ~1 day.
- **Revisit trigger:** Prisha's call in Week 8 when the CLI scaffold starts.

---

**Decision D-16: Dual submission to both tracks**
- **Option A (v1):** dual-submit if Phase 3 lands early — the measurement study to Technical, the dataset+tool to Data & Tool.
- **Option B:** single submission to Data & Tool.
- **Recommendation: B by default.** The tracks do accept different contributions and a clean split is legitimate, but a desk rejection for concurrent submission would be catastrophic and the upside does not justify the tail risk for a first submission. If there is any doubt about whether the split is clean, there is no doubt: submit once.
- **Reversibility:** **one-way** — a concurrent-submission finding cannot be undone.
- **Revisit trigger:** only if a faculty co-author with MSR experience reviews both drafts and confirms no substantial text overlap. Dr. Yoga Raja C A should make this call, not the students.

---

**Decision D-17: LLM use inside the pipeline**
- **Option A (v1 Rule 6):** no LLM calls in the reproducible pipeline, ever.
- **Option B (v1 T4.4):** an LLM re-ranker over the top-50 candidates as a stretch model.
- **These are in tension and v1 never reconciled them.**
- **Recommendation: both, with a hard boundary.** The reproducible core — harvest, parse, label, graph, features, LightGBM, R-GCN, all baselines, every number in every table — contains **zero** LLM calls. The re-ranker is an optional, clearly-separated demo path and, if reported at all, is reported as a non-deterministic ablation with the model version pinned, temperature 0, and **the cached responses released alongside the dataset** so the ablation is at least replayable. It never touches the headline numbers.
- **Reversibility:** two-way (the re-ranker is cuttable at any point).
- **Revisit trigger:** if the re-ranker cannot be made replayable via cached responses, cut it entirely rather than shipping an unreproducible number.

---

**Decision D-18: How the placement-season collision is handled**
- **Option A:** absorb it informally — work around it when it happens.
- **Option B:** declare a blackout window in Week 1, front-load the critical path, assign named backups.
- **Recommendation: B**, and this is the decision most likely to be skipped and most likely to matter. Deepanshu owns Phases 0, 1, and 4 — the entire critical path — and the placement window overlaps Weeks 8–13, which contains the model, the ablations, the abstract, and the submission. Concretely: harvester and labelling engine complete by end of August; Sanskriti runs the labelling engine at least once before the window opens; Prisha runs feature extraction at least once; and the Week 13 abstract is drafted in Week 12.
- **Reversibility:** two-way in principle, **one-way in practice** — you cannot retroactively transfer knowledge during a crunch.
- **Revisit trigger:** as soon as the placement calendar is known. **This is a Week 1 action, not a Week 8 one.**

---

## 43. Open Questions Requiring a Human Decision

`[merged v2 G.10 + new]` — each with the options and the evidence that would resolve it. These are not for Claude Code; they need a person, and most need the team together.

| # | Question | Options | Evidence that resolves it | Owner | By when |
| --- | --- | --- | --- | --- | --- |
| **Q1** | Final dataset name | `BR-Bench` / `RadiusBench` / other | Google Scholar + GitHub search for collisions; 10 minutes | All three | **Week 1** |
| **Q2** | Matrix-build aggregation rule | union / per-leg / primary-leg-only | `n_matrix_legs` distribution on the first 5k instances | Deepanshu | **Week 2** (D-12) |
| **Q3** | Monorepo policy | exclude / per-module graphs | How many frame repos are multi-module, and how many usable repos that costs | Prisha | **Week 3** (D-13) |
| **Q4** | Mining Challenge proposal | submit / skip | Is BR-Bench v0.1 real by ~25 Aug? 6 hours for a lottery ticket with an enormous payoff | All three | **~25 Aug** |
| **Q5** | Include TypeScript | yes / no | Phase 2 exit date and Gate 1 margin | Sanskriti | **Week 5** (D-03) |
| **Q6** | Gold re-execution machine time | 3 laptops overnight / free-tier cloud VM / hybrid | Measured minutes per instance on the first 20 | All three | **Week 5** |
| **Q7** | Tell the guide about MSR | now / after Review 1 | None needed — **the recommendation is now**; guides advocate harder with a real venue and their name on the paper | Deepanshu | **Week 1** |
| **Q8** | Placement blackout window | dates + backup assignments | Deepanshu's actual placement calendar | Deepanshu | **Week 1** (D-18) |
| **Q9** | Dual submission | yes / no | A faculty read of both drafts confirming no text overlap | Dr. Yoga Raja C A | **~10 Oct** (D-16) |
| **Q10** | Publish the pseudonymisation salt | publish / withhold / discard | Whether any analysis needs author identity linkage across the release | Deepanshu | **Week 12** |
| **Q11** | Canary string design | format and placement | Convention survey of recent public benchmarks | Sanskriti | **Week 12** |
| **Q12** | Which repos to drop after Gate 1.5 | by binding rate / by yield / keep all | Per-repo binding rate and positive-instance counts | Prisha | **Week 5** |
| **Q13** | Whether the demo needs a backend at all | live backend / static examples only | Vercel cost and reliability under a viva-day load | Prisha | **Week 11** |
| **Q14** | Author order on the paper | — | A conversation the team should have **early**, not in November | All three | **Week 2** |
| **Q15** | Whether `covered_by` is worth building on the gold subset | build / skip | Binding rate at Gate 1.5 — if it is marginal, coverage data is the best diagnostic available | Prisha | **Week 6** |

**Q14 deserves a sentence.** Author order is the single most common source of late-stage friction on student papers, it costs nothing to agree in Week 2, and it is unpleasant to negotiate in Week 14 under deadline pressure. Agree it while everyone is relaxed and write it in the repo.

---

## 44. Deferred / Institutional Upgrade Paths

`[merged v2 B.4/B.6 + v1 + new]` — over-engineered or premature ideas, parked with the trigger condition that would justify building them. **Nothing here is a to-do; everything here is a documented decision not to build, with the evidence that would change it.**

| # | Upgrade | What it is | Why not now | Trigger condition |
| --- | --- | --- | --- | --- |
| **U1** | **Cross-repo / supply-chain blast radius** `[v2 B.4]` | *When a library changes, which downstream repositories' tests break?* Graphify's `global_graph.py` already namespaces node IDs across repos (`repoA::node_id`) and dedupes shared library nodes by label; `manifest_ingest.py` gives `depends_on` package edges; Dependabot PRs give abundant, machine-generated, clean-CI-signal instances | Needs a different corpus construction (linked repos), a different ground truth, and a cross-repo graph store | v1 dataset published and cited; a second semester or a follow-up paper. **Harvest the Dependabot PRs now** (T0.6) — they cost nothing extra and this becomes possible later |
| **U2** | **Impact oracle for coding agents** `[v2 B.6]` | An MCP tool an agent calls before committing: *"which tests should I run to validate this edit?"* Directly on-trend, connects to Graphify's agent-facing audience, and costs only the `predict_blast_radius` tool | Evaluation needs agent-generated patches and a comparison against full-suite runs — a different study | ICSE/FSE 2028 follow-up, or a strong final-year extension. **Mention in "future research questions"; do not build now** |
| **U3** | **IDE plugin** (VS Code / JetBrains) | Blast radius shown inline as you type | Distribution, packaging, and UI polish for zero research value | Only if the tool gets external adopters asking for it |
| **U4** | **Full GitHub App** (beyond the simple Action) | Installable app with persistent graph state per repo, incremental updates on push | Operational burden — a hosted service with auth, storage, and uptime | External adoption, or an industry collaboration |
| **U5** | **Multi-language expansion** (Go, Rust, C#, Ruby) | tree-sitter grammars already exist in the fork | Each language costs a test-ID rule, a log parser, and a re-execution environment (§15.2) | v2 of the dataset, or a community contribution — the pipeline is language-pluggable by design |
| **U6** | **Learned ranking beyond LightGBM / R-GCN** | Code-LM embeddings of diffs, pretrained GNNs, temporal graph networks | The GBDT will probably win at this scale (§12.3); pretraining is a GPU budget nobody has | Only after the dataset is ≥10× larger, or with GPU access |
| **U7** | **Real-time CI integration** on the critical path | Blocking merge on predicted risk | A prediction tool that blocks merges must be safe, and we explicitly are not (§4.3 non-goal 1) | Never in this form. A *warning* integration is the Action (T5.4) |
| **U8** | **KuzuDB / Neo4j migration** | A real graph database | Breaks one-command reproduction; the access pattern does not need it (§19.2) | A single repo graph >2M nodes, or U1. Evaluate **Kuzu first** — embedded, keeps the one-command property |
| **U9** | **SCIP everywhere** (all languages, all commits) | Compiler-accurate graphs corpus-wide | Requires a successful build at every historical commit (§15.3) — the constraint that defines the project | If a future corpus is restricted to reproducible-build repos, which is a different sampling frame and a different paper |
| **U10** | **Data-flow / PDG layer** | Statement-level dependence for precise slicing | Needs types, needs a build, and buys precision we discard when ranking (§16.1) | If the RQ8 taxonomy shows that coarse method-level propagation is the dominant proxy-failure category |
| **U11** | **Real coverage instrumentation** (`covered_by` edges) | Ground-truth test↔code mapping | The cost that makes dynamic RTS impractical at scale | Free on the gold subset — use it as a **validation instrument** (§16.3), not a feature. Corpus-wide only with institutional compute |
| **U12** | **Distributed harvesting** | Multiple machines, sharded frame | Three PATs at 15k req/hr already comfortably exceed the need | Corpus target above ~1,000 repos |
| **U13** | **DI/IoC `wires` edges** | Spring/Guice/decorator wiring resolution | Speculative until evidence says it matters (§17.4) | RQ8 taxonomy places DI/IoC in the top three proxy-failure categories |
| **U14** | **Framework-implicit edges beyond `conftest.py` and annotations** | Routes, ORM↔schema, event handlers | Unbounded surface; low yield for test prediction (§17.5) | Same: a category appearing in the RQ8 taxonomy earns its implementation |
| **U15** | **BR-Bench as a hosted service / leaderboard** | Public leaderboard for test-selection models | Operational commitment beyond a student project's lifetime | Community uptake — if a second group publishes on BR-Bench, this becomes worth doing |

**The pattern worth noticing:** almost every trigger above is *"if the data says so"*. That is the point of building the dataset first — it converts architecture arguments into empirical questions, which is a much better way to decide what to build next.

---

# Part IX — Defence & Reference

## 45. Reviewer Pre-Mortem

`[merged v1 + new rows]` — write your answers to these **before** you write the paper. If you cannot answer one convincingly, that is a research task, not a writing task. **This table also answers most viva questions verbatim.**

| # | Objection | Your answer |
| --- | --- | --- |
| 1 | "Labels are observational, not causal." | Gold subset of 300–500 Docker-re-executed instances with base/head verdicts; report agreement rate *r*. Limitations states the scope of the causal claim explicitly |
| 2 | "Flaky tests contaminate your labels." | Four-filter pipeline; three splits; all headline results on `strict` with sensitivity analysis. Flakiness prevalence reported as a finding in its own right |
| 3 | "Only 90 days of data." | Rolling capture Aug–Nov gives ~6 months; the window is documented; the harvester is released so anyone can extend it. Framed as a *live* dataset with versioned DOIs |
| 4 | "Survivorship bias — merged PRs are green." | We label per-push, not per-merge, and include closed-unmerged PRs and non-default-branch pushes. Positive-class prevalence reported per event type |
| 5 | "Only two languages." | Java for baseline comparability (Ekstazi/STARTS/RTPTorrent are all Java), Python for corpus scale. The pair is a research variable, not a compromise. Pipeline is language-pluggable; adding a language is one parser |
| 6 | "RTPTorrent already exists." | Travis-era, pre-2020, single-language, build-job-anchored, prioritization-oriented. Ours is GHA-era, PR-anchored, multi-language, with explicit changed-file→failing-test edges. Comparison table in §II |
| 7 | "GHALogs already has the logs." | GHALogs is a log corpus; we are a *labelled* corpus. We parse verdicts, link to diffs, de-flake, and label fault revelation. Cite and, where possible, build on it |
| 8 | "Meta already solved predictive test selection." | On a proprietary monorepo, never independently replicated because no public data existed. We create the data that makes replication possible |
| 9 | "Graphify already does PR impact." | Unvalidated graph-proximity heuristic, and **zero-hop** — it matches paths and reports communities without traversing an edge. We evaluate it — the first such evaluation — and treat it as a baseline, fairly and generously |
| 10 | "Your GNN doesn't beat a GBDT." | Reported honestly as an ablation with analysis of why: graph features are largely captured by engineered distance features at this scale; sample efficiency; homophily assumptions |
| 11 | "Cross-project generalisation is poor." | Reported honestly. This is a finding: test-failure prediction is strongly project-specific, which motivates per-project fine-tuning and *increases* the value of a multi-project dataset |
| 12 | "How do we know your parsers are right?" | 40-log hand-labelled fixture set; per-parser precision reported; per-tier accuracy reported; parsers open-sourced |
| 13 | "Ethical/legal concerns about mining." | Public repos only, permissive licences, GitHub ToS honoured, authorship pseudonymised, secret-scanned before release. Stated in the paper |
| 14 | "Did you use AI to write this?" | Yes, disclosed in Acknowledgements per ACM/IEEE policy, with the scope of use stated |
| 15 | `[new]` **"Your graph is unsound — what about reflection and dynamic dispatch?"** | Both are acknowledged as accepted unsoundness with a stated position (§17), not discovered limitations. Dynamic boundaries are **flagged and used as features**; the phantom-edge rate is measured on a hand-checked sample; we rank rather than prove, and every graph-quality claim is measured against the CI ground truth we built precisely to measure it |
| 16 | `[new]` **"How do you avoid leakage in the time split?"** | Time-based splits only, never random; a written leakage audit (T4.7) covering trailing-window cutoffs, cross features, the `touches_test_file` exclusion rule, and near-duplicate code across train/test repos; a CI assertion that fails if the exclusion rule is violated |
| 17 | `[new]` **"Your binding rate is only X% — aren't your graph features mostly missing?"** | Measured in Week 5 with a hard 70% floor gate, reported per repo and per strategy, and validated against real coverage on the gold subset. Instances below threshold are identifiable in the release so anyone can filter |
| 18 | `[new]` **"You forked someone else's tool. What did you actually build?"** | ~1,200–2,000 lines added against ~15,000+ inherited, and the added lines are exactly the research contribution: commit-pinning, test-node binding, historical edges, label integration, features, the model. The fork is credited, pinned by commit SHA, MIT-compatible, and we contribute back upstream (T6.9) |
| 19 | `[new]` **"Precision/recall/F1 at what operating point?"** | The cutoff rule is stated (§18.7) and, once calibration exists, *derived* from cost rather than chosen. Full Recall@k curves are reported so no single operating point carries the claim |
| 20 | `[new]` **"Isn't your positive class so rare that these numbers are meaningless?"** | Prevalence is published (expect 1 in 200–2,000). We report ranking metrics rather than accuracy, use `scale_pos_weight`/focal loss, and ship both full-negative and sampled-negative variants so others can choose |

---

## 46. Immediate Next Actions

`[v1]` — ordered. Do them in order.

1. **Today** — create three fine-grained GitHub PATs (`public_repo`, `read:org`), put them in `.env`, verify rate limits.
2. **Today** — run the SEART query, export the candidate frame.
3. **Tomorrow** — implement `TokenPool` + `get_with_backoff()`. Nothing else touches HTTP.
4. **Day 3–4** — the capture loop. Get it running against 10 repos, verify raw JSONL looks sane.
5. **Day 5** — scale to 300 repos, deploy as a daemon, set up the nightly mirror.
6. **Day 6** — dashboard. Watch the numbers climb.
7. **Day 7** — team meeting: freeze `test_id` format, freeze `instances.parquet` schema, assign Week 1.

Then, in parallel with the harvester running unattended:

8. **Week 1** — brief Dr. Yoga Raja C A on the fault-revelation framing (it is inside the approved abstract already) and the MSR 2027 Data & Tool Showcase target, using the §4.5 script. Guides are far more helpful when they know there is a real venue and a real date.
9. **Week 1** — set up the shared Overleaf, the GitHub org, and the GitHub Project board mirroring the Master Task Graph (§35).
10. **By ~25 Aug** — decide on the MSR Mining Challenge dataset proposal. Six hours of work for a lottery ticket with an enormous payoff.

`[new]` **Three additions to the Week-1 meeting agenda**, because each is cheap now and expensive later:

11. **Week 1** — declare the placement blackout window and assign named backups (**D-18 / T13**). Ten minutes.
12. **Week 1** — agree author order (**Q14**). Five minutes now, or an unpleasant hour in November.
13. **Week 1** — decide the dataset name (**Q1 / D-08**) and stop discussing it.

---

## 47. References

`[merged v1 Reference Additions + new Research Expansion]`

### 47.1 The approved Zeroth Review list (7 references, APA)

These are the references the guide approved on 16-07-2026. They stay in the paper and each is differentiated in §28.2.

1. Borg, M., Wnuk, K., Regnell, B., & Runeson, P. (2017). Supporting change impact analysis using a recommendation system: An industrial case study in a safety-critical context. *IEEE Transactions on Software Engineering, 43*(7), 675–700.
2. Huang, Y., Jiang, J., Luo, X., Chen, X., Zheng, Z., Jia, N., & Huang, G. (2022). Change-patterns mapping: A boosting way for change impact analysis. *IEEE Transactions on Software Engineering, 48*(7), 2376–2398.
3. Dai, P., Wang, Y., Jin, D., Gong, Y., & Yang, W. (2022). An improving approach to analyzing change impact of C programs. *Computer Communications, 182*, 60–71.
4. Zhao, J., Yang, H., Xiang, L., & Xu, B. (2002). Change impact analysis to support architectural evolution. *Journal of Software Maintenance and Evolution: Research and Practice, 14*(5), 317–333.
5. Hunsen, C., Lochau, M., Schaefer, I., & Schulze, S. (2016). Modular change impact analysis for configurable software. *Proceedings of ICSME*, 446–456. IEEE.
6. Zhang, S., Gu, Z., Lin, Y., & Zhao, J. (2008). Change impact analysis for AspectJ programs. *Proceedings of ICSM*, 87–96. IEEE.
7. Gupta, C., & Gupta, V. (2015). Software change impact analysis: An approach to compute and prioritize impacted functions in software systems. *International Journal of Systems and Service-Oriented Engineering, 5*(2), 44–55.

### 47.2 Reference additions from v1, grouped by the role each plays `[v1]`

**Closest related work (Change Impact Analysis)**
- *From Seed to Scope: Reasoning to Identify Change Impact Sets* (RIPPLE), ICSE 2026 `[unverified]` — LLM-based intent-aware IA over **co-change** relationships. Your primary contrast: different dependent variable.
- Borg et al., TSE 2017 and Huang et al., TSE 2022 — already in the approved list.

**Regression Test Selection (your reachability baselines)**
- Gligoric, Eloussi & Marinov, *Practical regression test selection with dynamic file dependencies* (Ekstazi), ISSTA 2015.
- Legunsen et al., *STARTS: STAtic regression test selection*, ASE 2017.
- *Hybrid Regression Test Selection by Synergizing File and Method Call Dependences* (JcgEks), FSE 2024 Companion `[unverified]` — method-level RTS, the current frontier.
- Empirical comparison of Ekstazi / HyRTS / OpenClover / STARTS, *Journal of Systems and Software*, 2021 `[unverified]` — gives the safety/precision violation metric definitions.

**Predictive Test Selection (your task, industrial precedent)**
- Machalica, Samylkin, Porth & Chandra, *Predictive Test Selection*, ICSE-SEIP 2019 — the Meta paper; the headline framing comes from here.
- Pan, Bagherzadeh, Ghaleb & Briand, *Test case selection and prioritization using machine learning: a systematic literature review*, EMSE 2022 — the survey to position against.
- *Targeted Test Selection Approach in Continuous Integration*, 2025 `[unverified]` — recent industrial work.

**Datasets (your §II comparison table)**
- Mattis, Rein, Dürsch & Hirschfeld, *RTPTorrent*, MSR 2020 — the dataset you supersede.
- Beller, Gousios & Zaidman, *TravisTorrent*, MSR 2017 — the ancestor.
- Moriconi et al., *GHALogs: Large-scale dataset of GitHub Actions runs*, MSR 2025 `[unverified]` — the substrate.
- Cardoen et al., *A dataset of GitHub Actions workflow histories*, MSR 2024 `[unverified]`.
- Brandt, Panichella, Zaidman & Beller, *LogChunks: A dataset for build log analysis*, MSR 2020.
- Cheng et al., *Revisiting Test-Case Prioritization on Long-Running Test Suites* (LRTS), ISSTA 2024 `[unverified]`.

**Flakiness (your T3 defence)**
- Bell et al., *DeFlaker: Automatically detecting flaky tests*, ICSE 2018.
- Alshammari, Morris, Hilton & Bell, *FlakeFlagger: Predicting flakiness without rerunning tests*, ICSE 2021.
- Lam et al., *iDFlakies: A framework for detecting and partially classifying flaky tests*, ICST 2019.
- Luo, Hariri, Eloussi & Marinov, *An empirical analysis of flaky tests*, FSE 2014 — the root-cause taxonomy.
- Fatima, Ghaleb & Briand, *Just-in-time flaky test detection via abstracted failure symptom matching*, 2023 `[unverified]`.

**Methods / infrastructure**
- Dabic, Aghajani & Bavota, *Sampling projects in GitHub for MSR studies* (SEART GHS), MSR 2021 — cite for the sampling frame.
- Spadini, Aniche & Bacchelli, *PyDriller*, ESEC/FSE 2018 — cite for Git mining.
- Hoang et al., *DeepJIT*, MSR 2019; Hoang et al., *CC2Vec*, ICSE 2020; Pornprasit & Tantithamthavorn, *JITLine*, MSR 2021 — the JIT defect-prediction line, adjacent framing.
- Gebru et al., *Datasheets for Datasets*, CACM 2021 — cite for the datasheet.
- Traag, Waltman & van Eck, *From Louvain to Leiden*, Scientific Reports 2019 — cite for Graphify's community detection.
- `safishamsi/graphify` (MIT) — cite the repository and its release tag in the artifact section.

**Adjacent execution-grounded benchmarks (contrast, not competition)**
- Jimenez et al., *SWE-bench*, ICLR 2024 — for the F→P label construction pattern you invert.
- *CI-Repair-Bench*, 2026 `[unverified]` — GHA-mined, Python, repair-oriented; shares the 90-day retention constraint, different task.

### 47.3 Research expansion — grounded prior art `[new]`

The merge brief asks for real prior art in change impact analysis, program slicing, code property graphs, test selection/prioritization, and MSR-style repository mining, cited specifically enough to find, with speculation clearly separated. **Everything in this subsection is well-established published work I can identify precisely; anything I could not verify to that standard is marked `[unverified]` above and must be checked before citation.**

**Change impact analysis — foundations**
- Bohner, S. A., & Arnold, R. S. (1996). *Software Change Impact Analysis*. IEEE Computer Society Press. — the field's founding collection; the source of the standard vocabulary (starting impact set, estimated impact set, actual impact set). **Use this vocabulary in the paper; it makes the contribution legible to the CIA community.**
- Lehnert, S. (2011). A taxonomy for software change impact analysis. *Proceedings of IWPSE-EVOL*. — the taxonomy against which to position the approach.
- Li, B., Sun, X., Leung, H., & Zhang, S. (2013). A survey of code-based change impact analysis techniques. *Software Testing, Verification and Reliability, 23*(8). — the survey a reviewer will expect to see cited.
- Ren, X., Shah, F., Tip, F., Ryder, B. G., & Chesley, O. (2004). Chianti: A tool for change impact analysis of Java programs. *OOPSLA*. — **the closest classical tool**; its atomic-change decomposition informs §18.2. Explain in Related Work why it cannot be run at corpus scale (it needs a build — §15.3).
- Law, J., & Rothermel, G. (2003). Whole program path-based dynamic impact analysis (PathImpact). *ICSE*. — dynamic impact analysis; the precision ceiling we do not reach and the cost we do not pay.
- Apiwattanapong, T., Orso, A., & Harrold, M. J. (2005). Efficient and precise dynamic impact analysis using execute-after sequences. *ICSE*. — the efficiency counterpart to PathImpact.

**Program slicing and dependence graphs**
- Weiser, M. (1981). Program slicing. *ICSE*. — the origin.
- Ferrante, J., Ottenstein, K. J., & Warren, J. D. (1987). The program dependence graph and its use in optimization. *ACM TOPLAS, 9*(3). — the PDG; cited in §16.1 for why we do not build one.
- Horwitz, S., Reps, T., & Binkley, D. (1990). Interprocedural slicing using dependence graphs. *ACM TOPLAS, 12*(1). — the SDG.
- Tip, F. (1995). A survey of program slicing techniques. *Journal of Programming Languages, 3*(3). — the survey.

**Code property graphs and static analysis frameworks**
- Yamaguchi, F., Golde, N., Arp, D., & Rieck, K. (2014). Modeling and discovering vulnerabilities with code property graphs. *IEEE S&P*. — the CPG; cited in §16.1 for why our representation differs.
- Vallée-Rai, R., et al. (1999). Soot — a Java bytecode optimization framework. *CASCON*. — the bytecode-analysis alternative rejected in §15.3.
- Bravenboer, M., & Smaragdakis, Y. (2009). Strictly declarative specification of sophisticated points-to analyses (Doop). *OOPSLA*.
- Sui, Y., & Xue, J. (2016). SVF: Interprocedural static value-flow analysis in LLVM. *CC*.

**Call-graph construction and its known unsoundness** — directly relevant to §17
- Dean, J., Grove, D., & Chambers, C. (1995). Optimization of object-oriented programs using static class hierarchy analysis (CHA). *ECOOP*.
- Bacon, D. F., & Sweeney, P. F. (1996). Fast static analysis of C++ virtual function calls (RTA). *OOPSLA*.
- Livshits, B., Whaley, J., & Lam, M. S. (2005). Reflection analysis for Java. *APLAS*. — cited in §17.3 for why we flag rather than resolve.
- Reif, M., et al. (2019). Judge: Identifying, understanding, and evaluating sources of unsoundness in call graphs. *ISSTA*. — **the paper to cite when stating accepted unsoundness**; it makes the position principled rather than apologetic.
- Sui, L., Dietrich, J., Tahir, A., & Xu, X. (2020). On the recall of static call graph construction in practice. *ICSE*. — empirical evidence that even mature tools miss edges.

**Mining co-change and evolutionary coupling** — the L4 layer and the B7 baseline
- Gall, H., Hajek, K., & Jazayeri, M. (1998). Detection of logical coupling based on product release history. *ICSM*. — the origin of logical/evolutionary coupling.
- Zimmermann, T., Weissgerber, P., Diehl, S., & Zeller, A. (2005). Mining version histories to guide software changes (ROSE). *IEEE TSE, 31*(6). — **the canonical co-change recommender**; the direct ancestor of the co-change label class this work argues against.
- Ying, A. T. T., Murphy, G. C., Ng, R., & Chu-Carroll, M. C. (2004). Predicting source code changes by mining change history. *IEEE TSE, 30*(9).
- Kagdi, H., Gethers, M., Poshyvanyk, D., & Collard, M. L. (2010). Blending conceptual and evolutionary couplings to support change impact analysis. *WCRE/ICSM*. — hybrid coupling, close in spirit to our L2+L4 combination.
- Śliwerski, J., Zimmermann, T., & Zeller, A. (2005). When do changes induce fixes? (SZZ). *MSR*. — needed for RQ6's bug-inducing-commit linkage.

**AST differencing** — §18.1
- Fluri, B., Würsch, M., Pinzger, M., & Gall, H. (2007). Change distilling: Tree differencing for fine-grained source code change extraction. *IEEE TSE, 33*(11).
- Falleri, J.-R., Morandat, F., Blanc, X., Martinez, M., & Monperrus, M. (2014). Fine-grained and accurate source code differencing (GumTree). *ASE*.

**Regression test selection and prioritization** — §24
- Rothermel, G., & Harrold, M. J. (1997). A safe, efficient regression test selection technique. *ACM TOSEM, 6*(2). — **the definition of safety** we explicitly do not provide (§17.1).
- Rothermel, G., Untch, R. H., Chu, C., & Harrold, M. J. (2001). Prioritizing test cases for regression testing. *IEEE TSE, 27*(10). — the APFD metric.
- Yoo, S., & Harman, M. (2012). Regression testing minimization, selection and prioritisation: a survey. *STVR, 22*(2). — the survey.
- Elbaum, S., Rothermel, G., & Penix, J. (2014). Techniques for improving regression testing in continuous integration development environments. *FSE*. — CI-context RTS at Google scale; the closest industrial precedent before Meta.
- Memon, A., et al. (2017). Taming Google-scale continuous testing. *ICSE-SEIP*.
- Zhang, L. (2018). Hybrid regression test selection (HyRTS). *ICSE*. `[unverified — confirm venue and year]`

**ML for software engineering — methodology cautions**
- Allamanis, M. (2019). The adverse effects of code duplication in machine learning models of code. *Onward!* — **cite this in the leakage audit** (T4.7); near-duplicate code across train/test splits is a known inflator.
- Allamanis, M., Brockschmidt, M., & Khademi, M. (2018). Learning to represent programs with graphs. *ICLR*. — the GNN-on-code precedent for T4.3.
- Schlichtkrull, M., et al. (2018). Modeling relational data with graph convolutional networks (R-GCN). *ESWC*.
- Hu, Z., Dong, Y., Wang, K., & Sun, Y. (2020). Heterogeneous graph transformer (HGT). *WWW*.
- Bhattacharya, P., Iliofotou, M., Neamtiu, I., & Faloutsos, M. (2012). Graph-based analysis and prediction for software evolution. *ICSE*. — graph metrics as predictors of software evolution; a useful precedent for the centrality features.

**Repository mining infrastructure**
- Gousios, G. (2013). The GHTorrent dataset and tool suite. *MSR*. — the ancestor of all GitHub mining datasets.
- Dabic, O., Aghajani, E., & Bavota, G. (2021). Sampling projects in GitHub for MSR studies. *MSR*. — SEART; the sampling frame.
- Spadini, D., Aniche, M., & Bacchelli, A. (2018). PyDriller: Python framework for mining software repositories. *ESEC/FSE*.

**Speculative design proposals in this document — clearly separated, as the brief requires.** The following are *our* design ideas, not claims grounded in prior work, and must not be presented as established: the impact half-life hypothesis (**RQ9**, §T3.11); graph-detected test gaps as a proxy for coverage gaps (**RQ6**, §T3.13); the specific scoring formula and its default constants (§18.5); the tiered node/edge taxonomy (§16.2–16.3); the snapshot+delta versioning scheme (§19.3); the dynamic-boundary feature family (§17.3); and the claim that co-change and fault-revealing sets are "nearly disjoint" (§11.1), which is a **hypothesis to be tested by RQ1, not a finding**. Do not let any of these drift into the paper's prose as established fact before the data says so.

---

## 48. Final Note

`[v1]`

The technical work here is substantial but tractable. The thing that will actually determine whether this becomes a paper is **the harvester running by Friday**. Every other decision in this document can be revised, reversed, or rebuilt. Log expiry cannot.

Three additional things worth internalising:

**The measurement is the paper; the model is the bonus.** Teams fail at this by spending September on a GNN and October discovering their labels were wrong. Spend September on labels you trust.

**Honest negative results are publishable on this track.** "Graph proximity heuristics achieve only X% recall against real CI outcomes" and "cross-project generalisation is poor" are both findings. Do not bend numbers to manufacture a win you did not get.

**Ship the artifact as if it were the paper.** On the Data & Tool Showcase track, it effectively is. A reviewer who can `pip install` your tool and reproduce a table in ten minutes is a reviewer who accepts.

`[v2 Closing note]` The Graphify investigation changed the shape of this project in a good way. You are inheriting a mature, security-hardened, well-tested extraction engine with a plugin architecture that happens to have an empty slot exactly where your contribution goes — and the one feature that looked like competition turns out to be a zero-hop path match that has never been evaluated. That is close to the ideal situation: most of the boring work is done, and the interesting question is untouched.

The two things that decide whether this becomes a paper are still the same. **Get the harvester running.** Then **measure the binding rate by Week 5** — because if tests don't bind to graph nodes, nothing downstream is real, and you want to know that in September, not October.

`[new]` And one thing neither source said out loud: **this project has four independent ways to succeed.** A dataset alone is a Data & Tool paper. A dataset plus the divergence measurement is a stronger one. Add a working predictor and it is stronger still. Add none of them and you still have a full BITE497J project with a live system, a real corpus, and an honest evaluation. Every gate in §37.1 fails *into* a submittable outcome. That is not optimism; it is the structure of the plan, and it is the reason to start the harvester today rather than deliberating for another week.

Now go build the harvester.

---

# Appendix A — Coverage Matrix

This appendix is the proof of **R1 (zero loss)**. Every section of both source documents appears below with its destination in this document. **Nothing is marked "dropped."** Where a source item was superseded by a Decision, the original is still present in the text of that Decision as the rejected option — a rejected option that is written down and argued against is not lost, it is resolved.

**Status vocabulary:**
- **Carried** — reproduced with wording preserved
- **Carried + expanded** — reproduced, then extended in an `Expansion` subsection or a deeper chapter
- **Merged** — combined with the corresponding item from the other source; the more rigorous version won, unique details from the other absorbed
- **Relocated** — moved to a different Part under R4/the one structural deviation (§0.3); content unchanged
- **Resolved** — the two sources conflicted; both options are preserved inside a Decision block

## A.1 `BlastRadius_Supreme_Roadmap_v1.md` → destination

| Source § (line) | Source heading | Destination | Status |
| --- | --- | --- | --- |
| 1 | Title / preamble | §Title, §0.2 | Merged |
| 17 | Project North Star | **§1** | Carried |
| 41 | The Novelty Thesis | **§2** | Carried + expanded (§2 now also states what is *not* claimed, per D-02) |
| 47 | Why this survives a hostile reviewer | **§2.1** | Carried |
| 59 | The three deliverables | **§2.2** | Carried |
| 65 | Good news on the approved abstract | **§2.3** | Carried + expanded (§4.5 adds the full scope-drift register) |
| 71 | Hard Dates & Venue Strategy | **§3** | Carried, dates re-verified 4 Aug 2026 |
| 90 | Recommended strategy: Data & Tool primary | **§3.1** | Carried → **Resolved as D-01** (Technical Track preserved as Option B) |
| 104 | Mandatory compliance checklist | **§3.4** | Carried |
| 116 | Threat Register preamble | **§5** intro | Carried |
| 120 | T1 — logs expire after 90 days 🔴 | **§5 T1** | Carried; reinforced in §46 and §48 |
| 130 | T2 — Survivorship bias | **§5 T2** | Carried |
| 138 | T3 — Flaky test contamination | **§5 T3** | Carried + expanded (T3.14 sensitivity analysis) |
| 151 | T4 — Language / build fragmentation | **§5 T4** | Carried → **Resolved as D-03** (TypeScript cut; full defence §15.2) |
| 165 | T5 — Log parsing is a swamp | **§5 T5** | Carried |
| 178 | T6 — Labels observational, not causal | **§5 T6** | Carried + expanded (§21.5 causal anchor) |
| 188 | Phases Overview | **§7** | Carried |
| 204–212 | Phase 0 status + subtasks T0.1–T0.5 | **§8.1–§8.6** | Carried |
| 297 | Phase 0 exit criteria | **§8.6** | Carried + expanded (attrition funnel, frame freeze) |
| 307–313 | Phase 1 status + subtasks T1.1–T1.6 | **§9.1–§9.7** | Carried |
| 409 | Phase 1 exit criteria | **§9.7** | Carried |
| 420–426 | Phase 2 status + subtasks T2.1–T2.5 | **§10.1–§10.6** | Carried; **deep specification relocated to Part IV** (§0.3) |
| 485 | Phase 2 exit criteria | **§10.6** | Carried + expanded (Gate 1.5 binding rate) |
| 494–500 | Phase 3 status + Research Questions RQ1–RQ4 | **§11.1–§11.2** | Carried + expanded (RQ5–RQ11 register, §11.6.6) |
| 518 | Phase 3 subtasks T3.1–T3.9 | **§11.3–§11.5** | Carried + expanded (T3.10–T3.15) |
| 561 | Phase 3 exit criteria | **§11.5** | Carried |
| 570–574 | Phase 4 status + evaluation protocol | **§12.1–§12.2**, **§32** | Carried (protocol duplicated deliberately as the frozen reference) |
| 584 | Phase 4 subtasks T4.1–T4.5 | **§12.3–§12.7** | Carried + expanded (T4.6–T4.8) |
| 632 | Phase 4 exit criteria | **§12.7** | Carried |
| 641–647 | Phase 5 status + subtasks T5.1–T5.6 | **§13.1–§13.7** | Carried + expanded (T5.7 explainability, T5.8 degradation) |
| 681 | Phase 5 exit criteria | **§13.7** | Carried |
| 690–696 | Phase 6 status + 4-page structure | **§14.1–§14.2** | Carried |
| 711 | Phase 6 subtasks T6.1–T6.8 | **§14.3** | Carried + expanded (T6.9–T6.12) |
| 722 | Also produce (course deliverables) | **§38** | Merged with v2 Part E (v2's table is more complete; v1's items absorbed) |
| 731–737 | Graphify Reuse Map — Take | **§29.3** | Merged with v2 A.1 (v2's module-by-module verdicts are more specific) |
| 752 | Graphify Reuse Map — Leave | **§29.3–§29.4** | Merged |
| 762 | Graphify Reuse Map — Build | **§29.3** | Merged |
| 771 | The one real danger | **§29.7**, **§10.1** | Carried |
| 779 | Full Tech Stack | **§30** | Carried |
| 802 | Hard constraints to design around | **§30.1** | Carried |
| 811–815 | `instances.parquet` schema | **§31.1** | Carried + expanded (new columns: `n_matrix_legs`, `is_bot_pr`, `base_run_distance`, `label_provenance`) |
| 845 | `outcomes.parquet` schema | **§31.2** | Carried + expanded |
| 864 | `graph_nodes/edges.parquet` schema | **§31.3** | Carried + expanded (new `identity_map.parquet`, `graph_index.parquet`) |
| 877 | `cochange.parquet` | **§31.4** | Carried |
| 883 | `gold.parquet` | **§31.5** | Carried |
| 890 | Release hygiene | **§22.5**, **§31.6** | Carried + expanded (canary string, `br-bench-lite`) |
| 898 | Evaluation Protocol | **§32** | Carried |
| 914–945 | Claude Code Working Protocol, Rules 1–9 | **§34.1** | Carried verbatim → Rule 6 vs T4.4 **Resolved as D-17** |
| 945 | The build sequence rule | **§34.2** | Carried |
| 951–1084 | Master Task Graph, all weeks | **§35** | Carried + expanded (new tasks interleaved with tags; owner backups added) |
| 1085 | Team Split | **§36** | Carried + expanded (backup column, interface contract table) |
| 1104 | Week-by-Week Timeline | **§37** | Carried + expanded (§37.2 collision map) |
| 1124 | The three go/no-go gates | **§37.1** | Carried + expanded (**Gate 1.5** added from v2 G.11) |
| 1139 | Reviewer Pre-Mortem (14 rows) | **§45** | Carried verbatim + 6 new rows (#15–#20) |
| 1162 | Immediate Next Actions (10 items) | **§46** | Carried + expanded (items 11–13) |
| 1182 | Reference Additions | **§47.2** | Carried + expanded (§47.3 grounded prior art) |
| 1231 | Final Note | **§48** | Carried + merged with v2 Closing note |

## A.2 `BlastRadius_Roadmap_Vol2_Graphify_and_Expansion.md` → destination

| Source § | Source heading | Destination | Status |
| --- | --- | --- | --- |
| A.0 | The headline finding (zero-hop) | **§29.1** | Carried — this is the single most consequential finding in either source |
| A.0 (48) | Naming collision — decide Week 1 | **§4.4**, **D-08**, **Q1** | Resolved (Option B: BR-Bench) |
| A.0 (60) | The reframing this unlocks | **§2.1**, **§29.1** | Carried |
| A.1 (68–128) | Module-by-module verdict, core pipeline, high-value finds, interfaces, delete list, test suite | **§29.2**, **§29.4**, **§29.5** | Carried |
| A.2 | The surgical fork plan | **§10.1** (ordered sequence), **§29.3** | Carried |
| A.3 | `TestResolver` plugin design + code | **§29.6** | Carried, code preserved → **D-10** |
| A.3 (210) | Upstream contribution | **§14.4 T6.9** | Carried, scheduled for November |
| B.1 | Calibrated risk score, not a set | **§11.6**, **§12.8 T4.6**, RQ7 | Carried |
| B.2 | The test-gap finding | **§11.6 T3.13**, RQ6, **U11** | Carried |
| B.3 | Qualitative failure taxonomy | **§11.6 T3.10**, RQ8 | Carried — highest effort-to-value item in §39 |
| B.4 | Cross-repo blast radius | **§44 U1** | Relocated to deferred, with T0.6 (Dependabot capture) kept live so it stays possible |
| B.5 | Impact half-life | **§11.6 T3.11**, RQ9 | Carried; flagged as speculative in §47.3 |
| B.6 | Impact oracle for coding agents | **§44 U2** | Relocated to deferred; MCP tool (T5.5) kept as the hook |
| B.7 | The economics section | **§14.4 T6.10** | Carried |
| B.8 | Extended Research Questions RQ5–RQ11 | **§11.6.6** | Carried |
| C.0 | The context header | **§34.3** | Carried verbatim |
| C.1 | `T0.2a` Token pool prompt | **§34.4 C.1** | Carried verbatim |
| C.2 | `T1.1g` Test ID normalization prompt | **§34.4 C.2** | Carried verbatim |
| C.3 | `T1.3b` Fault-revealing set prompt | **§34.4 C.3** | Carried verbatim |
| C.4 | `T2.2c` Incremental graphs prompt | **§34.4 C.4** | Carried verbatim |
| C.5 | `T3.7` Graphify baseline prompt | **§34.4 C.5** | Carried verbatim |
| C.6 | Reusable prompt template | **§34.4 C.6** | Carried verbatim + new C.7–C.9 |
| D | Repository Layout | **§33** | Carried |
| E | Course Deliverable Mapping | **§38** | Carried + expanded (§37.2 collisions) |
| F | Additional Risks T7–T12 | **§6.1** | Carried + expanded (T13–T19) |
| G | What Changed From Volume I (12 items) | **Applied throughout**; recorded in **Appendix B.2** | Merged — see note below |
| Closing note | — | **§48** | Merged with v1's Final Note |

**Note on v2 Part G.** Part G was a *delta description* — a list of twelve corrections v2 made to v1. In a unified document a delta list is not content; it is an instruction. All twelve have therefore been **applied in place** (the corrected values now appear in the relevant sections) rather than reproduced as a standalone list, and the list itself is preserved in **Appendix B.2** as changelog history. This is the only place where a source section was transformed rather than carried, and it is done to satisfy R1's *intent* — no idea lost — rather than its letter.

## A.3 `Zerothreview_Template__2_.pdf` → destination

| Source element | Destination | Status |
| --- | --- | --- |
| Approved title "BlastRadius" | §4.4, D-08 | Carried (dataset named separately) |
| Team + registration numbers | §36 | Carried |
| Guide (Dr. Yoga Raja C A) | §36, §43 Q9, §46 item 8 | Carried |
| Approved abstract text | §2.3, §4.5 | Carried; every clause mapped in the §4.5 drift register |
| 7 approved references | §47.1 | Carried verbatim; each differentiated in §28.2 |
| Approval status (YES, 16-07-2026) | §3, §38 | Carried |

## A.4 Merge-brief requirements → destination

| Brief requirement | Destination |
| --- | --- |
| R1 zero loss | This appendix |
| R2 v1 as spine | Part order, §§1–14 numbering, §0.3 states the one deviation |
| R3 dedup only on identical deliverables | §29 (reuse maps merged), §38 (course mapping merged), §48 (closing notes merged) |
| R4 new material at end of Part | Every `N.x Expansion` subsection |
| R5 conflicts → Decision blocks | **§42**, D-01 … D-18 |
| R6 provenance tags | Every top-level item; legend in §0.1 |
| Graph layer as first-class chapter | **Part IV**, §§15–20 |
| Dataset & evaluation of equal weight | **Part V**, §§21–28 |
| Product & delivery layer | §4 (vision/personas/non-goals), Part VII §§35–41 |
| Prioritization + MVP cut line | **§39**, §39.1 |
| Risk register incl. 4 named risks | §6.3 — graph scale (T15), CI signal (T17), schema churn (T18), placement collision (T13) |
| Dependency graph | **§40** |
| Open questions | **§43** |
| Deferred upgrade paths | **§44** |
| Research expansion with findable citations | **§47.3**, `[unverified]` marks in §47.2 |
| Coverage matrix / changelog / glossary / self-check | Appendices A / B / C / D |

---

# Appendix B — Changelog

## B.1 What this merge pass changed

| # | Change | Rationale |
| --- | --- | --- |
| 1 | Added **Part IV** (graph layer, §§15–20) as a first-class chapter | v1 specified the graph in five subtasks inside Phase 2 — enough to schedule, not enough to build. This is the one structural deviation from R2 and it is declared in §0.3 |
| 2 | Added **Part V** (dataset & evaluation, §§21–28) | The dataset is the primary contribution (D-02); it deserves at least the weight given to the model |
| 3 | Added **§4** product layer — vision, 6 personas, 10 non-goals, scope-drift register | Nothing in either source stated who this is for or what it refuses to do. The non-goals are load-bearing: "we do not claim safety" appears in §17.1 and §45 |
| 4 | Added **§42 Decision Register**, D-01 … D-18 | Six genuine conflicts existed between the sources and were resolved silently nowhere. Now each has both options, a recommendation, a door-direction, and a revisit trigger |
| 5 | Added **T13–T19** to the threat register | Notably **T13 placement-season collision**, which v1 and v2 both ignored despite Deepanshu owning the entire critical path |
| 6 | Added **Gate 1.5** (binding rate ≥70%, Week 5) | Promoted from v2 G.11. The most likely silent failure mode in the project |
| 7 | Added **§39 prioritization + the Review 1 MVP cut line** | Neither source said what *not* to build before Review 1. The cut line is the operative output of the whole appendix |
| 8 | Added **§40 dependency graph** with the five hard blocking edges | Makes the `test_id` contract's centrality visible rather than implicit |
| 9 | Added **§41 metrics** — engineering SLOs and project-health indicators | v1 had research metrics only |
| 10 | Added **§44 deferred upgrade paths** U1–U15 with trigger conditions | Converts "not now" into "not until the data says so" |
| 11 | Added **§47.3 grounded prior art**, with speculative design ideas explicitly quarantined | The brief required findable citations and no invented numbers. Chianti, Judge, ROSE, GumTree, Rothermel's safety definition, and Allamanis on duplication are now cited where they do actual work |
| 12 | Added **6 new rows to the Reviewer Pre-Mortem** (#15–#20) | Unsoundness, leakage, binding rate, fork provenance, operating point, class imbalance — the six objections the new depth invites |
| 13 | Marked unverified claims `[unverified]` throughout | Including v2's "75k-star" claim about Graphify, which is trivially checkable and must not reach a slide unchecked |
| 14 | Added `owner_backup` throughout §35–§36 | Consequence of T13 |
| 15 | Re-verified MSR 2027 dates against the live site (4 Aug 2026) | Data & Tool: abstract 5 Nov, paper 10 Nov, 4pp+1pp, single-anonymous, Dublin 26–27 Apr 2027. The brief's "~October" is the *Technical* track — see D-01 |

## B.2 v2 Part G — the twelve Volume-I corrections (applied, not just recorded)

Preserved here as history. **Each is already applied in the body**; the "Applied at" column is where to verify.

| # | Correction from Volume I | Applied at |
| --- | --- | --- |
| G.1 | `normalize_test_id` extends Graphify `ids.py` rather than being written fresh | §9.2 T1.1g, §29.6, **D-09** |
| G.2 | Test-node typing becomes a registered `LanguageResolver` plugin | §10.4 T2.3b, §29.6, **D-10** |
| G.3 | Graphify's PR/CI parsing lifted for the harvester | §8.4 T0.3h |
| G.4 | Incremental rebuild gains a blocking cold-vs-incremental equivalence assertion | §10.3 T2.2e, §19.1 |
| G.5 | Graphify baseline split into COMMUNITY and DIRECT | §11.4 T3.7a–c, **D-11** |
| G.6 | Fork sequence made explicit and ordered, with `GRAPHIFY_COMMIT.txt` | §10.1, §29.3 |
| G.7 | Their test suite adopted as a regression harness | §29.5 |
| G.8 | Dependabot / bot PRs captured and tagged | §8.7 T0.6 |
| G.9 | Manifest ingestion layer added for `depends_on` edges | §10.7 T2.7 |
| G.10 | Open questions surfaced for human decision | §43 |
| G.11 | Binding-rate gate introduced at Week 5 | §37.1 **Gate 1.5** |
| G.12 | Upstream contribution scheduled *after* submission | §14.4 T6.9 |

## B.3 Versioning of this document

| Version | Date | Change |
| --- | --- | --- |
| v1.0 | — | `BlastRadius_Supreme_Roadmap_v1.md` (archived) |
| Vol II | — | `BlastRadius_Roadmap_Vol2_Graphify_and_Expansion.md` (archived) |
| **v2.0** | **4 Aug 2026** | **This document.** Unified superset; replaces both permanently |

**Update protocol.** Amend in place; add a row here; never fork this document again. If a Decision is revisited, edit the Decision block and record the reversal in §42 — do not delete the original reasoning. The reasoning is the point.

---

# Appendix C — Glossary

**APFD** — Average Percentage of Faults Detected. Standard test-prioritization metric (Rothermel et al. 2001). Not our primary metric; we rank tests for selection, not for ordering.

**Actual impact set** — in Bohner & Arnold's vocabulary, the set that genuinely changed. Here, the **fault-revealing set**.

**Base-run distance** — how many commits separate an instance's head SHA from the CI run used as its baseline. Large values weaken the causal attribution; published per instance so it can be filtered.

**Binding rate** — the fraction of parsed `test_id`s that successfully resolve to a graph node. The project's single most important internal health metric; **Gate 1.5**.

**Blast radius** — the set of tests (or files) a change can plausibly affect. Note that Graphify uses the same phrase for a *zero-hop path match* (§29.1); our usage involves traversal.

**BR-Bench** — the dataset artifact. Named separately from the tool so it can be cited independently (**D-08**).

**Causal label** — a label produced by re-executing base and head under Docker and comparing verdicts. Expensive; applied to the gold subset only.

**CHA / RTA** — Class Hierarchy Analysis / Rapid Type Analysis; classical call-graph construction algorithms that over-approximate virtual dispatch.

**Change impact analysis (CIA)** — the research area. Our contribution is a measurement *within* it, not a new CIA algorithm.

**Co-change** — files that historically change together. The standard proxy label class; **RQ1 tests whether it predicts test failure**, and the hypothesis is that it largely does not.

**Cold vs incremental build** — full graph construction from scratch versus delta application. Their outputs must be byte-identical; that equality is a blocking test (§19.1).

**Confidence tier** — Graphify's vocabulary for edge certainty, inherited for label provenance (T1.9).

**Evolutionary coupling** — co-change formalised with support / confidence / lift.

**Fault-revealing set** — the tests that fail at head and passed at base, after flakiness filtering and the broken-trunk exclusion. **This is our label.**

**Flip rate** — how often a test changes verdict without a corresponding change; the flakiness signal.

**Gold subset** — the 300–500 instances re-executed in Docker to produce causal labels; the credibility anchor for the observational corpus.

**GHA** — GitHub Actions. Log retention is 90 days, which is **T1**, the only irreversible constraint in the project.

**Graphify** — `safishamsi/graphify` (MIT), the upstream tree-sitter extraction engine we fork. Provides ~15,000 lines of infrastructure; its impact computation is zero-hop, which is why it is a baseline rather than a competitor.

**Identity map** — the table tracking node identity across renames and moves (`identity_map.parquet`, §16.5). Without it, a file rename looks like a delete plus an unrelated create.

**Instance** — one (head SHA, workflow run) pair; the unit of prediction.

**Leakage** — training-time access to information unavailable at prediction time. Audited in T4.7; the `touches_test_file` flag is the specific trap.

**LOPO** — leave-one-project-out; the cross-project generalisation protocol.

**Matrix build** — a CI job replicated across OS/version legs. Failures are unioned across legs (**D-12**).

**MSR** — Mining Software Repositories, the target conference. **Data & Tool Showcase** is the target track (**D-01**).

**Phantom edge** — a graph edge with no real dependency behind it; measured on a hand-checked sample (T2.8).

**Precision / Recall@k** — our primary reporting form. Recall@20% ("catch what fraction of real failures while running a fifth of the suite") is the headline.

**PDG / SDG / CPG** — Program Dependence Graph / System Dependence Graph / Code Property Graph. Considered and rejected as the representation (**D-05**); all require data-flow, which requires a build.

**Predictive test selection** — the task. Industrial precedent: Machalica et al., ICSE-SEIP 2019 (Meta), never independently replicated for lack of public data — which is the gap this dataset fills.

**Provenance tag** — `[v1]` `[v2]` `[merged]` `[new]` `[unverified]`; see §0.1.

**Reach curve** — recall as a function of traversal depth k; justifies the depth cap (§18.4).

**RTS** — Regression Test Selection. Ekstazi (dynamic), STARTS (static) are the real-tool baselines.

**Safety (RTS sense)** — a selection technique is *safe* if it never omits a test that could reveal a fault (Rothermel & Harrold 1997). **We explicitly do not claim safety** (§17.1, non-goal 1).

**SCIP** — SourceGraph Code Intelligence Protocol; the optional compiler-accurate precision tier for Java (**D-04**, RQ5).

**SEART GHS** — the GitHub sampling service used to construct the repo frame (Dabic et al., MSR 2021).

**Seed set** — the nodes a change directly touches; the starting point of propagation (§18.3). Bohner & Arnold's *starting impact set*.

**Snapshot + delta** — the graph versioning scheme: full graph every 50 commits, deltas between (**D-14**).

**Split (strict / permissive / raw)** — three flakiness-filtering regimes. **All headline results use `strict`**, with sensitivity analysis across the others (T3.14).

**SZZ** — the algorithm linking fixes to bug-inducing commits (Śliwerski et al., MSR 2005); needed for RQ6.

**test_id** — the canonical normalized test identifier. **The join key for the entire project**, frozen Week 1, with a contract test inherited from Graphify's `ids.py` (**D-09**).

**Unexplained fraction** — the share of predicted tests for which no graph path can be shown; reported as an honesty metric of the explainability contract (§20.4).

**Unsoundness (accepted)** — known missing edges (reflection, dynamic dispatch, DI) that we flag and feature rather than resolve. Position stated in §17 and defended with Reif et al. (ISSTA 2019).

---

# Appendix D — Self-Check

An explicit confirmation against the merge contract. Each item states what was required, what was done, and where to verify.

**1. Zero loss — every idea, feature, phase, metric, risk, tech choice, and open question from both sources survives.**
✅ **Confirmed.** Appendix A maps all 68 v1 headings and all 34 v2 headings to destinations. No row reads "dropped." Weak items (TypeScript, LLM re-ranker, cross-repo, Neo4j) are annotated with a rationale and a revisit trigger rather than removed — see D-03, D-17, U1, D-06.

**2. v1 is the structural spine; deviations are declared.**
✅ **Confirmed, with exactly one declared deviation.** Parts I–III follow v1's order, numbering, and terminology. The single deviation — extracting the deep graph specification out of Phase 2 into Part IV — is stated in §0.3 and justified by the brief's explicit requirement that the graph layer be a first-class chapter. Phase 2's subtasks remain in place at §10 and cross-reference Part IV.

**3. Deduplication only where the deliverable is identical; the more rigorous version won.**
✅ **Confirmed.** Three merges occurred: the Graphify reuse maps (§29 — v2's module-level verdicts won, v1's take/leave/build framing absorbed), the course deliverable mapping (§38 — v2's table won, v1's item list absorbed), and the two closing notes (§48 — both preserved, sequenced). No third merge was performed, because no other pair of sections described the same deliverable.

**4. New material is appended at the end of its Part, never interleaved into source prose.**
✅ **Confirmed.** Every addition sits in a numbered `Expansion` subsection (§4, §6, §8.7, §9.8, §10.7, §11.6, §12.8, §13.8, §14.4) or in a Part that did not exist in either source (IV, V, VII, VIII). v1's prose in §§1–3, §5, §7–14, §29–34, §45–48 is unedited except for provenance tags and cross-references.

**5. Every conflict is an explicit Decision with options, recommendation, door-direction, and revisit trigger.**
✅ **Confirmed.** §42 contains **D-01 through D-18**. Six are genuine source-vs-source conflicts (D-01 track, D-02 contribution claim, D-03 language scope, D-11 baseline granularity, D-15 visualisation, D-17 the Rule-6-vs-T4.4 contradiction v1 never noticed). The remainder resolve choices the brief posed. Five are marked one-way doors: D-04 (parser spine), D-05 (graph formalism), D-08 (post-DOI), D-16 (dual submission), D-18 (in practice).

**6. Provenance tags on every top-level item.**
✅ **Confirmed.** `[v1]` `[v2]` `[merged]` `[new]` `[unverified]` applied at section and item level; legend at §0.1.

**7. Depth requirements met — graph layer, dataset/evaluation, product/delivery, research expansion.**
✅ **Confirmed.**
- *Graph layer* (Part IV): ingestion and parsing with a defended parser choice and a comparison table (§15.3); full node and edge taxonomies with build tiers (§16.2–16.3); node identity across renames (§16.5); hard problems with an explicit accepted-unsoundness position (§17); diff mapping, propagation, and scoring with actual formulae (§18); incrementality, storage evaluation, and concrete budgets with a worked feasibility check (§19); ten canonical queries plus surfacing and an explainability contract (§20).
- *Dataset & evaluation* (Part V): ground truth, schema, repo selection with an eight-stage attrition funnel, **ten baselines**, metrics, threats to validity in four categories, reproducibility, and novelty positioning against **all seven approved references** (§28.2).
- *Product & delivery*: §4 (vision, six personas, ten non-goals) and Part VII (task graph, ownership with backups, dual-clock timeline with a collision map, prioritization with the Review 1 MVP cut line, dependency graph with five hard blocking edges, metrics including engineering SLOs).
- *Research expansion*: §47.3 cites work specifically enough to locate — Chianti, PathImpact, Judge, ROSE, GumTree, Rothermel's safety definition, Allamanis on duplication — and quarantines our own speculative proposals in a closing paragraph.

**8. No invented numbers; unverified claims are marked.**
✅ **Confirmed.** Every metric threshold in this document is a *target we set* (70% binding rate, 5,000 instances, ≤10 s incremental build) or a *budget we computed* (§19.4), never a result we claim. All performance figures are stated as SLOs or hypotheses. Fifteen literature entries carry `[unverified]`, and v2's "75k-star" claim about Graphify is flagged explicitly in Appendix B.1 item 13. The one factual claim I re-verified externally is the MSR 2027 calendar (§3, D-01).

**Additionally confirmed:** the output is a single self-contained Markdown file with a stable-numbered table of contents; all comparisons are in tables (§15.3 parsers, §19.2 storage, §24 baselines, §28.2 references, §39 prioritization, §41 metrics); and nothing has been truncated or replaced with a placeholder.

