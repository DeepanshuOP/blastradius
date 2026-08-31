# BlastRadius — Live Task Board

> Extracted from `ROADMAP.md` §35. **This file is the burn-down; the roadmap is the reference.**
>
> **How to use:** tick boxes as tasks land. Bring the diff to the Sunday checkpoint. ⭐ marks tasks where getting it wrong invalidates downstream work — those get a second pair of eyes before merge.
>
> **Owners:** (D) Deepanshu · (P) Prisha · (S) Sanskriti. Backups per §36 — the backup must have *run* the component once before the placement blackout (D-18).

## Gates

- [ ] **Gate 1** — end Week 4 — ≥5,000 positive instances in `strict`
- [ ] **Gate 1.5** — end Week 5 — **test-node binding rate ≥70%** ⭐ *the most likely silent failure*
- [ ] **Gate 2** — end Week 7 — RQ1 divergence result statistically solid
- [ ] **Gate 3** — end Week 9 — model beats best baseline, within-project, p < 0.05

*Every gate failure still produces a submittable paper. See ROADMAP §37.1 for the failure branch of each.*

## Review 1 cut line (late Aug / early Sep)

Must exist — see ROADMAP §39.1:

- [ ] Harvester running ≥2 weeks, dashboard live *(this is the demo)*
- [ ] Attrition funnel with real numbers
- [ ] Parser suite: JUnit XML + pytest, precision number on the 40-log fixture set
- [ ] `normalize_test_id()` with contract test passing
- [ ] Labelling engine v0 on ≥20 repos
- [ ] (CUT - Roadmap Phase removed) Commit-pinned graph on the 3-repo mini-corpus, node/edge counts
- [ ] Architecture diagram + literature positioning
- [ ] Scope-drift conversation with the guide — **done, not pending**

**Explicitly not started before Review 1:** predictor · GNN · demo UI · GitHub Action · MCP tool · SCIP tier · LLM re-ranker · test-gap detection · calibration · TypeScript.

---

`[merged v1 + v2 Part G]` — each line is a self-contained micro-task. Copy one, add the §34.3 context header, hand it to Claude Code. ⭐ marks a task where getting it wrong invalidates downstream work.

### Week 0 — Harvester (Aug 4–10) 🔴
- [x] `T0.1a` Export SEART query → `data/frame/repos_raw.csv`; document query in `QUERY.md`
- [x] `T0.1b` Implement `src/harvest/liveness.py` — CI-liveness filter via `total_count` (implemented as fetch_n_runs_90d in src/harvest/frame.py)
- [x] `T0.1c` Implement `src/harvest/workflow_triage.py` — classify workflows test/build/deploy (implemented as classify_workflows / is_test_intent in src/harvest/frame.py)
- [x] `T0.1d` Produce `repos.csv` (300 candidates); manual review of top 50
- [x] `T0.2a` Implement `TokenPool` with quota-aware round-robin
- [x] `T0.2b` Implement `get_with_backoff()` — sole HTTP entry point
- [x] `T0.2c` Add request logging + `--dry-run` budget estimator
- [x] `T0.3a` SQLite cursor store + resume logic
- [x] `T0.3b` PR + commits + runs capture loop → gzipped JSONL
- [x] `T0.3c` Check-run annotations capture (priority: persists >90d)
- [x] `T0.3d` Artifact capture with name/size filter
- [x] `T0.3e` Job-log capture, failures prioritised
- [x] `T0.3f` SIGTERM flush + daily MANIFEST.json
- [ ] `T0.3g` Deploy as cron daemon in WSL2 + redundant GHA scheduled harvester
- [ ] `T0.3h` `[v2]` Lift `_parse_ci` + `_path_match` from graphify `prs.py`
- [ ] `T0.4a` Directory contract + CHECKSUMS
- [ ] `T0.4b` Nightly rclone/rsync mirror; verify by restoring one file
- [x] `T0.5a` Streamlit corpus dashboard
- [ ] `T0.6` `[v2]` Dependabot / bot-PR capture with `is_bot_pr` tagging
- [x] `T0.7` `[new]` Attrition funnel instrumentation → `ATTRITION.json` + dashboard
- [x] `T0.8` `[new]` Frame freeze + version tag before Phase 1

