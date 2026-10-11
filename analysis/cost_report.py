"""Token and dollar cost of E3 repair, the PR bot and Ask: `paper/generated/cost_report.md` and `.json`.

Offline and deterministic; reads only files already on disk:

  - `paper/generated/e3_usage.json`, written by `make repair-eval` from the replayed E3 caches (per model, variant
    and arm: tasks, plausible fixes, summed prompt and completion tokens);
  - `eval/llm_cache/usage.jsonl`, the client-side ledger (every live call; Bedrock rows carry `usd`);
  - `eval/llm_cache/bot_*.jsonl` and `ask_*.jsonl`, the recorded PR-bot and Ask runs.

Dollars at list price are what the recorded tokens would have cost on Groq's paid plan; the amount actually paid
is read from the ledger (Groq free tier rows carry no `usd`). NOT part of `make tables`; run by `make e3-sync`.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from analysis import paper_md

E3_USAGE = Path("paper/generated/e3_usage.json")
LEDGER = Path("eval/llm_cache/usage.jsonl")
CACHE_DIR = Path("eval/llm_cache")
OUT_JSON = Path("paper/generated/cost_report.json")

PRICES_DATE = "2026-10-11"
PRICES_URL = "https://groq.com/pricing"
#: USD per million tokens (input, output), Groq paid list prices as of PRICES_DATE.
GROQ_LIST_PRICES: dict[str, tuple[float, float]] = {
    "openai/gpt-oss-120b": (0.15, 0.60),
    "openai/gpt-oss-20b": (0.075, 0.30),
}
CHATREPAIR_CONTEXT = ("ChatRepair reported $0.42 per fixed bug (ChatGPT, Defects4J, 2024). "
                      "Different bugs and model; context only.")


def usd_at_list(model: str, prompt: int, completion: int) -> float | None:
    """USD at the Groq list price, or None when the model has no listed price here."""
    if model not in GROQ_LIST_PRICES:
        return None
    pin, pout = GROQ_LIST_PRICES[model]
    return prompt * pin / 1e6 + completion * pout / 1e6


def _div(a: float | None, b: int) -> float | None:
    return None if a is None or not b else a / b


def e3_rows(usage: dict) -> list[dict]:
    """One row per model and arm of the standard variant."""
    rows: list[dict] = []
    for key in sorted(usage):
        u = usage[key]
        if u["variant"] != "standard":
            continue
        for arm, a in sorted(u["arms"].items()):
            usd = usd_at_list(u["model"], a["prompt_tokens"], a["completion_tokens"])
            rows.append({
                "model": u["model"], "variant": u["variant"], "arm": arm, "n": a["n"], "accepted": a["accepted"],
                "calls": a["calls"], "prompt_tokens": a["prompt_tokens"], "completion_tokens": a["completion_tokens"],
                "in_per_task": _div(a["prompt_tokens"], a["n"]), "out_per_task": _div(a["completion_tokens"], a["n"]),
                "in_per_fix": _div(a["prompt_tokens"], a["accepted"]), "out_per_fix": _div(a["completion_tokens"], a["accepted"]),
                "usd_list_total": usd, "usd_list_per_task": _div(usd, a["n"]), "usd_list_per_fix": _div(usd, a["accepted"])})
    return rows


def recorded_runs(prefix: str) -> list[dict]:
    """Per model: calls and summed tokens in the `<prefix>_*.jsonl` caches."""
    out = []
    for path in sorted(CACHE_DIR.glob(f"{prefix}_*.jsonl")):
        recs = [json.loads(ln) for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
        if not recs:
            continue
        model = recs[0]["model"]
        pt = sum(int((r.get("usage") or {}).get("prompt_tokens", 0)) for r in recs)
        ct = sum(int((r.get("usage") or {}).get("completion_tokens", 0)) for r in recs)
        usd = usd_at_list(model, pt, ct)
        out.append({"model": model, "calls": len(recs), "prompt_tokens": pt, "completion_tokens": ct,
                    "usd_list_total": usd, "usd_list_per_call": _div(usd, len(recs)),
                    "tokens_per_call": (pt + ct) / len(recs), "file": path.name})
    return out


def live_pr_run(path: Path = Path("src/agents/demo/pr1_comment.md")) -> dict | None:
    """Model and total tokens from the footer of the bot's comment on the live PR (no input/output split is recorded)."""
    if not path.exists():
        return None
    m = re.search(r"model `([^`]+)` · ([\d,]+) tokens", path.read_text(encoding="utf-8"))
    return {"model": m.group(1), "tokens": int(m.group(2).replace(",", "")), "file": path.name} if m else None


