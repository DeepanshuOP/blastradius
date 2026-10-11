"""Ask BlastRadius: the fixed question set and its citation-faithfulness score (exploratory, D-61).

    uv run --extra ml --extra rag python -m analysis.ask_eval build      write eval/ask/questions.jsonl (deterministic)
    uv run --env-file .env --extra ml --extra rag python -m analysis.ask_eval record   one live run, cached (Groq)
    uv run --extra ml --extra rag python -m analysis.ask_eval report     replay from the cache, score, write answers.json

15 questions, 5 per type, built from real BR-Bench test ids and the seeded repositories:

* test-failure: "Why is <seeded failing test> failing?" with the first line of its recorded output, asked at the
  seeded task's head state (the PR applied), so the buggy function is in the code the assistant can retrieve.
* impact: "What is at risk if I change <seeded source file>?", so the E1 ranker's top-5 block is in the context.
* history: "Has <real BR-Bench test_id> failed before?" over the failure-history source.

Scoring is automatic and says nothing about correctness: the share of answers whose every `[Sk]` points to a real
retrieved item, and the share that cite at least one item. `record` is the only step that calls a model (the
cache is `eval/llm_cache/ask_openai_gpt-oss-20b.jsonl`); `report` replays it with the network forbidden.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from analysis import paper_md
from src.agents.ask import AskAgent, AskResult, score_answers
from src.eval.seeded.build import SEEDED
from src.eval.seeded.validate import head_state

OUT = Path("eval/ask")
QUESTIONS = OUT / "questions.jsonl"
ANSWERS = OUT / "answers.json"
TASKS = Path("eval/seeded/tasks.jsonl")
MODEL = "openai/gpt-oss-20b"
CACHE = Path("eval/llm_cache/ask_openai_gpt-oss-20b.jsonl")
PER_TYPE = 5


def build_questions(interim: Path = Path("data/interim")) -> list[dict]:
    """The fixed question list: deterministic from the seeded tasks and the failure-history table."""
    from src.rag.knowledge import load_failure_docs

    tasks = [json.loads(ln) for ln in TASKS.read_text(encoding="utf-8").splitlines() if ln.strip()]
    qs: list[dict] = []
    # test-failure: one task per repo/operator spread, in task-id order, first failing test with its first output line
    by_repo: dict[str, list[dict]] = {}
    for t in sorted(tasks, key=lambda t: t["task_id"]):
        by_repo.setdefault(t["repo"], []).append(t)
    picks = []
    for repo in sorted(by_repo):
        picks.append(by_repo[repo][0])
    first_ids = {p["failing_tests"][0]["test_id"] for p in picks}
    picks += [next(t for t in reversed(by_repo["shopcart"]) if t["failing_tests"][0]["test_id"] not in first_ids)]
    for t in picks[:PER_TYPE]:
        ft = t["failing_tests"][0]
        first = next((ln.strip() for ln in ft.get("output", "").splitlines() if ln.strip()), "")[:160]
        qs.append({"type": "test-failure", "task_id": t["task_id"], "repo": t["repo"],
                   "question": f"Why is {ft['test_id']} failing? Its output starts: {first}"})
    # impact: the seeded (gt) source file of five tasks in different repos / files
    seen: set[tuple[str, str]] = set()
    for t in sorted(tasks, key=lambda t: t["task_id"]):
        key = (t["repo"], t["gt_file"])
        if key in seen:
            continue
        seen.add(key)
        if len([q for q in qs if q["type"] == "impact"]) < PER_TYPE and t["repo"] in ("shopcart", "itsdangerous", "click",
                                                                                       "markupsafe"):
            n_repo = len([q for q in qs if q["type"] == "impact" and q["repo"] == t["repo"]])
            if n_repo < 2:
                qs.append({"type": "impact", "task_id": t["task_id"], "repo": t["repo"],
                           "question": f"What is at risk if I change {t['gt_file']}?"})
    # history: real test ids that failed with a message at least three times, spread over the sorted list
    docs = load_failure_docs(interim, with_labels=False)
    count: dict[str, int] = {}
    for d in docs:
        count[d.meta["test_id"]] = count.get(d.meta["test_id"], 0) + 1
    cands = sorted(t for t, c in count.items() if c >= 3)
    step = max(1, len(cands) // PER_TYPE)
    for t in cands[::step][:PER_TYPE]:
        qs.append({"type": "history", "task_id": None, "repo": None,
                   "question": f"Has {t} failed before? When and with what message?"})
    for i, q in enumerate(qs, 1):
        q["id"] = f"Q{i:02d}"
    return qs


def load_questions() -> list[dict]:
    return [json.loads(ln) for ln in QUESTIONS.read_text(encoding="utf-8").splitlines() if ln.strip()]


def knowledge_for(q: dict, embedder, failure_docs):
    """The knowledge base for one question (code of the seeded repo at head state, its docs, failure history)."""
    from src.rag.knowledge import Knowledge, code_docs, load_repo_docs

    docs = list(failure_docs)
    if q["repo"]:
        repo = SEEDED / "repos" / q["repo"]
        docs = code_docs(repo) + load_repo_docs(repo) + docs
    return Knowledge(docs, embedder)         # history questions search failure history only (SOURCES_BY_TYPE)


def answer_all(llm, embedder) -> list[tuple[dict, AskResult]]:
    from src.rag.knowledge import load_failure_docs

    failure = load_failure_docs()
    tasks = {t["task_id"]: t for t in (json.loads(ln) for ln in TASKS.read_text(encoding="utf-8").splitlines() if ln.strip())}
    out = []
    for q in load_questions():
        if q["type"] == "test-failure":
            with head_state(SEEDED / "repos" / q["repo"], tasks[q["task_id"]]["pr_diff"]):
                kb = knowledge_for(q, embedder, failure)
                res = AskAgent(kb, SEEDED / "repos" / q["repo"], llm).ask(q["question"])
        else:
            kb = knowledge_for(q, embedder, failure)
            res = AskAgent(kb, SEEDED / "repos" / q["repo"] if q["repo"] else None, llm).ask(q["question"])
        out.append((q, res))
        print(f"{q['id']} [{q['type']}] cited={res.cited} faithful={res.faithful} tokens={res.tokens}", flush=True)
    return out


def write_outputs(pairs: list[tuple[dict, AskResult]]) -> None:
    ANSWERS.parent.mkdir(parents=True, exist_ok=True)
    doc = {"model": MODEL, "questions": [{**q, **r.to_json()} for q, r in pairs]}
    ANSWERS.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def faithfulness_section(pairs: list[tuple[dict, AskResult]]) -> str:
    """Markdown for `rq5_retrieval.md`."""
    text = ("\n## Citation faithfulness of Ask (recorded once with " + MODEL + ", exploratory)\n\n"
            f"{len(pairs)} fixed questions (`eval/ask/questions.jsonl`), answers recorded in "
            f"`{CACHE}`. Scored automatically; this says nothing about whether an answer is correct, only that "
            "its citations point at items the model was actually shown.\n\n")
    rows = []
    for typ in ("test-failure", "impact", "history", "all"):
        rs = [r for q, r in pairs if typ == "all" or q["type"] == typ]
        s = score_answers(rs)
        rows.append([typ, s["answered"], paper_md.rate(s["all_citations_real_or_none"], s["answered"]),
                     paper_md.rate(s["cites_at_least_one"], s["answered"]),
                     paper_md.rate(s["all_citations_real"], s["answered"]), s["abstained"]])
    text += paper_md.table(["question type", "answered", "no [Sk] points outside the retrieved items",
                            "cites at least one item", "both (every citation real, at least one)",
                            "answered \"not in the context\""], rows)
    return text


def section_from_answers(path: Path = ANSWERS) -> str:
    """The faithfulness section from the recorded `answers.json` (no model, no index): what `make rag-eval` includes."""
    from types import SimpleNamespace

    if not path.exists():
        return ("\n## Citation faithfulness of Ask\n\nNot recorded yet: run `python -m analysis.ask_eval record` "
                "(one Groq run with " + MODEL + ", cached).\n")
    doc = json.loads(path.read_text(encoding="utf-8"))
    pairs = [({"type": q["type"]}, SimpleNamespace(answer=q["answer"], faithful=q["faithful"], cited=q["cited"]))
             for q in doc["questions"]]
    return faithfulness_section(pairs)


def main(argv: list[str] | None = None) -> int:
    mode = (argv or sys.argv[1:] or ["report"])[0]
    if mode == "build":
        OUT.mkdir(parents=True, exist_ok=True)
        qs = build_questions()
        QUESTIONS.write_text("\n".join(json.dumps(q, ensure_ascii=False) for q in qs) + "\n", encoding="utf-8")
        print(f"wrote {QUESTIONS} ({len(qs)} questions)")
        return 0
    from src.rag.index import FastEmbedder

    embedder = FastEmbedder()
    if mode == "record":
        from src.agents.llm import GroqLLM
        from src.agents.llm_cache import LLMCache

        key = os.environ.get("GROQ_API_KEY", "")
        if not key:
            raise SystemExit("record needs GROQ_API_KEY (`uv run --env-file .env ...`)")
        llm = GroqLLM(api_key=key, model=MODEL, cache=LLMCache(CACHE))
    else:                                   # report: replay only
        os.environ["BR_LLM_REPLAY"] = "1"
        os.environ["BR_OFFLINE"] = "1"
        from src.agents.llm import GroqLLM
        from src.agents.llm_cache import CacheMiss, LLMCache

        if not CACHE.exists():
            print("no recorded answers yet (eval/llm_cache/ask_*.jsonl): nothing to score")
            return 0
        llm = GroqLLM(api_key="replay", model=MODEL, cache=LLMCache(CACHE, replay=True), ledger=Path(os.devnull))
    pairs = answer_all(llm, embedder)
    write_outputs(pairs)
    print(faithfulness_section(pairs))
    return 0


if __name__ == "__main__":
    sys.exit(main())
