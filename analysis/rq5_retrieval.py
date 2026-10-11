"""RQ5 (exploratory, not pre-registered): is the change-aware gain just better retrieval?

    uv run --extra ml --extra rag python -m analysis.rq5_retrieval        (offline; `make rag-eval`)

No LLM. Compares, on all 70 seeded tasks x {standard, hard}, whether the ground-truth function is among the
top 3 chunks for five retrieval modes:

    L1  BM25 over every function              (= arm R1's retrieval)
    L2  dense over every function
    L3  hybrid (RRF k = 60) over every function
    L4  BM25 over the functions the diff touches, E1 tie-break  (= arm R2's retrieval)
    L5  hybrid over the functions the diff touches

L1 and L4 are `repair.select_chunks` itself, with the cut at 3 lifted to read the rank of the ground truth, so
they are the retrievers of R1 / R2 and not re-implementations. The sparse side of L3 / L5 uses the same
tokens and the same `bm25_scores`. Output: `paper/generated/rq5_retrieval.md`. NOT part of `make tables`.
"""

from __future__ import annotations

import json
import math
import os
import sys
from contextlib import contextmanager
from pathlib import Path

import numpy as np

import analysis.rq4_repair as rq4
from analysis import paper_md
from src.agents import repair
from src.agents.repair import FailureReport, changed_line_ranges, query_tokens
from src.eval.seeded.build import SEEDED, source_files
from src.eval.seeded.validate import head_state
from src.features.online import diff_stats
from src.rag.chunks import chunk_repo
from src.rag.context import query_text
from src.rag.index import Embedder, FastEmbedder, from_chunks, rrf
from src.rag.knowledge import INTERIM, Knowledge, load_failure_docs

RESULT_MD = "rq5_retrieval.md"
LOCALIZATION = ("L1", "L2", "L3", "L4", "L5")
LABELS = {
    "L1": "L1 BM25, whole repo (= R1)",
    "L2": "L2 dense, whole repo",
    "L3": "L3 hybrid (RRF), whole repo",
    "L4": "L4 BM25, functions touched by the diff (= R2)",
    "L5": "L5 hybrid (RRF), functions touched by the diff",
}
HEADER_NOTE = ("**Exploratory, not pre-registered; produced by `make rag-eval`, not `make tables`.** "
               "The pre-registered E3 analysis (`docs/phase/033-e3-preregistration.md`) is unchanged. "
               "No LLM is involved: retrieval only. Dense vectors: `jinaai/jina-embeddings-v2-base-code` "
               "(pinned snapshot, CPU, D-61).")


@contextmanager
def full_ranking():
    """Lift `select_chunks`' cut at three chunks so the rank of the ground truth can be read (order unchanged)."""
    old = repair.MAX_CHUNKS
    repair.MAX_CHUNKS = 10 ** 9
    try:
        yield
    finally:
        repair.MAX_CHUNKS = old


def ranks_for(task: dict, repo: Path, srcs: list[str], embedder: Embedder) -> dict[str, list[tuple[str, str]]]:
    """For each mode, the full ranking as `(file, qualname)` pairs, best first. Needs the PR applied to `repo`."""
    changed, n_lines = diff_stats(task["pr_diff"])
    report = FailureReport(failing=task["failing_tests"], pr_diff=task["pr_diff"], triage="mine",
                           changed_files=list(changed))
    tie = rq4.e1_priority(repo, changed, n_lines)
    out: dict[str, list[tuple[str, str]]] = {}
    with full_ranking():
        out["L1"] = [(c.file, c.qualname) for c in repair.select_chunks("R1", repo, srcs, report)]
        out["L4"] = [(c.file, c.qualname) for c in repair.select_chunks("R2", repo, srcs, report, tie)]
    chunks = chunk_repo(repo, None, srcs)
    idx = from_chunks(chunks, embedder)
    touched_lines = changed_line_ranges(task["pr_diff"])
    touched = {c.ukey for c in chunks if any(c.start <= ln <= c.end for ln in touched_lines.get(c.file, []))}
    restrict = touched or None          # the same fallback as R2: no touched function -> the whole repo
    q, toks = query_text(task["failing_tests"]), query_tokens(task["failing_tests"])
    n = len(chunks)
    out["L2"] = [c.key for c in idx.search(q, n, "dense")]
    out["L3"] = [c.key for c in idx.search(q, n, "hybrid", tokens=toks)]
    out["L5"] = [c.key for c in idx.search(q, n, "hybrid", restrict_to=restrict, tokens=toks)]
    return out


