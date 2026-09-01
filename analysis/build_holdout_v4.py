import csv
import gzip
import json
import pathlib
import random
import struct
from collections import Counter
from analysis.expected_audit import extract_harness_count

SEED = 20260831
MAX_UNCOMPRESSED_BYTES = 8 * 1024 * 1024
MAX_FAILURES_PER_LOG = 6
MAX_PER_REPO = 2

TARGETS = {
    "Maven": {"Failing": 10, "Clean": 5},
    "Gradle": {"Failing": 10, "Clean": 5},
    "pytest": {"Failing": 8, "Clean": 2}
}

HOLDOUT_V4_DIR = pathlib.Path("tests/fixtures/holdout_v4")
EXISTING_DIRS = [
    pathlib.Path("tests/fixtures/logs"),
    pathlib.Path("tests/fixtures/holdout"),
    pathlib.Path("tests/fixtures/holdout_v3")
]
RAW_DIR = pathlib.Path("data/raw")
FRAME_PATH = pathlib.Path("data/frame/frame_v1.csv")
MANIFEST_PATH = pathlib.Path("analysis/holdout_v3_manifest.json")

def get_gzip_isize(p: pathlib.Path) -> int:
    with open(p, "rb") as f:
        f.seek(-4, 2)
        return struct.unpack("<I", f.read(4))[0]

def get_used_jobs() -> set[str]:
    used = set()
    for d in EXISTING_DIRS:
        if d.exists():
            for p in d.glob("*.txt"):
                parts = p.stem.split("__")
                if len(parts) >= 3:
                    used.add(parts[2])
                elif len(parts) == 2:
                    used.add(parts[1])
    return used

def get_python_repos() -> set[str]:
    repos = set()
    if FRAME_PATH.exists():
        with open(FRAME_PATH, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row.get("lang") == "Python":
                    repos.add(f"{row['owner']}/{row['repo']}")
    return repos

def inspect_candidate(path_str: str) -> dict:
    p = pathlib.Path(path_str)
    try:
        isize = get_gzip_isize(p)
        if isize > MAX_UNCOMPRESSED_BYTES: return None
        jid = p.parent.name
        repo = p.parts[2].replace("__", "/")
        with gzip.open(p, "rt", encoding="utf-8", errors="replace") as gz:
            line = gz.readline()
            if not line: return None
            data = json.loads(line)
            body = data.get("body", "")
        cnt, h_type, evid = extract_harness_count(body)
        return {
            "path": path_str,
            "repo": repo,
            "job_id": jid,
            "harness_count": cnt,
            "harness_type": h_type,
            "uncompressed_size": isize
        }
    except Exception:
        return None

def main():
    used_jobs = get_used_jobs()
    candidates = []

    # Load Java logs from manifest
    if MANIFEST_PATH.exists():
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            for c in json.load(f):
                if c.get("status") == "ok" and c.get("uncompressed_size", 0) <= MAX_UNCOMPRESSED_BYTES:
                    candidates.append(c)

    # Load Python logs
    py_repos = get_python_repos()
    raw_files = [str(p) for p in RAW_DIR.glob("*/job/*/*/logs.jsonl.gz") if p.parts[2].replace("__", "/") in py_repos]
    for f in raw_files:
        res = inspect_candidate(f)
        if res: candidates.append(res)

    # Filter unused
    candidates = [c for c in candidates if c["job_id"] not in used_jobs]

    strata = {
        "Maven": {"Failing": [], "Clean": []},
        "Gradle": {"Failing": [], "Clean": []},
        "pytest": {"Failing": [], "Clean": []}
    }

    for c in candidates:
        ht = c["harness_type"] or ""
        cnt = c["harness_count"]
        
        # Classify Harness
        if "Maven" in ht:
            h_cat = "Maven"
        elif "Gradle" in ht:
            h_cat = "Gradle"
        elif "Pytest" in ht or "pytest" in ht.lower():
            h_cat = "pytest"
        else:
            # Check NO_SUMMARY and treat as clean for any? Actually we want Clean logs to match a specific harness
            # The v3 holdout picked NO_SUMMARY as "clean" but did not assign it a harness.
            # Here we need 5 Maven Clean, 5 Gradle Clean. If ht is NO_SUMMARY, we can't tell which it is.
            # We'll skip NO_SUMMARY, and only take "Maven (Clean)", "Gradle (Clean)", etc.
            continue

        if cnt is None or cnt == 0:
            strata[h_cat]["Clean"].append(c)
        elif 1 <= cnt <= MAX_FAILURES_PER_LOG:
            strata[h_cat]["Failing"].append(c)

    rng = random.Random(SEED)
    selected = []
    repo_counts = Counter()

    for ht, cat_targets in TARGETS.items():
        for cat, target in cat_targets.items():
            pool = strata[ht][cat]
            pool.sort(key=lambda x: (x["repo"], x["job_id"]))
            rng.shuffle(pool)
            
            added = 0
            for c in pool:
                if added >= target: break
                if repo_counts[c["repo"]] < MAX_PER_REPO:
                    selected.append(c)
                    repo_counts[c["repo"]] += 1
                    added += 1
            print(f"Strata {ht}-{cat}: Target {target}, Realised {added}")

    HOLDOUT_V4_DIR.mkdir(exist_ok=True, parents=True)
    # clean out old files if they exist
    for f in HOLDOUT_V4_DIR.glob("*.txt"):
        f.unlink()

    expected_content = "# Holdout v4 Expected Outcomes\n\n<!-- Format matching spec 008-B Expected Class -->\n"
    for c in selected:
        p = pathlib.Path(c["path"])
        repo_owner = p.parts[2]
        jid = c["job_id"]
        out_name = f"{repo_owner}__{jid}.txt"
        
        with gzip.open(p, "rt", encoding="utf-8", errors="replace") as gz:
            data = json.loads(gz.readline())
            body = data.get("body", "")
            
        (HOLDOUT_V4_DIR / out_name).write_text(body, encoding="utf-8")
        
        expected_content += f"## {out_name}\n"
        # Determine expected class based on where it was drawn from
        # Note: If it's from the Failing pool, expected class is Failing
        exp_cls = None
        for ht in TARGETS:
            if c in strata[ht]["Failing"]: exp_cls = "Failing"
            if c in strata[ht]["Clean"]: exp_cls = "Clean"
        
        expected_content += f"- **Expected Class**: {exp_cls}\n"
        expected_content += f"- **Expected Identifier Count**: \n"
        expected_content += f"- **Expected Identifiers**: \n"
        expected_content += f"- **Justification**: \n\n"

    (HOLDOUT_V4_DIR / "EXPECTED.md").write_text(expected_content, encoding="utf-8")
    
    # Overlap verification
    print("Overlap verification:")
    overlap_count = 0
    all_selected_jobs = {c["job_id"] for c in selected}
    used_jobs_again = get_used_jobs()
    for j in all_selected_jobs:
        if j in used_jobs_again:
            overlap_count += 1
    print(f"Overlap count: {overlap_count}")

if __name__ == "__main__":
    main()
