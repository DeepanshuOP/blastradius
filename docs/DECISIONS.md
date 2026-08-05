# BlastRadius — Decisions in Force

> Condensed from `ROADMAP.md` §42. **Recommendations only** — the full options, reasoning, and reversibility analysis are in the roadmap.
>
> These are constraints, not suggestions. If a task appears to require violating one, **stop and ask Deepanshu.**

| # | Decision | In force | Door | Revisit when |
|---|---|---|---|---|
| **D-01** | Target track | **MSR 2027 Data & Tool Showcase.** 4pp, single-anonymous, abstract 5 Nov, paper 10 Nov | one-way after 20 Oct | Gate 3 passes by Wk 9 **and** baselines complete by 5 Oct **and** all three agree |
| **D-02** | Claimed contribution | **Dataset + honest evaluation.** Not a novel SOTA predictor. Negative model results are publishable | two-way | Model wins cross-project by a large robust margin |
| **D-03** | Language scope | **Java + Python. TypeScript is cut** | two-way to add; one-way to drop Java | Phase 2 exits a full week early AND Gate 1 comfortably passed |
| **D-04** | Parser strategy | **tree-sitter spine everywhere** + optional SCIP tier on reproducible-build Java. Build-independence is non-negotiable | one-way for the spine | Java phantom-edge rate > 25% → SCIP becomes required for Java |
| **D-05** | Graph formalism | **Multi-layer typed property graph.** No data-flow, no PDG, no CPG | **one-way** | Never within this project |
| **D-06** | Storage | **NetworkX in-process + DuckDB/Parquet as system of record.** No graph database | two-way | Single repo graph > 2M nodes → evaluate **Kuzu** first |
| **D-07** | Diff extraction | **Tier 1 tree-sitter symbol diff corpus-wide; Tier 2 GumTree on the gold subset only** | two-way | Tier1/Tier2 agreement < 85% on gold |
| **D-08** | Naming | Project `BlastRadius`; **dataset named `BR-Bench`** separately | one-way after DOI | Week 1 only, then stop discussing |
| **D-09** | Test-ID normalizer | **Extend `vendor/graphify-br/graphify/ids.py`.** Do not write a fresh one — same normalizer for test IDs and node IDs is what makes the join work | two-way, painful | None expected |
| **D-10** | Test-node typing | **Registered `LanguageResolver` plugin** in graphify's `resolver_registry`, upstreamable | two-way | None |
| **D-11** | Graphify baseline | **Two baselines:** `GRAPHIFY-COMMUNITY` (generous) and `GRAPHIFY-DIRECT` (floor). Their impact computation is zero-hop — do not strawman it | two-way | None |
| **D-12** | Matrix builds | **Union failures across legs**, record `n_matrix_legs` | two-way | >20% of instances have `n_matrix_legs > 1` → sensitivity analysis. **Decide Week 2** |
| **D-13** | Monorepos | **Excluded from the v1 frame**, exclusion counted and reported | two-way | Exclusion costs >15% of usable repos. **Decide Week 3** |
| **D-14** | Graph versioning | **Snapshot every 50 commits + deltas**, materialised at instance base SHAs only | two-way | Graph store > 150 GB |
| **D-15** | Visualisation | vis.js (forked) for internal/CLI; **Cytoscape.js for the public demo** (compound nodes = free hairball defence) | two-way, ~1 day | Prisha's call, Week 8 |
| **D-16** | Dual submission | **No. Single submission to Data & Tool** | **one-way** | Only if a faculty co-author confirms no text overlap |
| **D-17** | LLM in pipeline | **Zero LLM calls in the reproducible core** — harvest, parse, label, graph, features, models, baselines, every published number. Re-ranker is an optional demo path only, and is cut entirely if its responses can't be cached and released | two-way | If not replayable, cut it |
| **D-18** | Placement collision | **Blackout window declared Week 1.** Deepanshu's critical path front-loaded into August; named backups must each run the critical component **before** the window opens | one-way in practice | As soon as the placement calendar is known — **Week 1 action** |

## The three that most often get violated silently

- **D-17** — someone adds "just one" LLM call for convenience. Any number touched by it is unpublishable.
- **D-09** — someone writes a second normalizer that is independently correct but disagrees on one Unicode edge case. Bindings drop silently.
- **D-05 / scope** — someone implements documented-but-deferred node types because Part IV describes them. Part IV is a spec, not a work order.