def score_task(task: dict, rankings: dict[str, list[tuple[str, str]]]) -> dict:
    """Per-mode hit@1, hit@3, reciprocal rank and distractor count among the top 3."""
    gt = (task["gt_file"], task["gt_function"])
    hard = {(d["file"], d["function"]) for d in task.get("hard_distractors", [])}
    rec: dict = {"task_id": task["task_id"], "repo": task["repo"], "operator": task["operator"]}
    for mode, ranked in rankings.items():
        pos = ranked.index(gt) + 1 if gt in ranked else 0
        top = ranked[:3]
        rec[mode] = {"hit1": pos == 1, "hit3": 1 <= pos <= 3, "rr": 1.0 / pos if pos else 0.0,
                     "distractor": sum(1 for f, q in top if f in task["distractor_files"] or (f, q) in hard),
                     "n": len(top)}
    return rec


def localization(variant: str, embedder: Embedder, pins: dict) -> list[dict]:
    """Score every task of a variant (the PR is applied to the seeded repo for the duration of each task)."""
    recs = []
    for t in rq4.load_variant(variant):
        repo = SEEDED / "repos" / t["repo"]
        if not repo.exists():
            raise SystemExit(f"{repo} is missing: run `make seeded` first")
        with head_state(repo, t["pr_diff"]):
            srcs = source_files(repo, {"src_dirs": pins[t["repo"]]["src_dirs"]})
            recs.append(score_task(t, ranks_for(t, repo, srcs, embedder)))
    return recs


def mode_table(recs: list[dict]) -> str:
    """hit@1, hit@3, MRR, distractor share per mode."""
    n = len(recs)
    rows = []
    for m in LOCALIZATION:
        top = sum(r[m]["n"] for r in recs)
        rows.append([LABELS[m], paper_md.rate(sum(r[m]["hit1"] for r in recs), n),
                     paper_md.rate(sum(r[m]["hit3"] for r in recs), n),
                     f"{sum(r[m]['rr'] for r in recs) / n:.3f}" if n else "n/a",
                     paper_md.rate(sum(r[m]["distractor"] for r in recs), top)])
    return paper_md.table(["mode", "hit@1", "hit@3", "MRR", "top-3 chunks that are distractors"], rows)


def paired_tests(by_variant: dict[str, list[dict]]) -> tuple[str, dict]:
    """McNemar on hit@3, L3 vs L1 and L5 vs L4, per variant, Holm-adjusted over all of them."""
    from src.eval import stats as S

    tests = []
    for v, recs in by_variant.items():
        for a, b in (("L3", "L1"), ("L5", "L4")):
            only_a = sum(1 for r in recs if r[a]["hit3"] and not r[b]["hit3"])
            only_b = sum(1 for r in recs if r[b]["hit3"] and not r[a]["hit3"])
            tests.append((v, a, b, only_a, only_b, rq4.mcnemar_twosided(only_a, only_b)))
    adj = S.holm_adjust([t[-1] for t in tests])
    rows = [[v, f"{a} vs {b}", oa, ob, f"{p:.4g}", f"{h:.4g}"] for (v, a, b, oa, ob, p), h in zip(tests, adj)]
    text = paper_md.table(["variant", "comparison (hit@3)", "first only", "second only", "p (exact, two-sided)",
                           f"Holm-adjusted (family of {len(tests)})"], rows)
    return text, {(t[0], t[1], t[2]): (t[3], t[4], h) for t, h in zip(tests, adj)}


def gap_sentence(variant: str, recs: list[dict]) -> str:
    """Plain-language reading of how much of the L1 -> L4 gap smarter retrieval (L3) closes."""
    n = len(recs)
    h = {m: sum(r[m]["hit3"] for r in recs) for m in LOCALIZATION}
    gap = h["L4"] - h["L1"]
    if gap <= 0:
        return (f"{variant}: change-aware BM25 (L4, {h['L4']}/{n}) does not beat whole-repo BM25 (L1, {h['L1']}/{n}) "
                "on hit@3, so there is no gap for smarter retrieval to close.")
    d3 = h["L3"] - h["L1"]
    head = (f"{variant}: hit@3 is {h['L1']}/{n} for whole-repo BM25 (L1), {h['L3']}/{n} for whole-repo hybrid (L3, no "
            f"knowledge of the change) and {h['L4']}/{n} for change-aware BM25 (L4). ")
    if d3 <= 0:
        mid = (f"Smarter retrieval alone does not close the gap: L3 is {-d3} task(s) below L1, while knowing the change "
               f"(L4) is {gap} above it. ")
    else:
        closed = d3 / gap
        mid = (f"Smarter retrieval alone closes {'most' if closed >= 0.5 else 'less than half'} of the gap: L3 recovers "
               f"{d3} of the {gap} tasks that L4 recovers over L1 ({closed:.0%}). ")
    return head + mid + f"Change-aware hybrid (L5) reaches {h['L5']}/{n}."


