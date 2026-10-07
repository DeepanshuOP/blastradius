"""Environment-failure audit of the strict labels. Measurement only: no label changes.

Each strict label `(run_id, test_id)` is classified from the failure messages of
its parsed outcome rows (one row per job in a matrix) using
`analysis/failure_class.py`. Per-label rule, applied over the label's rows:
code-level if ANY row is code-level (the test demonstrably failed on code),
else environment-strict if any row is, else timeout if any row is, else unknown.
Timeouts are reported apart from the strict environment class: a timeout is a
symptom that a change can cause. "Unknown" is split
into `no message recorded` and `message matched no pattern`; the former is the
majority of labels and bounds what this audit can see.

Writes `paper/generated/infra_failures.md`: patterns used, counts and rates for
labels and instances, an RQ1 sensitivity table (environment-strict removed;
environment-strict plus timeout removed), and sampled messages for hand review.
"""

from __future__ import annotations

import random

import pandas as pd

from analysis import paper_md
from analysis.failure_class import CODE, ENVIRONMENT, TIMEOUT, UNKNOWN, classify, pattern_listing
from analysis.rq1_divergence import K_VALS, METHODS, evaluate_k, ground_truth, load_data

SAMPLE_SEED = 20261110  # the project's sampling seed (attrition_funnel footnote 2)
SAMPLE_SIZE = 10
MESSAGE_CHARS = 200
_PRECEDENCE = {CODE: 0, ENVIRONMENT: 1, TIMEOUT: 2, UNKNOWN: 3}
CLASSES = (CODE, ENVIRONMENT, TIMEOUT, UNKNOWN)
NAME = {CODE: "code-level", ENVIRONMENT: "environment-strict", TIMEOUT: "timeout", UNKNOWN: "unknown"}


def classify_labels(strict: pd.DataFrame, parsed: pd.DataFrame) -> pd.DataFrame:
    """One row per strict label with its class, deciding rule and a message.

    Args:
        strict: Strict `outcomes` rows (run_id, test_id).
        parsed: `parsed_outcomes` rows (run_id, test_id, job_id, failure_message).

    Returns:
        Columns run_id, test_id, cls, rule, message (the deciding row's message;
        empty when none was recorded), sorted by (run_id, test_id).
    """
    rows = parsed.merge(strict[["run_id", "test_id"]].drop_duplicates(), on=["run_id", "test_id"])
    rows = rows.sort_values(["run_id", "test_id", "job_id"])
    best: dict[tuple[int, str], tuple[int, str, str, str]] = {}
    for r in rows.itertuples():
        msg = r.failure_message if isinstance(r.failure_message, str) else ""
        cls, rule = classify(msg)
        if cls == UNKNOWN and msg:
            rule = "message matched no pattern"
        elif cls == UNKNOWN:
            rule = "no message recorded"
        key = (int(r.run_id), r.test_id)
        cand = (_PRECEDENCE[cls], cls, rule, msg)
        if key not in best or cand[0] < best[key][0]:
            best[key] = cand
    out = pd.DataFrame(
        [{"run_id": k[0], "test_id": k[1], "cls": v[1], "rule": v[2], "message": v[3]}
         for k, v in best.items()]
    )
    missing = strict[["run_id", "test_id"]].drop_duplicates().merge(
        out[["run_id", "test_id"]], how="left", indicator=True)
    missing = missing[missing["_merge"] == "left_only"].drop(columns="_merge")
    if len(missing):  # a strict label with no parsed row at all: no evidence
        missing = missing.assign(cls=UNKNOWN, rule="no message recorded", message="")
        out = pd.concat([out, missing], ignore_index=True)
    return out.sort_values(["run_id", "test_id"]).reset_index(drop=True)


def instance_table(labels: pd.DataFrame) -> list[list]:
    """Instance-level rates from the labelled strict labels."""
    n = labels["run_id"].nunique()
    per = labels.groupby("run_id")["cls"]
    any_env = int((per.apply(lambda s: (s == ENVIRONMENT).any())).sum())
    all_env = int((per.apply(lambda s: (s == ENVIRONMENT).all())).sum())
    any_to = int((per.apply(lambda s: (s == TIMEOUT).any())).sum())
    all_envto = int((per.apply(lambda s: s.isin([ENVIRONMENT, TIMEOUT]).all())).sum())
    any_code = int((per.apply(lambda s: (s == CODE).any())).sum())
    none_code_or_env = int((per.apply(lambda s: (s == UNKNOWN).all())).sum())
    return [
        ["instances with >= 1 environment-strict label", paper_md.rate(any_env, n)],
        ["instances whose labels are ALL environment-strict", paper_md.rate(all_env, n)],
        ["instances with >= 1 timeout label", paper_md.rate(any_to, n)],
        ["instances whose labels are ALL environment-strict or timeout", paper_md.rate(all_envto, n)],
        ["instances with >= 1 code-level label", paper_md.rate(any_code, n)],
        ["instances whose labels are ALL unknown", paper_md.rate(none_code_or_env, n)],
    ]


