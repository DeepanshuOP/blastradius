#!/usr/bin/env python3
"""Unbiased Census of GitHub Check-Run Annotations across captured repositories.

Per ROADMAP §5.5, §34.4 C.2, and T1.1g.
Generates paper/generated/annotation_census.md and prints to stdout.
"""

from __future__ import annotations

import base64
import glob
import gzip
import json
import math
import os
import re
import sys
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from analysis import paper_md

RUNTIME_S = 0.0

SEED = 20261110
TARGET_SAMPLE_SIZE = 1500

IDENTIFIER_RE = re.compile(r"^[\w.$]+(?:#|::)[\w$]+")
DOTTED_FQN_RE = re.compile(r"^[a-zA-Z_$][\w$]*(?:\.[a-zA-Z_$][\w$]*)+$")

# Common code file extensions
SOURCE_EXTENSIONS = {
    ".java", ".py", ".kt", ".groovy", ".scala",
    ".ts", ".js", ".c", ".cpp", ".h", ".hpp", ".cs", ".go", ".rs", ".rb", ".php"
}

# Substrings / patterns indicating a test path
TEST_PATH_SUBSTRINGS = ["/test/", "/tests/", "test_", "_test.", "Test.java", ".test.", "Tests.java"]


@dataclass
class AnnotationRecord:
    repo: str
    file_path: str
    level: str
    raw_title: Optional[str]
    clean_title: Optional[str]
    raw_path: Optional[str]
    clean_path: Optional[str]
    path_category: str
    is_test_path: bool
    is_title_non_null: bool
    is_title_identifier: bool
    message_excerpt: str


def classify_path(raw_path: Optional[str]) -> Tuple[str, bool]:
    """Classify the annotation path into one of the canonical census categories."""
    if raw_path is None or not str(raw_path).strip():
        return ("null/empty", False)
    
    p = str(raw_path).strip()
    norm_p = p.replace("\\", "/")
    
    # Dotted FQN without file path slashes
    if "/" not in norm_p and DOTTED_FQN_RE.match(p):
        return ("dotted_fqn", False)
    
    # Workflow / Config files
    if norm_p.startswith(".github") or any(norm_p.endswith(ext) for ext in [
        ".yml", ".yaml", ".md", ".toml", ".json", ".xml", ".properties", ".gradle"
    ]):
        return ("workflow/config (.github, .yml, .md)", False)
    
    # Check if code file
    ext = Path(norm_p).suffix.lower()
    is_code = ext in SOURCE_EXTENSIONS or any(norm_p.endswith(e) for e in SOURCE_EXTENSIONS)
    
    if is_code:
        # Check test file pattern
        if any(sub in norm_p for sub in TEST_PATH_SUBSTRINGS):
            return ("test-path source file", True)
        return ("source file (.java/.py)", False)
    
    return ("other", False)


def compute_percentile(sorted_list: Sequence[int], p: float) -> float:
    """Compute percentile from sorted list."""
    if not sorted_list:
        return 0.0
    k = (len(sorted_list) - 1) * p
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return float(sorted_list[int(k)])
    d0 = sorted_list[int(f)] * (c - k)
    d1 = sorted_list[int(c)] * (k - f)
    return d0 + d1


def sample_files(
    repo_files: Dict[str, List[str]],
    target_sample: int,
    seed: int
) -> Tuple[List[str], Dict[str, int], Dict[str, int]]:
    """Deterministically take a stratified proportional random sample of files."""
    import random
    rng = random.Random(seed)
    
    total_files = sum(len(flist) for flist in repo_files.values())
    if total_files <= target_sample:
        sampled = []
        allocations = {}
        for r, flist in sorted(repo_files.items()):
            sampled.extend(flist)
            allocations[r] = len(flist)
        return sampled, allocations, {r: len(flist) for r, flist in repo_files.items()}
    
    allocations = {}
    remainders = []
    
    for repo, flist in sorted(repo_files.items()):
        n_r = len(flist)
        exact_share = (n_r / total_files) * target_sample
        base = int(exact_share)
        rem = exact_share - base
        allocations[repo] = max(1 if n_r > 0 else 0, base)
        remainders.append((rem, repo))
    
    curr_total = sum(allocations.values())
    diff = target_sample - curr_total
    
    if diff > 0:
        remainders.sort(key=lambda x: x[0], reverse=True)
        for _, repo in remainders[:diff]:
            allocations[repo] = min(len(repo_files[repo]), allocations[repo] + 1)
    elif diff < 0:
        remainders.sort(key=lambda x: x[0])
        for _, repo in remainders[:abs(diff)]:
            if allocations[repo] > 1:
                allocations[repo] -= 1
                
    sampled_files = []
    for repo in sorted(repo_files.keys()):
        flist = sorted(repo_files[repo])  # sort deterministically first
        k = allocations[repo]
        sampled_files.extend(rng.sample(flist, k))
        
    return sampled_files, allocations, {r: len(flist) for r, flist in repo_files.items()}


