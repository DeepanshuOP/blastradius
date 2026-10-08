# Skeptical Reviewer Report: BR-Bench MSR 2027 Submission

**Manuscript**: paper/draft/main.tex  
**Target Venue**: IEEE/ACM MSR 2027 Data and Tool Showcase Track  
**Format**: \documentclass[10pt,conference]{IEEEtran}, 10pt, 4 pages body + 1 page references  
**Review Standards Applied**: .agents/skills/research-paper-writing-conference/references/final-submission-gate.md and paper-review.md

---

## 1. Executive Summary

This paper presents **BR-Bench**, an open benchmark linking pull-request continuous integration code changes directly to individual fault-revealing tests across Java and Python GitHub Actions pipelines.

As a reviewer evaluating this work under the standards of the MSR Data Showcase track, the primary scientific contribution is the **dataset artifact itself** rather than an empirical study. The paper properly treats RQ1 as an illustrative "example use" rather than its headline contribution. The manuscript is methodologically rigorous, honest about negative outcomes and pre-registered gate shortfalls, and completely grounded in traceable project evidence generated from paper-numbers-v1.1.

Below is an exhaustive assessment of the submission gates, reviewer dimensions, and flagged items requiring author action before camera-ready submission.

---

## 2. Reviewer Evaluation across the Five Core Dimensions

### Dimension 1: Contribution
- **Assessment**: **Strong**. Existing open benchmarks in continuous integration either predate GitHub Actions and cover only single languages (e.g., RTPTorrent on Travis CI), or provide raw unparsed log archives without test-level verdicts, base resolution, or change-to-test fault linking (e.g., GHALogs). Industrial systems at Meta and Google demonstrate the value of predictive test selection but rely on proprietary, unreleased corporate datasets. BR-Bench bridges this gap by providing an open, reproducible substrate linking git diffs to verified fault-revealing tests.
- **Strengths**: Explicit definition of fault revelation ({\text{reveal}} = (T_{\text{head\_fail}} \setminus T_{\text{base\_fail}}) \setminus T_{\text{flaky}}$), canonical test identifiers, and test-to-file binding against pinned repository trees.
- **Risks**: The dataset volume (762 strict instances, 4,168 labels) fell short of the pre-registered Gate 1 threshold (5,000), and the corpus is heavily skewed towards Java (83.7% of strict instances, 92.5% of labels).

### Dimension 2: Writing Clarity
- **Assessment**: **Very Good**. The structure adheres strictly to the required MSR sections: Introduction $\to$ Data Source \& Collection $\to$ Storage \& Schema $\to$ Dataset Overview \& Quality $\to$ RQ1 Example Use $\to$ Originality $\to$ Limitations $\to$ Future Work $\to$ Availability $\to$ Conclusion.
- **Tone**: Concrete, factual, and free of hype. Forbidden marketing terms ("novel", "state-of-the-art", "significantly") have been avoided. Every drafted paragraph is marked % [AI DRAFT] to facilitate the authors' personal human-authorship rewrite.
- **Visuals**: Fig. 1 (TikZ pipeline) clearly communicates data flow; Table I defines core schema structures; Table II captures attrition; Table III provides split and language breakdowns; Fig. 2 clearly displays RQ1 micro recall comparisons; Table IV documents data quality metrics.

### Dimension 3: Experimental Strength
- **Assessment**: **Sound and Properly Positioned**. RQ1 evaluates four test selection proxies at budget =10$ on an identical set of =576$ instances where all-partner co-change fires (,316$ positive test labels).
- **Leakage Control**: Crucially, the authors audited and eliminated historical data leakage (fixing future commit leakage in 713/713 instances, eliminating double-counting across splits in 721/762 instances, and implementing symmetric partner lookups).
- **Finding**: Historical failure frequency achieves 39.44% micro recall compared to only 7.67% for test-restricted co-change and 4.64% for all-partner co-change, demonstrating the empirical deficiency of version-control co-change heuristics.

### Dimension 4: Evaluation Completeness & Negative Results
- **Assessment**: **Exemplary Scientific Honesty**. The authors do not hide weaknesses:
  - Gate 1 failure is clearly stated in the abstract and limitations.
  - Gate 1.5 full-confidence binding failure (63.83% vs. 70% threshold) is prominently reported alongside the combined figure (94.29%).
  - Parser evaluation on development sets (fixture corpus 46/46, holdout v1 30/30) is explicitly acknowledged as non-independent, and the uncompleted status of holdout v5 is openly admitted.
  - Failure class regex categorization is clearly qualified as a lower bound (77.69% unknown).
  - The 90-day log expiry cliff (33.21% of failed runs already purged by GitHub Actions at harvest time) is transparently reported.

### Dimension 5: Method Design Soundness
- **Assessment**: **Technically Robust**. 
  - Base resolution requires exact green or parsed failure sets, avoiding upstream defect misattribution.
  - Same-commit flakiness pruning removes 46 non-deterministic labels.
  - Pinned clone resolution ensures deterministic binding rates regardless of subsequent repository churn.
  - The pipeline runs completely deterministically without LLM dependencies.

---

## 3. Submission Gate Checklist (inal-submission-gate.md)