### Weeks 1–4 — Corpus & Ground Truth (Aug 10–Sep 6)
- [x] `T1.1a` Build 40-log fixture corpus with hand-labelled expected output
- [x] `T1.1b` `annotations.py` parser
- [x] `T1.1c` `junit_xml.py` parser (Surefire + pytest)
- [x] `T1.1d` `log_pytest.py` parser
- [x] `T1.1e` `log_maven.py` parser
- [x] `T1.1f` `log_gradle.py` parser
- [x] `T1.1g` `normalize_test_id()` extending graphify `ids.py` + contract test ⭐
- [ ] `T1.1h` `resolve_test_file()` + binding-rate report ⭐
- [ ] `T1.1i` Per-parser coverage + precision report
- [ ] `T1.2a` Changed-file extraction with hunks
- [ ] `T1.2b` tree-sitter symbol-level change extraction
- [ ] `T1.2c` Change taxonomy flags (full taxonomy §18.2)
- [x] `T1.3a` Base-run resolution with `base_run_distance` ⭐
- [x] `T1.3b` Fault-revealing set computation (broken-trunk filter) ⭐
- [ ] `T1.3c` Same-SHA flip detection
- [ ] `T1.3d` Rolling flip-rate flakiness scoring
- [x] `T1.3e` Three splits: strict / permissive / raw
- [x] `T1.3f` Emit `instances.parquet` + `outcomes.parquet`
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
- [ ] (CUT) `T2.1a` Fork Graphify v8 → `vendor/graphify-br/`, preserve LICENSE + NOTICE
- [ ] (CUT) `T2.1b` Strip LLM pass and non-code extractors
- [ ] (CUT) `T2.1c` Pin versions; re-run their test suite
- [ ] (CUT) `T2.1d` `[v2]` Record `GRAPHIFY_COMMIT.txt`; follow the ordered fork sequence §10.1
- [ ] (CUT) `T2.2a` `git worktree` commit-pinned checkout manager
- [ ] (CUT) (CUT - Roadmap Phase removed) `T2.2b` Graph build at SHA → `graph_{repo}_{sha}.json`
- [ ] (CUT) `T2.2c` Incremental rebuild via content hashing ⭐
- [ ] (CUT) (CUT - Roadmap Phase removed) `T2.2d` Graph validation + parse-failure-rate gate
- [ ] (CUT) `T2.2e` `[v2]` Incremental-vs-cold equivalence assertion (blocking) ⭐
- [ ] (CUT) `T2.2f` `[new]` Snapshot + delta storage and `graph_index.parquet` (§19.3)
- [ ] (CUT) `T2.3a` Node type classification (test/source/config/build)
- [ ] (CUT) `T2.3b` `test_id` ↔ test-node binding as a registered `LanguageResolver` ⭐
- [ ] (CUT) `T2.3c` `tests` / `tests_by_convention` / `tests_by_layout` edges
- [ ] (CUT) `T2.3d` Extended edge-type schema (§16.3)
- [ ] (CUT) `T2.3e` `[new]` Binding-rate report + dashboard tile ⭐ (**Gate 1.5**)
- [ ] (CUT) `T2.4a` `co_changes` weighted edges
- [ ] (CUT) `T2.4b` `co_fails` edges
- [ ] (CUT) `T2.4c` Node attributes (churn, complexity, age, failure rate)
- [ ] (CUT) `T2.5a` Query API primitives (§20.1 Q1–Q10)
- [ ] (CUT) `T2.5b` DuckDB feature cache + benchmark
- [ ] (CUT) `T2.6` `[v2]` SCIP precision tier on the Java subset (RQ5, optional)
- [ ] (CUT) `T2.7` `[v2]` `manifest_ingest` package layer + `depends_on` edges
- [ ] (CUT) `T2.8` `[new]` Phantom-edge rate measurement, 100 hand-checked edges/language
- [ ] (CUT) `T2.9` `[new]` Graph-quality dashboard tiles (binding / parse-fail / orphan / phantom)
- [ ] (CUT) `T2.10` `[new]` Node identity map (`identity_map.parquet`, §16.5)
- [ ] (CUT) `T2.11` `[new]` Dynamic-boundary flagging (§17.3)

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
- [ ] (CUT) (CUT - Roadmap Phase removed) `T4.1a` Graph feature extraction
- [ ] (CUT) `T4.1b` Change feature extraction
- [ ] (CUT) `T4.1c` Test-history feature extraction
- [ ] (CUT) `T4.1d` Cross features + leakage audit ⭐
- [ ] (CUT) `T4.1e` `[new]` Dynamic-boundary features
- [ ] (CUT) `T4.2a` LightGBM lambdarank + Optuna sweep
- [ ] (CUT) `T4.2b` SHAP attribution
- [ ] (CUT) (CUT - Roadmap Phase removed) `T4.3a` PyG heterogeneous graph construction
- [ ] (CUT) `T4.3b` Neighbour-sampled R-GCN training loop
- [ ] (CUT) `T4.3c` Focal loss + early stopping on Recall@20%
- [ ] (CUT) `T4.4` (optional) Claude re-ranker over top-50
- [ ] (CUT) `T4.5a` 5-seed runs, mean ± std
- [ ] (CUT) `T4.5b` Ablation table (graph/history/change/all)
- [ ] (CUT) `T4.5c` Learning curve vs training-set size
- [ ] (CUT) `T4.5d` Cross-project LOPO evaluation
- [ ] (CUT) `T4.6` `[v2]` Calibration: reliability diagram, Brier, cost-optimal threshold (RQ7)
- [ ] (CUT) `T4.7` `[new]` Written leakage audit + CI assertion ⭐
- [ ] (CUT) (CUT - Roadmap Phase removed) `T4.8` `[new]` File-level prediction head (§18.8)

### Weeks 10–13 — Tool & Demo (Oct 12–Nov 2)
- [ ] (CUT - Roadmap Phase removed) `T5.1` `blastradius` CLI (init/predict/explain/serve/gaps)
- [ ] `T5.2` FastAPI service + OpenAPI + caching layers (§20.2)
- [ ] `T5.3a` Next.js shell + PR URL input
- [ ] (CUT - Roadmap Phase removed) `T5.3b` Interactive graph with impact highlighting + hairball controls (§20.3)
- [ ] `T5.3c` Cost-saved panel
- [ ] `T5.3d` Four-way comparison panel (co-change / reachability / model / truth) ⭐
- [ ] `T5.3e` Vercel deploy with pre-computed examples
- [ ] `T5.4` GitHub Action + marketplace listing
- [ ] (CUT - Roadmap Phase removed) `T5.5` MCP `predict_blast_radius` tool in the fork's `serve.py`
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