def localization_section(by_variant: dict[str, list[dict]]) -> str:
    text = ("\n## Localization: is the seeded function among the top 3 chunks? (no model, 70 tasks per variant)\n\n"
            "On the standard variant the seeded edit lies inside the diff that L4 / L5 search, so their advantage is "
            "partly by construction; the hard variant (4-6 no-op edits inside executed functions) measures how much "
            "remains. Ties in L1 / L4 are broken exactly as in E3; ties in L2 / L3 / L5 by file path then line.\n")
    for v, recs in by_variant.items():
        text += f"\n### {v.capitalize()} variant (n = {len(recs)})\n\n" + mode_table(recs)
    tests, _ = paired_tests(by_variant)
    text += ("\n### Paired tests\n\n\"first only\" = the first-named mode has the ground truth in its top 3 where the "
             "second does not. Exact McNemar, two-sided, Holm-adjusted over the four tests below.\n\n" + tests)
    text += "\n### Reading\n\n" + "\n\n".join(gap_sentence(v, r) for v, r in by_variant.items()) + "\n"
    return text


# ---- failure-history retrieval (the Ask source "BR-Bench failure history") -------------------------
HISTORY_MODES = ("bm25", "dense", "hybrid")
HISTORY_LABELS = {"bm25": "BM25", "dense": "dense", "hybrid": "hybrid (RRF)"}


def failure_history_queries(interim: Path = INTERIM):
    """`(queries, docs)`: head failures of the E2 chronological test split, and every failure with a message.

    Queries are the (run, test) failures of runs in the E2 test split (D-57: runs ordered by
    `(run_started_at, run_id)`, last 20%) that carry a parsed failure message; documents are every failure
    with a message in any run, each as its message only (a pure message-to-message retrieval).
    """
    from analysis.failure_class import classify
    from analysis.rq3_triage import load_labels, split_runs

    labels = load_labels()
    split = split_runs(labels)
    test_runs = {r for r, s in split.items() if s == "test"}
    docs = load_failure_docs(interim, with_labels=False)
    for d in docs:
        d.text = d.meta["message"]
        d.meta["fclass"] = classify(d.meta["message"])[0]
    queries = [d for d in docs if d.meta["run_id"] in test_runs]
    return queries, docs