def sensitivity(data, exclude: set) -> list[list]:
    """RQ1 rows with and without environment-strict, and environment-strict plus timeout, labels.

    Args:
        data: Loaded RQ1 inputs.
        exclude: `{"environment-strict": labels, "environment-strict + timeout": labels}`.

    Returns:
        One row per (k, variant, method).
    """
    rows = []
    variants = (("all strict labels", set()),) + tuple((f"{name} removed", ex) for name, ex in exclude.items())
    for k in K_VALS:
        for name, ex in variants:
            df = evaluate_k(data, ground_truth(data, ex), k)
            for key, label in METHODS:
                rows.append([k, name, label, len(df), f"{df[f'{key}_p'].mean():.3f}",
                             f"{df[f'{key}_r'].mean():.3f}", f"{df[f'{key}_j'].mean():.3f}"])
    return rows


def main() -> None:
    outcomes = pd.read_parquet("data/interim/outcomes.parquet")
    parsed = pd.read_parquet("data/interim/parsed_outcomes.parquet")
    instances = pd.read_parquet("data/interim/instances_raw.parquet")
    strict = outcomes[outcomes["split"] == "strict"]
    labels = classify_labels(strict, parsed)
    n = len(labels)
    n_inst = labels["run_id"].nunique()

    text = paper_md.header(
        "Environment-failure audit of the strict labels", "analysis/infra_failure_audit.py",
        "Measurement only: no label is changed or removed from `outcomes.parquet`. The classification "
        "is regex-based on the parsed failure message and is a lower bound on environment failures "
        "wherever the message is empty.")
    text += "\n## Patterns used (decision order)\n\n" + "\n".join(f"- {p}" for p in pattern_listing()) + "\n"
    text += ("\nPer-label rule: code-level if any of the label's rows is code-level, else environment "
             "if any is, else unknown.\n")

    text += "\n## Strict labels by class\n\n"
    rows = [[NAME[c], paper_md.rate(int((labels["cls"] == c).sum()), n)] for c in CLASSES]
    text += paper_md.table(["class", "labels"], rows)
    unk = labels[labels["cls"] == UNKNOWN]
    text += "\n### By deciding rule\n\n" + paper_md.table(
        ["class", "rule", "labels"],
        [[NAME[c], r, paper_md.rate(int(((labels["cls"] == c) & (labels["rule"] == r)).sum()), n)]
         for (c, r) in sorted(labels[["cls", "rule"]].drop_duplicates().itertuples(index=False, name=None))])
    text += (f"\nUnknown splits into {paper_md.rate(int((unk['rule'] == 'no message recorded').sum()), n)} "
             f"with no message recorded and {paper_md.rate(int((unk['rule'] == 'message matched no pattern').sum()), n)} "
             "with a message that matched no pattern.\n")

    text += "\n## Strict instances\n\n" + paper_md.table(
        ["measure", f"instances (of {n_inst:,} strict)"], instance_table(labels))

    lang = instances.drop_duplicates("run_id").set_index("run_id")["language"]
    labels["language"] = labels["run_id"].map(lang)
    rows = []
    for lg in sorted(labels["language"].dropna().unique()):
        sub = labels[labels["language"] == lg]
        rows.append([lg] + [paper_md.rate(int((sub["cls"] == c).sum()), len(sub)) for c in CLASSES])
    text += "\n## Labels by language\n\n" + paper_md.table(["language"] + [NAME[c] for c in CLASSES], rows)

    env = labels[labels["cls"] == ENVIRONMENT]
    tmo = labels[labels["cls"] == TIMEOUT]

    def keys(frame: pd.DataFrame) -> set:
        return set(zip(frame["run_id"].astype(int), frame["test_id"]))

    exclude = {"environment-strict": keys(env), "environment-strict + timeout": keys(env) | keys(tmo)}
    data = load_data()
    text += ("\n## RQ1 sensitivity: labels removed\n\n"
             + "; ".join(f"{name}: {len(ex):,} labels" for name, ex in exclude.items())
             + ". An instance whose ground truth becomes empty leaves the evaluation (n falls). "
             "Mean P/R/J over n instances, as in `rq1.md`.\n\n")
    text += paper_md.table(["k", "labels", "method", "n", "mean P", "mean R", "mean J"],
                           sensitivity(data, exclude))

    for title, pool, note in (("environment-strict", env, "each should be a failure that is not the change's fault"),
                              ("timeout", tmo, "each may still be a real hang the change caused")):
        pool = pool.sort_values(["run_id", "test_id"]).reset_index(drop=True)
        picks = random.Random(SAMPLE_SEED).sample(range(len(pool)), min(SAMPLE_SIZE, len(pool)))
        text += (f"\n## {len(picks)} sampled {title} messages (seed {SAMPLE_SEED}, truncated to {MESSAGE_CHARS} chars)\n\n"
                 f"For hand review: {note}.\n\n")
        for i in sorted(picks):
            r = pool.iloc[i]
            msg = r["message"][:MESSAGE_CHARS].replace("\n", " ").replace("|", "\\|")
            text += f"- run {r['run_id']}, `{r['test_id']}`, rule `{r['rule']}`: `{msg}`\n"

    path = paper_md.write("infra_failures.md", text)
    print(f"Wrote {path}: {paper_md.rate(len(env), n)} environment-strict, {paper_md.rate(len(tmo), n)} timeout, "
          f"{paper_md.rate(int((labels['cls'] == CODE).sum()), n)} code-level strict labels")


if __name__ == "__main__":
    main()
