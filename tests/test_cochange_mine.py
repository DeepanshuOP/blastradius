"""Tests for git commit co-change mining (analysis/cochange_mine.py).

Verifies support, confidence, and lift metrics computed over real repository
git history against hand-computed ground truth derived via direct git commands.
"""

from __future__ import annotations

import json
from pathlib import Path

import pyarrow.parquet as pq
import pytest

from analysis.cochange_mine import (
    COCHANGE_SCHEMA,
    DEFAULT_AS_OF,
    discover_cloned_repos,
    mine_all_repos,
    mine_repo_cochange,
)


def test_cochange_hand_computed_castorini() -> None:
    """Assert support, confidence, and lift against hand-computed ground truth on castorini/anserini.

    Git commands used to derive ground truth:
    1. Total non-merge commits in window (2025-08-29T14:13:00Z to 2026-08-29T14:13:00Z):
       git -C data/clones/castorini__anserini rev-list --count --no-merges \\
           --since="2025-08-29T14:13:00Z" --until="2026-08-29T14:13:00Z" HEAD
       -> 327 commits. 19 commits touch > 50 files and are skipped. Mined commits = 308.

    2. Commits touching src/main/java/io/anserini/search/topicreader/Topics.java with <= 50 files:
       13 qualifying commits:
         23c4dfdd, cb611fa2, 9bfc04b2, 25918902, f8e3bcb6, 08ef0ded, c4275251,
         7ebe1b38, f2ae641e, 2133d40d, a11aac48, 4c2e2044, d276b57e
       (3 commits skipped with > 50 files: 5f091ba5 [213], 6caeb33a [1773], 43e90b01 [618])
       -> n_commits_a = 13.

    3. Commits touching src/test/java/io/anserini/search/topicreader/TopicReaderTest.java with <= 50 files:
       13 qualifying commits:
         23c4dfdd, fe3a07e4, 9bfc04b2, 25918902, f8e3bcb6, bc3b9f91, c4275251,
         2133d40d, ed1b9e84, a11aac48, 4c2e2044, d276b57e, 03ae0b0f
       (4 commits skipped with > 50 files: 5f091ba5 [213], 4074cde6 [106], 6caeb33a [1773], 43e90b01 [618])
       -> n_commits_b = 13.

    4. Co-occurring commits (both modified in same commit):
       9 commits:
         23c4dfdd, 9bfc04b2, 25918902, f8e3bcb6, c4275251, 2133d40d,
         a11aac48, 4c2e2044, d276b57e
       -> support = 9.

    Derived metrics:
      conf_a_to_b = support / n_commits_a = 9 / 13 ≈ 0.69230769
      conf_b_to_a = support / n_commits_b = 9 / 13 ≈ 0.69230769
      lift        = (support * n_commits_total) / (n_commits_a * n_commits_b)
                  = (9 * 308) / (13 * 13) = 2772 / 169 ≈ 16.40236686
    """
    repo_path = Path("data/clones/castorini__anserini")
    if not repo_path.exists():
        pytest.skip("data/clones/castorini__anserini not present")

    rows, stats = mine_repo_cochange(
        repo_full="castorini/anserini",
        repo_path=repo_path,
        as_of="2026-08-29T14:13:00Z",
        window_days=365,
        support_threshold=3,
        max_files_per_commit=50,
    )

    assert stats["repo_full"] == "castorini/anserini"
    assert stats["total_commits_in_window"] == 327
    assert stats["merges_skipped"] == 0
    assert stats["oversize_commits_skipped"] == 19
    assert stats["mined_commits"] == 308

    target_pair = (
        "src/main/java/io/anserini/search/topicreader/Topics.java",
        "src/test/java/io/anserini/search/topicreader/TopicReaderTest.java",
    )

    matching = [
        r for r in rows
        if (r["file_a"] == target_pair[0] and r["file_b"] == target_pair[1])
        or (r["file_a"] == target_pair[1] and r["file_b"] == target_pair[0])
    ]

    assert len(matching) == 1, f"Expected exactly 1 pair record for {target_pair}"
    row = matching[0]

    assert row["support"] == 9
    assert row["n_commits_a"] == 13
    assert row["n_commits_b"] == 13
    assert row["n_commits_total"] == 308
    assert row["conf_a_to_b"] == pytest.approx(9.0 / 13.0)
    assert row["conf_b_to_a"] == pytest.approx(9.0 / 13.0)
    assert row["lift"] == pytest.approx(2772.0 / 169.0)
    assert row["window_days"] == 365
    assert row["as_of"] == "2026-08-29T14:13:00Z"


def test_cochange_pruning_and_symmetry(tmp_path: Path) -> None:
    """Verify that support threshold prunes small pairs and unordered file pairs are canonicalized."""
    repo_path = Path("data/clones/castorini__anserini")
    if not repo_path.exists():
        pytest.skip("data/clones/castorini__anserini not present")

    rows, stats = mine_repo_cochange(
        repo_full="castorini/anserini",
        repo_path=repo_path,
        as_of="2026-08-29T14:13:00Z",
        window_days=365,
        support_threshold=5,  # Higher threshold
        max_files_per_commit=50,
    )

    for r in rows:
        assert r["support"] >= 5, f"Pair {r['file_a']} <-> {r['file_b']} has support {r['support']} < 5"
        assert r["file_a"] < r["file_b"], "File pairs must be alphabetically sorted"
        assert 0.0 <= r["conf_a_to_b"] <= 1.0
        assert 0.0 <= r["conf_b_to_a"] <= 1.0
        assert r["lift"] >= 0.0


def test_mine_all_repos_output(tmp_path: Path) -> None:
    """Test full mine_all_repos pipeline writing to parquet and pin JSON on a single repository."""
    repo_path = Path("data/clones/castorini__anserini")
    if not repo_path.exists():
        pytest.skip("data/clones/castorini__anserini not present")

    out_parquet = tmp_path / "cochange_test.parquet"
    out_pin = tmp_path / "COCHANGE_PIN_test.json"

    total_pairs, stats = mine_all_repos(
        clones_dir=Path("data/clones"),
        repo_filter=["castorini/anserini"],
        as_of=DEFAULT_AS_OF,
        window_days=365,
        support_threshold=3,
        max_files_per_commit=50,
        output_parquet=out_parquet,
        pin_file=out_pin,
    )

    assert out_parquet.is_file()
    assert out_pin.is_file()
    assert total_pairs > 0

    # Verify parquet schema
    table = pq.read_table(out_parquet)
    assert table.schema.names == COCHANGE_SCHEMA.names
    assert table.num_rows == total_pairs

    # Verify pin JSON
    with open(out_pin, encoding="utf-8") as f:
        pin_data = json.load(f)

    assert pin_data["as_of"] == DEFAULT_AS_OF
    assert pin_data["window_days"] == 365
    assert pin_data["support_threshold"] == 3
    assert pin_data["total_pairs_retained"] == total_pairs
    assert len(pin_data["repos"]) == 1
    assert pin_data["repos"][0]["repo_full"] == "castorini/anserini"