def run_census() -> str:
    """Execute the full census and return the markdown report."""
    t0 = time.perf_counter()
    
    # 1. Snapshot all annotation files under data/raw
    all_files = sorted(glob.glob("data/raw/*/checkrun/*/*/annotations.jsonl.gz"))
    repo_files: Dict[str, List[str]] = defaultdict(list)
    for f in all_files:
        parts = f.split("/")
        if len(parts) >= 3:
            repo_files[parts[2]].append(f)
            
    total_captured_files = len(all_files)
    total_repos_with_annotations = len(repo_files)
    
    # 2. Stratified proportional sampling
    sampled_files, allocations, repo_totals = sample_files(
        repo_files, TARGET_SAMPLE_SIZE, SEED
    )
    actual_sample_size = len(sampled_files)
    sampling_fraction = (actual_sample_size / total_captured_files) if total_captured_files > 0 else 0.0
    
    # 3. Process sampled files
    empty_files_count = 0
    empty_arrays_count = 0
    base64_encoded_records_count = 0
    differing_shape_files = 0
    
    annotations_per_file: List[int] = []
    records: List[AnnotationRecord] = []
    
    level_counter: Counter = Counter()
    path_counter: Counter = Counter()
    null_title_count = 0
    
    plausible_identifiers: List[Tuple[str, str, str]] = []
    prose_titles: List[Tuple[str, str, str]] = []
    
    repo_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
        "sampled_files": 0,
        "total_files": 0,
        "total_annotations": 0,
        "test_and_title_annotations": 0,
    })
    
    for r, count in allocations.items():
        repo_stats[r]["sampled_files"] = count
        repo_stats[r]["total_files"] = repo_totals[r]
        
    for fpath in sampled_files:
        repo = fpath.split("/")[2]
        file_annotation_count = 0
        file_had_content = False
        
        try:
            with gzip.open(fpath, "rt", encoding="utf-8", errors="replace") as f:
                for line in f:
                    try:
                        data = json.loads(line)
                    except Exception:
                        differing_shape_files += 1
                        continue
                    
                    if isinstance(data, dict) and "_footer" in data:
                        continue
                    
                    if not isinstance(data, dict) or "body" not in data:
                        differing_shape_files += 1
                        continue
                    
                    raw_body = data["body"]
                    enc = data.get("encoding")
                    if enc == "base64":
                        base64_encoded_records_count += 1
                        try:
                            raw_body = base64.b64decode(raw_body).decode("utf-8", errors="replace")
                        except Exception:
                            differing_shape_files += 1
                            continue
                            
                    try:
                        items = json.loads(raw_body)
                    except Exception:
                        differing_shape_files += 1
                        continue
                        
                    if isinstance(items, list):
                        if len(items) == 0:
                            empty_arrays_count += 1
                        else:
                            file_had_content = True
                            for it in items:
                                if not isinstance(it, dict):
                                    continue
                                file_annotation_count += 1
                                level = str(it.get("annotation_level", "unknown")).lower()
                                level_counter[level] += 1
                                
                                raw_title = it.get("title")
                                clean_title = str(raw_title).strip() if raw_title is not None else ""
                                is_title_non_null = bool(clean_title)
                                
                                if not is_title_non_null:
                                    null_title_count += 1
                                    
                                raw_p = it.get("path")
                                clean_p = str(raw_p).strip() if raw_p is not None else ""
                                path_cat, is_test_p = classify_path(clean_p)
                                path_counter[path_cat] += 1
                                
                                is_ident = False
                                if is_title_non_null:
                                    if IDENTIFIER_RE.match(clean_title):
                                        is_ident = True
                                        plausible_identifiers.append((repo, clean_title, clean_p))
                                    else:
                                        prose_titles.append((repo, clean_title, clean_p))
                                        
                                msg_excerpt = str(it.get("message", "")).replace("\n", " ")[:80]
                                
                                rec = AnnotationRecord(
                                    repo=repo,
                                    file_path=fpath,
                                    level=level,
                                    raw_title=raw_title,
                                    clean_title=clean_title if is_title_non_null else None,
                                    raw_path=raw_p,
                                    clean_path=clean_p if clean_p else None,
                                    path_category=path_cat,
                                    is_test_path=is_test_p,
                                    is_title_non_null=is_title_non_null,
                                    is_title_identifier=is_ident,
                                    message_excerpt=msg_excerpt,
                                )
                                records.append(rec)
                                
                                repo_stats[repo]["total_annotations"] += 1
                                if is_test_p and is_title_non_null:
                                    repo_stats[repo]["test_and_title_annotations"] += 1
                    else:
                        differing_shape_files += 1
        except Exception:
            differing_shape_files += 1
            
        if not file_had_content:
            empty_files_count += 1
            
        annotations_per_file.append(file_annotation_count)
        
    t1 = time.perf_counter()
    global RUNTIME_S
    RUNTIME_S = t1 - t0  # wall-clock: stdout only, never in the file
    
    # 4. Compute distributions
    total_ann = len(records)
    annotations_per_file.sort()
    
    min_ann = annotations_per_file[0] if annotations_per_file else 0
    median_ann = compute_percentile(annotations_per_file, 0.50)
    p90_ann = compute_percentile(annotations_per_file, 0.90)
    max_ann = annotations_per_file[-1] if annotations_per_file else 0
    
    non_null_ann_files = [x for x in annotations_per_file if x > 0]
    med_non_null = compute_percentile(non_null_ann_files, 0.50) if non_null_ann_files else 0
    p90_non_null = compute_percentile(non_null_ann_files, 0.90) if non_null_ann_files else 0
    
    # Cross-tab total
    cross_tab_count = sum(1 for r in records if r.is_test_path and r.is_title_non_null)
    cross_tab_pct = (cross_tab_count / total_ann * 100) if total_ann > 0 else 0.0
    
    # Build Markdown Output
    lines: List[str] = []
    lines.append(paper_md.header("GitHub Check-Run Annotation Census", "analysis/annotation_census.py").rstrip("\n"))
    lines.append("")
    lines.append(f"Unbiased stratified random census of **{actual_sample_size:,}** check-run annotation files")
    lines.append(f"drawn from **{total_captured_files:,}** captured files across **{total_repos_with_annotations}** repositories (Seed: `{SEED}`).")
    lines.append("")
    
    # Section 1: Sampling & Stratification
    lines.append("## 1. Sampling & Stratification Breakdown")
    lines.append("")
    lines.append(f"- **Total Annotation Files in Corpus:** {total_captured_files:,}")
    lines.append(f"- **Target Sample Size:** {TARGET_SAMPLE_SIZE:,}")
    lines.append(f"- **Actual Sampled Files:** {actual_sample_size:,}")
    lines.append(f"- **Sampling Fraction:** {sampling_fraction:.4f} ({sampling_fraction*100:.2f}%)")
    lines.append(f"- **Files with Differing Envelope Shape:** {differing_shape_files}")
    lines.append(f"- **Base64 Encoded Records:** {base64_encoded_records_count}")
    lines.append(f"- **Files with Empty Payload / Array:** {empty_files_count:,} ({empty_files_count/actual_sample_size*100:.2f}%)")
    lines.append("")
    lines.append("| Repository | Total Files in Corpus | Sampled Files | Sampling Share |")
    lines.append("| :--- | :---: | :---: | :---: |")
    for r in sorted(repo_stats.keys()):
        st = repo_stats[r]
        tot = st["total_files"]
        smp = st["sampled_files"]
        pct = (smp / tot * 100) if tot > 0 else 0.0
        lines.append(f"| `{r}` | {tot:,} | {smp:,} | {pct:.2f}% |")
    lines.append(f"| **Total** | **{total_captured_files:,}** | **{actual_sample_size:,}** | **{sampling_fraction*100:.2f}%** |")
    lines.append("")
    
    # Section 2: Annotation Volume Distribution
    lines.append("## 2. Annotation Volume Distribution")
    lines.append("")
    lines.append(f"- **Total Annotations Extracted:** {total_ann:,}")
    lines.append(f"- **Annotations per File (all {actual_sample_size:,} sampled files):** Min = {min_ann}, Median = {median_ann:.1f}, P90 = {p90_ann:.1f}, Max = {max_ann}")
    lines.append(f"- **Annotations per Non-Empty File ({len(non_null_ann_files):,} files):** Min = {non_null_ann_files[0] if non_null_ann_files else 0}, Median = {med_non_null:.1f}, P90 = {p90_non_null:.1f}, Max = {max_ann}")
    lines.append("")
    
    # Section 3: Title & Level Breakdown
    lines.append("## 3. Title Nullness & Annotation Levels")
    lines.append("")
    null_pct = (null_title_count / total_ann * 100) if total_ann > 0 else 0.0
    non_null_count = total_ann - null_title_count
    non_null_pct = (non_null_count / total_ann * 100) if total_ann > 0 else 0.0
    
    lines.append("| Title State | Count | Percentage |")
    lines.append("| :--- | :---: | :---: |")
    lines.append(f"| **Null or Empty Title** (`\"\"` or `null`) | {null_title_count:,} | {null_pct:.2f}% |")
    lines.append(f"| **Non-Null Title** | {non_null_count:,} | {non_null_pct:.2f}% |")
    lines.append(f"| **Total** | **{total_ann:,}** | **100.00%** |")
    lines.append("")
    
    lines.append("### Annotation Levels")
    lines.append("")
    lines.append("| Annotation Level | Count | Percentage |")
    lines.append("| :--- | :---: | :---: |")
    for lvl, cnt in level_counter.most_common():
        pct = (cnt / total_ann * 100) if total_ann > 0 else 0.0
        lines.append(f"| `{lvl}` | {cnt:,} | {pct:.2f}% |")
    lines.append("")
    
    # Section 4: Path Classification
    lines.append("## 4. Annotation Path Classification")
    lines.append("")
    lines.append("| Path Category | Count | Percentage | Description |")
    lines.append("| :--- | :---: | :---: | :--- |")
    
    path_order = [
        ("source file (.java/.py)", "Production source files (e.g. `src/main/java/...`, `.py`)"),
        ("test-path source file", "Test files containing `/test/`, `test_`, or `Test.java`"),
        ("workflow/config (.github, .yml, .md)", "CI workflows, markdown templates, build scripts"),
        ("dotted_fqn", "Dotted class identifier without directory slashes (e.g. ArchUnit check)"),
        ("null/empty", "Missing or empty path attribute"),
        ("other", "Build artifacts, non-code resources, or miscellaneous paths"),
    ]
    
    for cat_name, desc in path_order:
        cnt = path_counter[cat_name]
        pct = (cnt / total_ann * 100) if total_ann > 0 else 0.0
        lines.append(f"| **{cat_name}** | {cnt:,} | {pct:.2f}% | {desc} |")
    lines.append(f"| **Total** | **{total_ann:,}** | **100.00%** | |")
    lines.append("")
    
    # Section 5: Non-Null Title Parsing: Identifiers vs Prose
    lines.append("## 5. Non-Null Title Parsing: Plausible Identifiers vs Prose")
    lines.append("")
    n_ident = len(plausible_identifiers)
    n_prose = len(prose_titles)
    ident_pct = (n_ident / non_null_count * 100) if non_null_count > 0 else 0.0
    prose_pct = (n_prose / non_null_count * 100) if non_null_count > 0 else 0.0
    
    lines.append(f"- **Plausible Test Identifier (`^[\\w.$]+(#|::)[\\w$]+`):** {n_ident:,} ({ident_pct:.2f}% of non-null titles; {n_ident/total_ann*100:.2f}% of all annotations)")
    lines.append(f"- **English Prose / Sentence / Freeform:** {n_prose:,} ({prose_pct:.2f}% of non-null titles; {n_prose/total_ann*100:.2f}% of all annotations)")
    lines.append("")
    
    lines.append("### Real Examples of Plausible Identifier Titles (up to 20):")
    if plausible_identifiers:
        for idx, (repo, t, p) in enumerate(plausible_identifiers[:20], 1):
            lines.append(f"{idx}. `[{repo}]` `{t}` (Path: `{p}`)")
    else:
        lines.append("*(No titles matched the strict `^[\\w.$]+(#|::)[\\w$]+` identifier pattern)*")
    lines.append("")
    
    lines.append("### Real Examples of Prose / Freeform Titles (20 samples):")
    if prose_titles:
        # Sample deterministically across prose titles
        step = max(1, len(prose_titles) // 20)
        sample_prose = [prose_titles[i] for i in range(0, min(len(prose_titles), step * 20), step)][:20]
        for idx, (repo, t, p) in enumerate(sample_prose, 1):
            lines.append(f"{idx}. `[{repo}]` \"{t}\" (Path: `{p}`)")
    lines.append("")
    
    # Section 6: Cross-Tabulation & Usable Test ID Yield
    lines.append("## 6. Cross-Tabulation: Usable Test-ID Candidate Yield")
    lines.append("")
    lines.append("An annotation is a candidate for extracting a test identifier if and only if:")
    lines.append("1. **Path is a test file** (`test-path source file`)")
    lines.append("2. **Title is non-null** (`title != \"\"`)")
    lines.append("")
    lines.append("| Metric | Count | % of All Annotations | % of Non-Empty Annotations |")
    lines.append("| :--- | :---: | :---: | :---: |")
    lines.append(f"| **Total Annotations Measured** | {total_ann:,} | 100.00% | — |")
    lines.append(f"| **Test Path & Non-Null Title (Usable Yield)** | **{cross_tab_count:,}** | **{cross_tab_pct:.2f}%** | **{cross_tab_pct:.2f}%** |")
    lines.append("")
    
    # Section 7: Per-Repository Breakdown of Yield
    lines.append("## 7. Per-Repository Usable Yield Breakdown")
    lines.append("")
    lines.append("| Repository | Sampled Files | Total Annotations | Usable Annotations (Test Path + Non-Null Title) | Yield % |")
    lines.append("| :--- | :---: | :---: | :---: | :---: |")
    for r in sorted(repo_stats.keys()):
        st = repo_stats[r]
        s_files = st["sampled_files"]
        t_ann = st["total_annotations"]
        u_ann = st["test_and_title_annotations"]
        y_pct = (u_ann / t_ann * 100) if t_ann > 0 else 0.0
        lines.append(f"| `{r}` | {s_files:,} | {t_ann:,} | {u_ann:,} | {y_pct:.2f}% |")
    lines.append(f"| **Total** | **{actual_sample_size:,}** | **{total_ann:,}** | **{cross_tab_count:,}** | **{cross_tab_pct:.2f}%** |")
    lines.append("")
    
    # Section 8: Architectural Conclusion
    lines.append("## 8. Census Verdict & Parser Priority Recommendation")
    lines.append("")
    if cross_tab_pct < 5.0:
        lines.append(f"> [!WARNING]")
        lines.append(f"> **Verdict: DEMOTE GitHub Check-Run Annotations.**")
        lines.append(f"> In an unbiased stratified sample of {actual_sample_size:,} files across {total_repos_with_annotations} repositories, **{null_pct:.2f}%** of annotations have a null/empty title, and only **{cross_tab_count:,} / {total_ann:,} ({cross_tab_pct:.2f}%)** annotations meet the minimum criteria of possessing both a test-path file and a non-null title. Furthermore, exactly **{n_ident} / {total_ann} ({n_ident/total_ann*100:.2f}%)** annotations match a canonical method identifier format (`#` or `::`). Annotations are overwhelmingly compiler warnings, linter messages, and CI infrastructure failures. Per §5.5, check-run annotations **must be demoted** from primary ground-truth to a secondary/fallback tier; Maven Surefire XML and build console logs must serve as the primary label source.")
    else:
        lines.append(f"> **Verdict: Retain Annotations.** Usable yield is {cross_tab_pct:.2f}%.")
    lines.append("")
    
    report_text = "\n".join(lines)
    
    # Write output to paper/generated/annotation_census.md
    out_path = Path("paper/generated/annotation_census.md")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report_text, encoding="utf-8")
    
    return report_text


def main() -> None:
    report = run_census()
    print(report)
    print(f"[stdout only] census took {RUNTIME_S:.2f}s")


if __name__ == "__main__":
    main()