def ledger_summary(path: Path = LEDGER) -> dict:
    """Calls and tokens per model in the client-side ledger, and the USD actually paid (Bedrock rows only)."""
    by_model: dict[str, dict] = {}
    paid = 0.0
    for ln in path.read_text(encoding="utf-8").splitlines():
        if not ln.strip():
            continue
        r = json.loads(ln)
        m = by_model.setdefault(r["model"], {"calls": 0, "tokens": 0})
        m["calls"] += 1
        m["tokens"] += int(r.get("tokens", 0))
        paid += float(r.get("usd") or 0.0)
    return {"by_model": by_model, "paid_usd": paid}


def build() -> dict:
    """Assemble the whole report as one JSON-able dict."""
    if not E3_USAGE.exists():
        raise SystemExit(f"{E3_USAGE} is missing: run `make repair-eval` first (it writes the per-arm token sums)")
    return {"prices": {"date": PRICES_DATE, "url": PRICES_URL,
                       "usd_per_million_in_out": {m: list(p) for m, p in GROQ_LIST_PRICES.items()}},
            "ledger": ledger_summary(), "e3": e3_rows(json.loads(E3_USAGE.read_text(encoding="utf-8"))),
            "bot": recorded_runs("bot"), "bot_live": live_pr_run(), "ask": recorded_runs("ask"), "context": CHATREPAIR_CONTEXT}


def _n(x: float | None, d: int = 0) -> str:
    return "n/a" if x is None else f"{x:,.{d}f}"


def render(doc: dict) -> str:
    """The markdown report."""
    paid = doc["ledger"]["paid_usd"]
    text = paper_md.header("Cost: tokens and dollars of E3 repair, the PR bot and Ask", "analysis/cost_report.py",
                           "Computed from `paper/generated/e3_usage.json` (written by `make repair-eval`), "
                           "`eval/llm_cache/usage.jsonl` and the recorded bot and Ask caches. Not part of `make tables`.")
    text += (f"\n**USD actually paid: {paid:.2f}** (Groq free tier; the ledger holds no paid rows)." if paid == 0 else
             f"\n**USD actually paid: {paid:.4f}** (sum of paid rows in the ledger).")
    pr = doc["prices"]
    text += ("\n\n**USD at Groq's paid list prices** (constants in `analysis/cost_report.py`, "
             f"{pr['date']}, {pr['url']}): " + "; ".join(f"{m} ${p[0]:.3f} in / ${p[1]:.3f} out per million tokens"
                                                          for m, p in pr["usd_per_million_in_out"].items())
             + ". These are what the same tokens would cost on the paid plan, not money spent.\n")
    rows = [[r["model"], r["arm"], r["n"], r["accepted"], _n(r["in_per_task"]), _n(r["out_per_task"]),
             _n(r["in_per_fix"]), _n(r["out_per_fix"]), _n(r["usd_list_per_task"], 5), _n(r["usd_list_per_fix"], 5)]
            for r in doc["e3"]]
    text += ("\n## E3 repair, standard variant (tokens from the replayed caches)\n\n"
             "Per plausible fix = all tokens the arm spent, divided by the fixes it produced (failed attempts included). "
             "R0 never calls a model. R3 includes its retries.\n\n"
             + paper_md.table(["model", "arm", "tasks", "plausible fixes", "input tok / task", "output tok / task",
                               "input tok / fix", "output tok / fix", "USD at list / task", "USD at list / fix"], rows))
    for title, key in (("PR bot: recorded runs", "bot"), ("Ask: recorded questions", "ask")):
        rr = [[r["model"], r["calls"], f"{r['prompt_tokens']:,}", f"{r['completion_tokens']:,}",
               _n(r["tokens_per_call"]), _n(r["usd_list_per_call"], 5), r["file"]] for r in doc[key]]
        text += (f"\n## {title}\n\n" + paper_md.table(
            ["model", "model calls", "input tokens", "output tokens", "tokens / call", "USD at list / call", "cache file"], rr))
    if doc.get("bot_live"):
        b = doc["bot_live"]
        text += (f"\nLive PR #1 run (`{b['file']}`, footer of the bot's comment): model `{b['model']}`, {b['tokens']:,} tokens in one run; "
                 "the comment records no input/output split, so no dollar figure is computed.\n")
    lr = [[m, v["calls"], f"{v['tokens']:,}"] for m, v in sorted(doc["ledger"]["by_model"].items())]
    text += "\n## Client-side ledger (every live call, all uses)\n\n" + paper_md.table(["model", "calls", "tokens"], lr)
    text += f"\n## Context, not a comparison\n\n{doc['context']}\n"
    return text


def main() -> int:
    doc = build()
    OUT_JSON.write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    paper_md.write("cost_report.md", render(doc))
    print(f"wrote paper/generated/cost_report.md and {OUT_JSON}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