def failure_history(embedder: Embedder, interim: Path = INTERIM) -> dict:
    """Retrieve past failures strictly before each test-split failure; hit@1, hit@5, MRR for two notions of "same".

    Per query the pool is the documents of the same repository with a run time strictly earlier than the query's.
    Targets: a past failure of the same `test_id`; a past failure of the same failure class (`analysis.failure_class`).
    A query is eligible for a target only if the pool contains at least one such document.
    """
    queries, docs = failure_history_queries(interim)
    kb = Knowledge(docs, embedder)
    idx = kb.index
    key_pos = {d.key: i for i, d in enumerate(kb.docs)}
    out: dict = {"n_queries": len(queries), "n_docs": len(docs), "targets": {}}
    ranks: dict[str, dict[str, list[int]]] = {t: {m: [] for m in HISTORY_MODES} for t in ("test", "class")}
    chance: dict[str, list[tuple[int, int]]] = {"test": [], "class": []}
    for q in queries:
        pool = [i for i, d in enumerate(kb.docs) if d.ts is not None and d.ts < q.ts and d.meta["repo"] == q.meta["repo"]]
        assert all(kb.docs[i].ts < q.ts for i in pool)       # time safety, by construction and checked
        if not pool:
            continue
        text = q.meta["message"]
        sparse = idx.sparse_ranking(_tokens(text), pool)
        dense = idx.dense_ranking(text, pool)
        fused = rrf([[i for i, _ in sparse], [i for i, _ in dense]])
        hyb = sorted(fused, key=lambda i: (-round(fused[i], 12), kb.docs[i].file, kb.docs[i].qualname))
        order = {"bm25": [i for i, _ in sparse], "dense": [i for i, _ in dense], "hybrid": hyb}
        for target, same in (("test", lambda d: d.meta["test_id"] == q.meta["test_id"]),
                             ("class", lambda d: d.meta["fclass"] == q.meta["fclass"])):
            pos = {i for i in pool if same(kb.docs[i])}
            if not pos:
                continue
            chance[target].append((len(pos), len(pool)))
            for m in HISTORY_MODES:
                assert all(kb.docs[i].ts < q.ts for i in order[m])   # nothing at or after the query time is retrieved
                first = next((r for r, i in enumerate(order[m], 1) if i in pos), 0)
                ranks[target][m].append(first)
    for target in ("test", "class"):
        n = len(chance[target])
        row: dict = {"eligible": n, "modes": {}}
        for m in HISTORY_MODES:
            r = ranks[target][m]
            row["modes"][m] = {"hit1": sum(1 for x in r if x == 1), "hit5": sum(1 for x in r if 1 <= x <= 5),
                               "mrr": (sum(1.0 / x for x in r if x) / n) if n else float("nan")}
        row["chance_hit1"] = sum(p / m for p, m in chance[target]) / n if n else float("nan")
        row["chance_hit5"] = (sum(1 - math.comb(m - p, min(5, m)) / math.comb(m, min(5, m)) for p, m in chance[target]) / n
                              if n else float("nan"))
        out["targets"][target] = row
    return out


def _tokens(text: str) -> list[str]:
    return query_tokens([{"test_id": "", "output": text}], output_chars=len(text))


def failure_history_section(res: dict) -> str:
    text = ("\n## Failure-history retrieval (the \"Ask\" failure source; no model, time-safe)\n\n"
            f"Queries: the {res['n_queries']:,} failures with a parsed message among the runs of the E2 chronological test "
            "split (D-57). For each, documents are the failures with a message in the same repository whose run started "
            "strictly earlier (a test asserts none at or after the query time is ever retrieved). Documents are message "
            "text only. \"Same test\" = a past failure of the same `test_id`; \"same class\" = a past failure of the "
            "same failure class (environment / timeout / code / unknown, `analysis/failure_class.py`). A query counts only "
            "when such a document exists in its pool (n eligible). Chance rows are the expected hit@1 and hit@5 of a "
            "random order over the same pools.\n")
    for target, label in (("test", "Retrieved a past failure of the same test_id"),
                          ("class", "Retrieved a past failure of the same failure class")):
        row = res["targets"][target]
        n = row["eligible"]
        rows = [[HISTORY_LABELS[m], paper_md.rate(row["modes"][m]["hit1"], n), paper_md.rate(row["modes"][m]["hit5"], n),
                 f"{row['modes'][m]['mrr']:.3f}" if n else "n/a"] for m in HISTORY_MODES]
        rows.append(["chance (random order)", f"{row['chance_hit1']:.2%}" if n else "n/a",
                     f"{row['chance_hit5']:.2%}" if n else "n/a", "-"])
        text += f"\n### {label} (n eligible = {n:,})\n\n" + paper_md.table(["retriever", "hit@1", "hit@5", "MRR"], rows)
    return text


def main(argv: list[str] | None = None) -> int:
    os.environ.setdefault("BR_OFFLINE", "1")
    pins = json.loads(rq4.REPOS_JSON.read_text())
    embedder = FastEmbedder()
    by_variant: dict[str, list[dict]] = {}
    for v in ("standard", "hard"):
        try:
            by_variant[v] = localization(v, embedder, pins)
        except FileNotFoundError:
            continue
    text = paper_md.header("RQ5 (exploratory): sparse vs dense vs hybrid vs change-aware retrieval",
                           "analysis/rq5_retrieval.py", HEADER_NOTE)
    text += localization_section(by_variant)
    if (INTERIM / "parsed_outcomes.parquet").exists():
        text += failure_history_section(failure_history(embedder))
    else:
        text += "\n## Failure-history retrieval\n\nNot computed: `data/interim` is not present on this machine.\n"
    from analysis.ask_eval import section_from_answers

    text += section_from_answers()
    paper_md.write(RESULT_MD, text)
    print(f"wrote paper/generated/{RESULT_MD}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
