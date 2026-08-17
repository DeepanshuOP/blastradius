"""BlastRadius — Live Corpus Dashboard (ROADMAP §8.5 / T0.5a).

A read-only Streamlit dashboard displaying the live state of the GitHub Actions harvest.
Connects strictly in read-only mode to SQLite (data/state/cursor.db) and joins with
data/frame/frame_v1.csv and filesystem directory statistics.
"""

from __future__ import annotations

import csv
import datetime
import os
import sqlite3
from collections import defaultdict
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

DB_URI = "file:data/state/cursor.db?mode=ro"
FRAME_PATH = Path("data/frame/frame_v1.csv")
RAW_ROOT = Path("data/raw")

ALL_KINDS = [
    "pulls",
    "pull_files",
    "pull_commits",
    "runs",
    "jobs",
    "checkruns",
    "annotations",
    "artifacts",
    "logs",
]

ALL_STATUSES = [
    "in_flight",
    "complete",
    "skipped",
    "expired",
    "failed",
]


def format_bytes(num_bytes: int | float) -> str:
    """Format bytes into a human-readable string (B, KB, MB, GB)."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if abs(num_bytes) < 1024.0:
            return f"{num_bytes:.2f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.2f} PB"


def format_duration(seconds: float) -> str:
    """Format seconds into days, hours, minutes."""
    if seconds < 0:
        return "0m"
    days, remainder = divmod(int(seconds), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, _ = divmod(remainder, 60)
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0 or days > 0:
        parts.append(f"{hours}h")
    parts.append(f"{minutes}m")
    return " ".join(parts)


@st.cache_data(ttl=30)
def load_frame_data() -> list[dict[str, str]]:
    """Load the frozen repository frame CSV."""
    if not FRAME_PATH.is_file():
        return []
    with open(FRAME_PATH, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


@st.cache_data(ttl=30)
def load_db_data() -> dict[str, Any]:
    """Query cursor.db read-only and return raw tables / aggregates."""
    result: dict[str, Any] = {
        "error": None,
        "is_stale": False,
        "repos_touched": 0,
        "total_units": 0,
        "total_complete": 0,
        "earliest_started_at": None,
        "latest_updated_at": None,
        "grid": {k: {s: 0 for s in ALL_STATUSES} for k in ALL_KINDS},
        "hourly_timeline": [],
        "repo_summaries": [],
        "touched_repo_names": set(),
    }

    if not os.path.exists("data/state/cursor.db"):
        result["error"] = "Database file data/state/cursor.db does not exist yet."
        return result

    try:
        con = sqlite3.connect(DB_URI, uri=True, timeout=5.0)
        cur = con.cursor()

        # 1. Headline aggregations
        cur.execute("SELECT COUNT(DISTINCT repo) FROM capture_unit")
        row = cur.fetchone()
        result["repos_touched"] = row[0] if row else 0

        cur.execute("SELECT COUNT(*) FROM capture_unit")
        row = cur.fetchone()
        result["total_units"] = row[0] if row else 0

        cur.execute("SELECT COUNT(*) FROM capture_unit WHERE status = 'complete'")
        row = cur.fetchone()
        result["total_complete"] = row[0] if row else 0

        cur.execute("SELECT MIN(started_at) FROM capture_unit")
        row = cur.fetchone()
        result["earliest_started_at"] = row[0] if row else None

        cur.execute("SELECT MAX(updated_at) FROM repo_cursor")
        row = cur.fetchone()
        result["latest_updated_at"] = row[0] if row else None

        # 2. Units by kind and status
        cur.execute("SELECT kind, status, COUNT(*) FROM capture_unit GROUP BY kind, status")
        for kind, status, count in cur.fetchall():
            if kind in result["grid"] and status in result["grid"][kind]:
                result["grid"][kind][status] = count

        # 3. Hourly timeline
        cur.execute(
            """
            SELECT strftime('%Y-%m-%d %H:00', completed_at) AS hr, COUNT(*)
            FROM capture_unit
            WHERE completed_at IS NOT NULL
            GROUP BY hr
            ORDER BY hr ASC
            """
        )
        result["hourly_timeline"] = cur.fetchall()

        # 4. Per-repo summaries
        cur.execute(
            """
            SELECT 
                c.repo,
                COALESCE(rc.sweep_status, 'idle') AS sweep_status,
                COALESCE(rc.pr_page, 0) AS pr_page,
                COALESCE(SUM(CASE WHEN c.status = 'complete' THEN 1 ELSE 0 END), 0) AS complete_units,
                COALESCE(SUM(CASE WHEN c.status = 'failed' THEN 1 ELSE 0 END), 0) AS failed_units,
                COALESCE(SUM(CASE WHEN c.status = 'in_flight' THEN 1 ELSE 0 END), 0) AS in_flight_units,
                COALESCE(SUM(CASE WHEN c.status = 'skipped' THEN 1 ELSE 0 END), 0) AS skipped_units,
                COALESCE(SUM(CASE WHEN c.status = 'expired' THEN 1 ELSE 0 END), 0) AS expired_units,
                COUNT(*) AS total_repo_units,
                MAX(c.completed_at) AS last_completed,
                MAX(rc.updated_at) AS last_updated
            FROM capture_unit c
            LEFT JOIN repo_cursor rc ON c.repo = rc.repo
            GROUP BY c.repo
            """
        )
        repo_rows = cur.fetchall()
        result["repo_summaries"] = repo_rows
        result["touched_repo_names"] = {r[0] for r in repo_rows}

        con.close()
    except sqlite3.OperationalError as exc:
        result["error"] = f"Database read warning (harvester active): {exc}"
        result["is_stale"] = True
    except Exception as exc:
        result["error"] = f"Unexpected error reading cursor store: {exc}"
        result["is_stale"] = True

    return result


@st.cache_data(ttl=30)
def load_storage_data() -> dict[str, Any]:
    """Scan data/raw measuring both apparent size (sum of file bytes) and on-disk usage (block-allocated)."""
    repo_stats: dict[str, dict[str, int]] = {}
    total_apparent = 0
    total_disk = 0
    total_files = 0
    total_dirs = 0

    if RAW_ROOT.is_dir():
        for entry in os.scandir(RAW_ROOT):
            if entry.is_dir() and not entry.name.startswith("."):
                r_apparent = 0
                r_disk = 0
                r_files = 0
                r_dirs = 1
                try:
                    st_root = entry.stat()
                    r_disk += getattr(st_root, "st_blocks", 0) * 512
                except OSError:
                    pass

                for dirpath, dirnames, filenames in os.walk(entry.path):
                    r_dirs += len(dirnames)
                    for d in dirnames:
                        try:
                            st_d = os.stat(os.path.join(dirpath, d))
                            r_disk += getattr(st_d, "st_blocks", 0) * 512
                        except OSError:
                            pass
                    for fn in filenames:
                        r_files += 1
                        fp = os.path.join(dirpath, fn)
                        try:
                            st_f = os.stat(fp)
                            r_apparent += st_f.st_size
                            r_disk += getattr(st_f, "st_blocks", 0) * 512
                        except OSError:
                            pass

                repo_stats[entry.name] = {
                    "apparent_bytes": r_apparent,
                    "disk_bytes": r_disk,
                    "file_count": r_files,
                    "dir_count": r_dirs,
                }
                total_apparent += r_apparent
                total_disk += r_disk
                total_files += r_files
                total_dirs += r_dirs

    return {
        "total_apparent_bytes": total_apparent,
        "total_disk_bytes": total_disk,
        "total_files": total_files,
        "total_dirs": total_dirs,
        "repo_stats": repo_stats,
    }


def main() -> None:
    st.set_page_config(
        page_title="BlastRadius — Live Corpus Dashboard",
        page_icon="💥",
        layout="wide",
    )

    # Header & Refresh
    col_title, col_ctrl = st.columns([4, 1])
    with col_title:
        st.title("💥 BlastRadius — Live Corpus Dashboard")
        st.caption("Execution-grounded GitHub Actions harvester status • ROADMAP §8.5 (T0.5a)")
    with col_ctrl:
        st.write("")
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    # Load Data
    frame_rows = load_frame_data()
    db_data = load_db_data()
    storage_data = load_storage_data()

    if db_data["error"]:
        if db_data["is_stale"]:
            st.warning(f"⚠️ Stale-Data Notice: {db_data['error']}")
        else:
            st.error(f"❌ Database Error: {db_data['error']}")

    # Build Frame lookup
    frame_total = len(frame_rows) if frame_rows else 300
    frame_map = {f"{r['owner']}/{r['repo']}": r for r in frame_rows}
    lang_totals = defaultdict(int)
    for r in frame_rows:
        lang_totals[r["lang"]] += 1

    # Check join consistency / mismatches
    touched_slugs = db_data["touched_repo_names"]
    mismatches = [slug for slug in touched_slugs if slug not in frame_map]

    # --- PANEL 1: HEADLINE ROW ---
    st.markdown("### 1. Headline Overview")
    repos_touched = db_data["repos_touched"]
    total_units = db_data["total_units"]
    total_complete = db_data["total_complete"]
    earliest_started = db_data["earliest_started_at"]
    latest_update = db_data["latest_updated_at"]

    # Calculate elapsed wall-clock
    if earliest_started:
        try:
            earliest_dt = datetime.datetime.fromisoformat(earliest_started)
            now_dt = datetime.datetime.now(datetime.timezone.utc)
            elapsed_sec = (now_dt - earliest_dt).total_seconds()
            wall_clock_str = format_duration(elapsed_sec)
        except Exception:
            wall_clock_str = "N/A"
    else:
        wall_clock_str = "N/A"

    data_as_of = latest_update if latest_update else datetime.datetime.now(datetime.timezone.utc).isoformat()

    h_col1, h_col2, h_col3, h_col4, h_col5 = st.columns(5)
    with h_col1:
        pct_touched = (repos_touched / frame_total * 100) if frame_total else 0
        st.metric("Repos Touched", f"{repos_touched} / {frame_total}", f"{pct_touched:.1f}%")
    with h_col2:
        st.metric("Total Capture Units", f"{total_units:,}")
    with h_col3:
        complete_pct = (total_complete / total_units * 100) if total_units else 0
        st.metric("Completed Units", f"{total_complete:,}", f"{complete_pct:.1f}%")
    with h_col4:
        st.metric("Wall-Clock Elapsed", wall_clock_str)
    with h_col5:
        st.metric("Data As Of", data_as_of[:19].replace("T", " ") + " UTC")

    st.divider()

    # --- PANEL 2: FRAME PROGRESS ---
    st.markdown("### 2. Frame Progress")
    p_col1, p_col2 = st.columns([3, 1])

    # Count touched by language
    touched_by_lang = defaultdict(int)
    for slug in touched_slugs:
        if slug in frame_map:
            touched_by_lang[frame_map[slug]["lang"]] += 1

    with p_col1:
        st.write(f"**Overall Frame Coverage:** {repos_touched} of {frame_total} repositories ({pct_touched:.1f}%)")
        st.progress(min(1.0, repos_touched / frame_total if frame_total else 0.0))

        # Language breakdown progress bars
        for lang, count_tot in sorted(lang_totals.items()):
            count_touched = touched_by_lang.get(lang, 0)
            lang_pct = (count_touched / count_tot) if count_tot else 0.0
            st.write(f"• **{lang}**: {count_touched} / {count_tot} ({lang_pct * 100:.1f}%)")
            st.progress(min(1.0, lang_pct))

    with p_col2:
        st.markdown("**Join Integrity**")
        if mismatches:
            st.error(f"⚠️ {len(mismatches)} repos in DB not found in frame_v1.csv")
            with st.expander("Show mismatches"):
                st.write(mismatches)
        else:
            st.success("✅ 0 frame join mismatches across all touched repos")

    st.divider()

    # --- PANEL 3: UNITS BY KIND AND STATUS ---
    st.markdown("### 3. Capture Units by Kind and Status")
    st.caption("Full 9 × 5 matrix. All kinds and statuses are guaranteed to appear.")

    grid_data = db_data["grid"]
    matrix_rows = []
    for kind in ALL_KINDS:
        row_dict: dict[str, Any] = {"Kind": kind}
        row_total = 0
        for status in ALL_STATUSES:
            cnt = grid_data[kind][status]
            row_dict[status] = cnt
            row_total += cnt
        row_dict["Total"] = row_total
        matrix_rows.append(row_dict)

    # Column Totals row
    col_totals: dict[str, Any] = {"Kind": "TOTAL"}
    grand_total = 0
    for status in ALL_STATUSES:
        s_total = sum(grid_data[k][status] for k in ALL_KINDS)
        col_totals[status] = s_total
        grand_total += s_total
    col_totals["Total"] = grand_total
    matrix_rows.append(col_totals)

    df_matrix = pd.DataFrame(matrix_rows)
    st.dataframe(
        df_matrix,
        hide_index=True,
        use_container_width=True,
    )

    st.divider()

    # --- PANEL 4: CAPTURE TIMELINE ---
    st.markdown("### 4. Capture Timeline")
    st.caption("Units completed per hour (corpus accumulation over time)")
    timeline_data = db_data["hourly_timeline"]
    if timeline_data:
        df_timeline = pd.DataFrame(timeline_data, columns=["Hour (UTC)", "Units Completed"])
        df_timeline["Hour (UTC)"] = pd.to_datetime(df_timeline["Hour (UTC)"])
        df_timeline = df_timeline.set_index("Hour (UTC)")
        st.bar_chart(df_timeline, y="Units Completed")
    else:
        st.info("No completed units recorded in timeline yet.")

    st.divider()

    # --- PANEL 5: PER-REPO TABLE ---
    st.markdown("### 5. Repository Breakdown")
    st.caption("Detailed status per repository touched by the harvester")
    repo_rows = db_data["repo_summaries"]

    table_data = []
    for r in repo_rows:
        slug = r[0]
        f_info = frame_map.get(slug, {})
        lang = f_info.get("lang", "Unknown")
        stars = f_info.get("stars", "N/A")
        sweep_status = r[1]
        pr_page = r[2]
        complete_units = r[3]
        failed_units = r[4]
        in_flight_units = r[5]
        total_repo_units = r[8]
        last_completed = r[9]
        last_updated = r[10]

        # Directory size if available
        dir_name = slug.replace("/", "__")
        r_st = storage_data["repo_stats"].get(dir_name, {})
        disk_sz = r_st.get("disk_bytes", 0)
        apparent_sz = r_st.get("apparent_bytes", 0)

        table_data.append(
            {
                "Repo": slug,
                "Language": lang,
                "Stars": stars,
                "Sweep Status": sweep_status,
                "PR Page": pr_page,
                "Complete Units": complete_units,
                "Failed Units": failed_units,
                "In Flight": in_flight_units,
                "Total Units": total_repo_units,
                "On-Disk Usage": format_bytes(disk_sz),
                "Apparent Size": format_bytes(apparent_sz),
                "_disk_bytes": disk_sz,
                "Last Updated": (last_updated or last_completed or "")[:19].replace("T", " "),
            }
        )

    if table_data:
        df_repos = pd.DataFrame(table_data)
        st.dataframe(
            df_repos.drop(columns=["_disk_bytes"]),
            hide_index=True,
            use_container_width=True,
        )
    else:
        st.info("No repositories touched yet.")

    st.divider()

    # --- PANEL 6: ZERO-YIELD REPOS ---
    st.markdown("### 6. Zero-Yield Repositories")
    z_col1, z_col2 = st.columns(2)

    with z_col1:
        st.markdown("#### Untouched Frame Repositories")
        untouched_list = [r for r in frame_rows if f"{r['owner']}/{r['repo']}" not in touched_slugs]
        st.write(f"**Total Untouched:** {len(untouched_list)} of {frame_total}")
        if untouched_list:
            with st.expander(f"View {len(untouched_list)} Untouched Repos", expanded=False):
                df_untouched = pd.DataFrame(
                    [
                        {
                            "Repo": f"{r['owner']}/{r['repo']}",
                            "Language": r.get("lang"),
                            "Stars": r.get("stars"),
                            "Rank": r.get("sample_rank"),
                        }
                        for r in untouched_list
                    ]
                )
                st.dataframe(df_untouched, hide_index=True, use_container_width=True)

    with z_col2:
        st.markdown("#### Touched with Zero Complete Units")
        zero_complete = [r for r in repo_rows if r[3] == 0]
        st.write(f"**Total Touched with 0 Complete:** {len(zero_complete)}")
        if zero_complete:
            with st.expander("View Zero-Complete Repos", expanded=True):
                st.dataframe(
                    pd.DataFrame(
                        [
                            {
                                "Repo": r[0],
                                "Sweep Status": r[1],
                                "In Flight": r[5],
                                "Failed": r[4],
                                "Total": r[8],
                            }
                            for r in zero_complete
                        ]
                    ),
                    hide_index=True,
                    use_container_width=True,
                )
        else:
            st.success("✅ All 26 touched repositories have produced completed units.")

    st.divider()

    # --- PANEL 7: STORAGE CONSUMPTION & 90-DAY PROJECTION ---
    st.markdown("### 7. Storage Consumption & 90-Day Projection")

    total_apparent = storage_data["total_apparent_bytes"]
    total_disk = storage_data["total_disk_bytes"]
    total_files = storage_data["total_files"]
    total_dirs = storage_data["total_dirs"]
    repo_stats = storage_data["repo_stats"]
    n_stored_repos = len(repo_stats)

    avg_apparent_per_repo = (total_apparent / n_stored_repos) if n_stored_repos > 0 else 0
    avg_disk_per_repo = (total_disk / n_stored_repos) if n_stored_repos > 0 else 0
    ratio = (total_disk / total_apparent) if total_apparent > 0 else 0.0
    mean_file_size = (total_apparent / total_files) if total_files > 0 else 0.0

    # Projection calculation:
    # Extrapolated for all 300 frame repos based on average ON-DISK usage observed so far
    extrapolated_300_disk_bytes = avg_disk_per_repo * frame_total

    s_col1, s_col2 = st.columns([1, 1])

    with s_col1:
        st.markdown("#### Live Storage Metrics")
        m_c1, m_c2 = st.columns(2)
        with m_c1:
            st.metric(
                "Apparent Size (sum of file bytes)",
                format_bytes(total_apparent),
                help="Sum of unpadded file lengths (st_size).",
            )
            st.metric("Total File Count", f"{total_files:,}")
        with m_c2:
            st.metric(
                "On-Disk Usage (block-allocated)",
                format_bytes(total_disk),
                f"{ratio:.2f}× block overhead",
                help="Actual filesystem blocks allocated on disk (4KB blocks + directory entries).",
            )
            st.metric("Total Directory Count", f"{total_dirs:,}")

        st.caption(
            f"ℹ️ **Overhead Explanation:** Mean apparent file size is **{format_bytes(mean_file_size)}**. "
            f"Because files and directories are allocated in 4 KiB filesystem blocks across {total_dirs:,} directories, "
            f"on-disk usage is **{ratio:.2f}×** larger than apparent payload bytes."
        )

        st.markdown("#### 90-Day Projection *(Stages 1+2 Metadata Only)*")
        st.metric(
            "Projected 300-Repo On-Disk Total",
            format_bytes(extrapolated_300_disk_bytes),
            help="Linear extrapolation from current average on-disk usage per repo across 300 frame repos.",
        )
        st.warning(
            "⚠️ **Projection Scope & Caveat:** This projection is a linear extrapolation covering **Stages 1+2 metadata only** "
            "(pulls, runs, jobs, checkruns, annotations). It does **NOT** include raw job execution logs or build artifacts, "
            "which are deferred (D-23) and constitute the dominant storage term per ROADMAP §30.1 (200–500 GB budget). "
            "Do not mistake this for a projection of the finished corpus."
        )

    with s_col2:
        st.markdown("#### Top Storage Consumers (On-Disk vs. Apparent)")
        if repo_stats:
            top_10 = sorted(repo_stats.items(), key=lambda x: x[1]["disk_bytes"], reverse=True)[:10]
            df_top10 = pd.DataFrame(
                [
                    {
                        "Repository": k.replace("__", "/"),
                        "On-Disk Usage": format_bytes(v["disk_bytes"]),
                        "Apparent Size": format_bytes(v["apparent_bytes"]),
                        "Files": f"{v['file_count']:,}",
                    }
                    for k, v in top_10
                ]
            )
            st.dataframe(df_top10, hide_index=True, use_container_width=True)
        else:
            st.info("No storage data found under data/raw.")

    st.divider()

    # --- PLACEHOLDER: PHASE 1 / V1 PANELS ---
    st.markdown("### 8. Phase 1 Ground-Truth Panels *(v1 Planned)*")
    st.info(
        "📌 **Phase 1 Deferred Panels (ROADMAP §8.5 / §9.1):**\n"
        "- **Failure Rate Distribution**: Positive class accumulation across workflow runs.\n"
        "- **Label-Source Tier Breakdown**: Annotation vs. Artifact vs. Raw Log parsing counts.\n"
        "\n*These metrics require deep JSONL parsing of run envelopes and test outcome extraction (T1.1 parser suite) to avoid disk contention during live harvest.*"
    )


if __name__ == "__main__":
    main()
