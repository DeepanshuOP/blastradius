"""E1 figures from `data/processed/rq2_results.json` (written by `analysis/rq2_predictor.py`).

fig3_recall_at_k.pdf       recall vs share of the suite run, one line per method
fig4_learning_curve.pdf    test Recall@10 vs share of training data
fig5_feature_importance.pdf  mean |SHAP| share per feature family

Numbers come from the JSON only; nothing is recomputed here. Skips with a
warning when matplotlib is absent, like `rq1_divergence.write_figures`.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

RESULTS = Path("data/processed/rq2_results.json")
OUT = Path("paper/generated")


def main() -> int:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("WARNING: matplotlib is not installed; skipping fig3-fig5.")
        return 0
    if not RESULTS.exists():
        print(f"{RESULTS} missing: run `make e1` first", file=sys.stderr)
        return 1
    r = json.loads(RESULTS.read_text())
    OUT.mkdir(parents=True, exist_ok=True)
    meta = {"CreationDate": None}

    plt.figure(figsize=(8, 5))
    xs = [100 * f for f in r["curve_fracs"]]
    for m in r["order"]:
        style = "-" if m == "ours" else ":" if m in ("B0", "B1") else "--"
        plt.plot(xs, r["recall_vs_suite"][m], style, marker="o" if m == "ours" else None,
                 linewidth=2.5 if m == "ours" else 1.3, label=f"{m} {r['methods'][m]}")
    plt.xscale("log")
    plt.xlabel("share of candidate test files run (%)")
    plt.ylabel("mean recall of failing test files")
    plt.ylim(0, 1.0)
    plt.title("Recall vs suite fraction (test split)")
    plt.legend(fontsize=7, loc="lower right")
    plt.tight_layout()
    plt.savefig(OUT / "fig3_recall_at_k.pdf", metadata=meta)
    plt.close()

    plt.figure(figsize=(8, 5))
    lc = r["learning_curve"]
    ks = sorted(lc, key=float)
    plt.plot([f"{int(float(k) * 100)}%\n(n={lc[k]['n']})" for k in ks], [lc[k]["r10"] for k in ks], marker="o",
             label="Recall@10")
    plt.plot([f"{int(float(k) * 100)}%\n(n={lc[k]['n']})" for k in ks], [lc[k]["ap"] for k in ks], marker="s",
             linestyle="--", label="MAP")
    plt.xlabel("share of the most recent training instances")
    plt.ylabel("test split")
    plt.ylim(0, 1.0)
    plt.title("Learning curve")
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUT / "fig4_learning_curve.pdf", metadata=meta)
    plt.close()

    plt.figure(figsize=(8, 5))
    fam = sorted(r["family_importance"].items(), key=lambda kv: kv[1])
    plt.barh([k for k, _ in fam], [100 * v for _, v in fam], color="skyblue", edgecolor="black")
    plt.xlabel("share of mean |SHAP| (%)")
    plt.title("Feature-family importance (test split, final model)")
    plt.tight_layout()
    plt.savefig(OUT / "fig5_feature_importance.pdf", metadata=meta)
    plt.close()
    print("Generated fig3_recall_at_k.pdf, fig4_learning_curve.pdf, fig5_feature_importance.pdf")
    return 0


if __name__ == "__main__":
    sys.exit(main())
