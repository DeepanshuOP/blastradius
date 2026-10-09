# Figures and Tables Todo List: BR-Bench MSR 2027

This document tracks all figures and tables in the MSR 2027 Data Showcase paper (paper/draft/main.tex), documenting what has been generated, its source data files, and remaining author actions.

## 1. Inventory of Figures and Tables

| Item | Description | Source File / Script | Built Format | Status | Author Action Required |
|---|---|---|---|---|---|
| **Fig. 1** | Pipeline Architecture Diagram (Harvest $\to$ Parse $\to$ Normalise $\to$ Base Resolution $\to$ Label $\to$ Bind $\to$ Release Bundle) | ROADMAP.md §4, docs/SCHEMAS.md, src/label/fault_revealing.py | TikZ (paper/draft/figs/pipeline.tikz) | **Built** | Review box dimensions, font sizes, and color contrast for grayscale/print readability. |
| **Table I** | Key Schema Fields of instances.parquet and outcomes.parquet | docs/SCHEMAS.md, ROADMAP.md §31 | LaTeX 	abular in main.tex | **Built** | Confirm column names match the final Parquet exports in elease/v0.1. |
| **Table II** | Pipeline Attrition Funnels (Repositories and Workflow Runs across all stages) | paper/generated/attrition_funnel.md (nalysis/attrition_funnel.py) | LaTeX 	abular in main.tex | **Built** | Confirm authorial stance on the 76 vs 77 swept repositories discrepancy note. |
| **Table III** | Dataset Composition by Split (All, Relaxed, Strict) and Language (Java, Python) | paper/generated/composition.md (nalysis/paper_numbers.py) | LaTeX 	abular in main.tex | **Built** | Verify percentages and distinct test counts. |
| **Fig. 2** | RQ1 Micro Recall at =10$ Bar Chart (Co-change All, Co-change Test, Changeset, Historical Frequency) | paper/generated/rq1.md (nalysis/rq1_divergence.py), inspired by paper/generated/fig2_accuracy.pdf | TikZ / PGFPlots (paper/draft/figs/rq1_chart.tikz) | **Built** | Optional: Replace inline TikZ with standalone vector PDF if camera-ready workflow requires external graphics. |
| **Table IV** | Data Quality Indicators (Base Resolution, Same-SHA Flakiness, Binding Rates, Failure Class Distribution) | paper/generated/base_resolution.md, inding.md, lakiness.md, infra_failures.md | LaTeX 	abular in main.tex | **Built** | Ensure the lower-bound nature of the regex failure classification is clearly understood. |

---

## 2. Source Files for Visual Artifacts

1. **paper/draft/figs/pipeline.tikz**:
   - Implements the complete end-to-end data processing workflow.
   - Uses native TikZ nodes with styled fill colors (lue!5, orange!8, green!8).
   - Compiles inline in main.tex with no external binary dependency.

2. **paper/draft/figs/rq1_chart.tikz**:
   - Implements the comparative bar chart for RQ1 micro recall at =10$.
   - Coordinates:
     - Co-change (All): 4.64% (61/1,316)
     - Co-change (Test): 7.67% (101/1,316)
     - Changeset: 17.02% (224/1,316)
     - Historical Frequency: 39.44% (519/1,316)
   - Uses PGFPlots with 
odes near coords displaying exact percentages.

---

## 3. What the Authors Must Still Produce

1. **Final Vector Graphic Assets (Optional)**:
   - If the publisher or camera-ready instructions request standalone EPS/PDF files instead of inline TikZ/PGFPlots, compile igs/pipeline.tikz and igs/rq1_chart.tikz via pdflatex -shell-escape or standalone class into pipeline.pdf and q1_chart.pdf.

2. **Zenodo DOIs**:
   - DONE: dataset DOI 10.5281/zenodo.23250262 and code DOI 10.5281/zenodo.23250690 are minted and inserted.

3. **Author Order and Affiliation Confirmation**:
   - Confirm the final order among Prisha Vadhavkar, Sanskriti Singh, and Deepanshu before submission.
   - Remove the provisional footnote once final agreement is reached.

4. **Secret Scan Human Confirmation**:
   - Perform human review on the 5 review samples flagged in docs/FINAL_STATUS.md before final Zenodo packaging.