"""Triage Agent: is a failing test mine (caused by this change), inherited, or flaky?

Input is a regression report plus the failure history the Regression agent keeps
(`history/test_outcomes.jsonl`: `ts`, `commit`, `test_id`, `outcome`, optionally `message`
and `branch`). Output is one class per failure, a confidence and a reason.

It uses the E2 LightGBM model (`models/e2_triage_v1.txt`, trained in `analysis/rq3_triage.py` on
BR-Bench) through the same feature definitions as the offline experiment
(`src/features/triage_features.py`). Without the model, or without `lightgbm`, it falls back to
the two rules the experiment compares against: R-branch (failed in any of the previous three
runs of the branch) and R-msg (the failure message was seen in an earlier run).

Honest limits: on BR-Bench the model's recall of not-mine failures is low (see
`paper/generated/rq3_triage.md`), and the live proximity / co-change features are unavailable
online, so they are passed as missing. A `mine` verdict therefore means "no evidence that it was
already failing", which is also what a CI server assumes for everything.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.features.triage_features import (RULE_BRANCH_N, TRIAGE_COLS, TriageHistory, fclass_onehot, message_hash)

MODEL_PATH = Path(__file__).resolve().parents[2] / "models" / "e2_triage_v1.txt"
CLASSES = ("mine", "inherited", "flaky")


@dataclass
class TriagedFailure:
    """One failing test, classified."""

    test_id: str
    klass: str          # mine | inherited | flaky
    confidence: float   # probability of the reported side of the mine / not-mine decision
    reason: str
    route: str          # repair | ignore | rerun


@dataclass
class TriageReport:
    """What the agent hands back."""

    commit: str
    model: str          # e2-lgbm-v1 | rules
    failures: list[TriagedFailure] = field(default_factory=list)

    @property
    def mine(self) -> list[TriagedFailure]:
        """The failures worth repairing."""
        return [f for f in self.failures if f.klass == "mine"]

    def counts(self) -> dict[str, int]:
        """Failures per class."""
        return {c: sum(1 for f in self.failures if f.klass == c) for c in CLASSES}


def _epoch(stamp: str, fallback: int) -> int:
    try:
        dt = datetime.fromisoformat(str(stamp).replace("Z", "+00:00"))
        return int((dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)).timestamp())
    except ValueError:
        return fallback  # e.g. the demo baseline's literal "baseline"


def load_history(path: Path, exclude_commit: str = "") -> tuple[pd.DataFrame, int]:
    """Failure events from `test_outcomes.jsonl` as the frame :class:`TriageHistory` indexes.

    Args:
        path: The jsonl history.
        exclude_commit: Events recorded at this commit are dropped: a failure being triaged is not its own history.

    Returns:
        `(events, now)` where `now` is one second after the newest event (0 for an empty history), so
        every history-derived feature is deterministic for a given file.
    """
    rows, runs = [], {}
    if path.exists():
        for i, line in enumerate(path.read_text(encoding="utf-8").splitlines()):
            if not line.strip():
                continue
            r = json.loads(line)
            key = r.get("commit", "")
            if exclude_commit and key == exclude_commit:
                continue
            runs.setdefault(key, len(runs) + 1)
            if r.get("outcome") in ("failed", "error"):
                rows.append({"repo": "local", "run_id": runs[key], "ts": _epoch(r.get("ts", ""), runs[key]),
                             "test_id": r["test_id"], "base_ref": r.get("branch", "main"),
                             "msg_hash": message_hash(r.get("message"))})
    ev = pd.DataFrame(rows, columns=["repo", "run_id", "ts", "test_id", "base_ref", "msg_hash"])
    now = int(ev["ts"].max()) + 1 if len(ev) else 0
    return ev, now


class TriageAgent:
    """Classify failures of a regression report."""

    def __init__(self, model_path: Path | None = MODEL_PATH, use_model: bool = True) -> None:
        self.booster = None
        self.threshold = 0.5
        self.features: list[str] = list(TRIAGE_COLS)
        mp = Path(model_path) if model_path else None
        if use_model and mp and mp.exists():
            try:
                import lightgbm as lgb

                self.booster = lgb.Booster(model_file=str(mp))
                meta = json.loads(mp.with_suffix(".json").read_text(encoding="utf-8"))
                self.threshold = float(meta.get("threshold_not_mine", 0.5))
                self.features = list(meta.get("feature_list", TRIAGE_COLS))
            except Exception:  # fall back to the rules rather than fail the pipeline
                self.booster = None

    @property
    def name(self) -> str:
        return "e2-lgbm-v1" if self.booster is not None else "rules"

    def run(self, failures: list[dict], history_path: Path, branch: str = "main", commit: str = "") -> TriageReport:
        """Classify `failures`.

        Args:
            failures: `[{"test_id", "outcome" (failed|error), "message", "duration_s"}]`, e.g. from a
                regression report's results.
            history_path: `history/test_outcomes.jsonl` of earlier runs.
            branch: The branch under test.
            commit: Commit id, carried into the report.

        Returns:
            One :class:`TriagedFailure` per input failure, in input order.
        """
        events, now = load_history(Path(history_path), commit)
        hist = TriageHistory(events)
        out = TriageReport(commit, self.name)
        for f in failures:
            tid, msg = f["test_id"], f.get("message", "")
            h = message_hash(msg)
            feats = {
                "prior_head_fail_7d": hist.prior_failures("local", tid, now, 7),
                "prior_head_fail_30d": hist.prior_failures("local", tid, now, 30),
                "failed_prev3_branch": int(hist.failed_in_previous("local", branch, tid, now, RULE_BRANCH_N)),
                "failed_prev10_branch": int(hist.failed_in_previous("local", branch, tid, now, 10)),
                "msg_hash_seen": int(hist.message_seen("local", h, now)),
                **fclass_onehot(msg), "status_error": int(f.get("outcome") == "error"), "n_job_rows": 1,
                "duration_s": f.get("duration_s"), "bound": 0}
            rule_branch, rule_msg = bool(feats["failed_prev3_branch"]), bool(feats["msg_hash_seen"])
            if self.booster is not None:
                row = [[feats.get(c, float("nan")) if feats.get(c) is not None else float("nan") for c in self.features]]
                p = float(self.booster.predict(pd.DataFrame(row, columns=self.features).to_numpy(dtype=float))[0])
                not_mine = p >= self.threshold
                conf = p if not_mine else 1 - p
                basis = f"model P(not mine) = {p:.2f} (threshold {self.threshold:.2f})"
            else:
                not_mine = rule_branch or rule_msg
                conf = 0.5 + 0.25 * (rule_branch + rule_msg) if not_mine else 0.5
                basis = "rules R-branch / R-msg"
            if not not_mine:
                klass, route_ = "mine", "repair"
                reason = f"{basis}; no evidence it was already failing"
            elif rule_branch or feats["prior_head_fail_30d"]:
                klass, route_ = "inherited", "ignore"
                reason = (f"{basis}; failed in {feats['prior_head_fail_30d']} earlier run(s) within 30 days"
                          + ("; failed in one of the previous 3 runs of the branch" if rule_branch else ""))
            else:
                klass, route_ = "flaky", "rerun"
                reason = f"{basis}; matches an earlier failure message but no prior failure of this test"
            out.failures.append(TriagedFailure(tid, klass, round(conf, 3), reason, route_))
        return out


def failures_of(report) -> list[dict]:
    """Failing results of a `RegressionReport` (or its JSON dict), full run preferred."""
    r = asdict(report) if hasattr(report, "__dataclass_fields__") else report
    block = r.get("full") or r["selected"]
    return [x for x in block["results"] if x["outcome"] in ("failed", "error")]