### Gate A — Scientific Integrity: **PASSED (with Limited Scope)**
- [x] Every important numeric claim is traceable to frozen generated tables in paper/generated/ (verified via CLAIM_LEDGER.md).
- [x] No invented results, datasets, baselines, or implementation details.
- [x] No unsupported SOTA/best/novel claims.
- [x] Limitations (Gate 1 missed, observational labels, language skew, expiry cliff) are prominently stated.

### Gate B — Human Authorship & Originality: **PASSED (Draft Mode)**
- [x] Every drafted paragraph is prefixed with % [AI DRAFT] as requested by the authors.
- [x] The manuscript serves as an initial prose pass for the student authors (Prisha Vadhavkar, Sanskriti Singh, Deepanshu) to rewrite, review, and accept before submission under MSR's AI-use policy.
- [x] No source paper or external text was copied.

### Gate C — Reproducibility: **PASSED**
- [x] Dataset schemas, splits, and preprocessing steps are fully defined.
- [x] Reproduction scripts (make tables $\approx 8$ min, make test passing 782 tests) are verified.
- [x] Raw logs and Parquet tables are deposited in the release pipeline.

### Gate D — Conference Format: **PASSED**
- [x] Uses \documentclass[10pt,conference]{IEEEtran}, standard IEEE numeric citation style, and IEEEtran.bst.
- [x] Exact page budget: precisely 4 pages of paper body + 1 page of references (total 5 pages).
- [x] Single-anonymous author names and affiliation (VIT Vellore) are included.
- [x] Tables have heads above; figures have captions below.

### Gate E — Reader Clarity: **PASSED**
- [x] One clear message per paragraph.
- [x] Stable terminology across sections ({\text{head\_fail}}, T_{\text{base\_fail}}, T_{\text{flaky}}, T_{\text{reveal}}$).
- [x] Acronyms defined upon first usage (CI, CIA, RTS, PTS, FQCN).

---

## 4. Itemised Audit: Missing Markers, Citations, DOIs, and Discrepancies

### A. Missing Information Markers ([MISSING:*])
1. **Section VII, Paragraph 3**:
   [MISSING: blind human annotations on holdout v5 fixtures]
   - *Rationale*: D-53 records that blind human annotations were not completed for the 40-log holdout v5 corpus before submission drafting. As mandated by the writing skill, we refuse to report development set figures (100% on fixture and holdout v1) as held-out generalization, and explicitly mark the independent evaluation as unmeasured.

### B. Citations Requiring Verification ([VERIFY CITATION])
1. **efs.bib / Citation [6] (memisevic2023predictive)**:
   Memisevic et al., Predictive Test Selection in Continuous Integration, Proc. IEEE/ACM Int. Conf. Softw. Eng., 2023.
   - *Action for Authors*: Confirm the exact title, author list, and publication venue for the Google predictive test selection paper before camera-ready submission.

### C. Placeholder Identifiers ([DOI-*])
1. **[DOI-DATA] (Section IX)**:
   - *Action for Authors*: Deposit elease/v0.1 onto Zenodo and replace [DOI-DATA] with the minted Zenodo DOI.
2. **[DOI-CODE] (Section IX)**:
   - *Action for Authors*: Create a tagged GitHub release and archive the code repository to mint and insert the source code DOI.

### D. Flagged Discrepancies
1. **Swept Repository Count (76 vs. 77 Repositories)**:
   - *Discrepancy*: paper/generated/attrition_funnel.md lists 76 swept repositories, whereas paper/generated/corpus_stats.md reports 77 active repositories.
   - *Explanation*: The 77th repository exists in harvested corpus metadata but yielded 0 workflow runs / 0 strict instances.
   - *Status in Paper*: Section II-A explicitly documents the 76 swept repositories and flags the 77th metadata repository in parenthetical text.
2. **Pre-registered Gate 1 Threshold (5,000 Positives)**:
   - *Discrepancy*: Gate 1 stands at 4,168/5,000 labels (83.36%) and 762/5,000 instances (15.24%).
   - *Status in Paper*: Prominently acknowledged as NOT MET in both the Abstract and Section VII (Limitations).
3. **Pre-registered Gate 1.5 Threshold (70% Binding)**:
   - *Discrepancy*: Full-confidence FQCN binding is 3,820/5,985 (63.83%), which is below 70%. Combined binding (including basename matches) is 5,643/5,985 (94.29%).
   - *Status in Paper*: Both figures are reported together; the shortfall on full confidence is explicitly acknowledged.
4. **Secret Scan Human Confirmation**:
   - *Discrepancy*: docs/FINAL_STATUS.md records that 5 review samples in the secret scan still require human verification prior to public Zenodo upload.
   - *Status in Paper*: Documented in Section III; authors must complete the inspection before publishing elease/v0.1.
5. **Author Order**:
   - *Discrepancy*: Author order is currently listed as Prisha Vadhavkar, Sanskriti Singh, Deepanshu.
   - *Status in Paper*: A provisional title footnote explicitly states that author order is subject to final confirmation among the student authors.

---

## 5. Verification Command Summary

The following command sequence was executed in WSL Ubuntu to verify compilation and page budgets:
`ash
cd paper/draft
pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
pdftotext main.pdf - | grep -E '\[[0-9]+\]'
`
**Compilation Result**: Clean build, 0 errors, exactly **5 pages** (Pages 1--4: Main Text ending cleanly with Conclusion; Page 5: References).