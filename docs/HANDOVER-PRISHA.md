# BlastRadius Handover: Prisha

## 1. What to Copy (Measured Data Transfer)
Copy these untracked directories into repository root (`/home/<user>/blastradius` on native ext4):
- `data/raw/` (4.9 GB / 2,734,020,926 B, irreplaceable due to 90-day GitHub Actions log expiry)
- `data/state/cursor.db` (131 MB / 136,785,920 B, required for point-in-time `--as-of` state reproduction)
- `data/interim/*.parquet` (33 MB / 33,803,225 B, interim tables required for analysis and tables)
- *Optional:* `data/clones/` (1.7 GB / 1,748,135,633 B, can alternatively be re-cloned)
- *Note:* `vendor/graphify-br/` (34 MB / 28,683,955 B) and `data/frame/` (9 files) are tracked in git.

## 2. Credentials & PATs
Generate 3 fresh GitHub Personal Access Tokens (PATs) yourself. **Never receive or request Deepanshu's PATs.**
Add your tokens to `.env` (which is gitignored):
```env
GITHUB_TOKEN_1=ghp_...
GITHUB_TOKEN_2=ghp_...
GITHUB_TOKEN_3=ghp_...
```
Always invoke network commands with credentials: `uv run --env-file .env <command>`.

## 3. Repo-Local Git Identity
Run repo-local git configuration immediately inside the cloned repository:
```bash
git config user.name "Prisha"
git config user.email "<your-github-noreply-or-authorized-email>"
```
*Why:* The global git configuration routes commits to a different GitHub account, which causes attribution discrepancies and violates commit author policies.

## 4. VS Code WSL Execution Requirement
Always open VS Code inside native WSL2 (`code .` inside `/home/<user>/blastradius`).
The bottom-left status badge in VS Code **must read `WSL: Ubuntu`**.
*Why:* Opening from Windows reaches ext4 via `\wsl.localhost`, causing CRLF line ending corruption, root ownership file locks, and path resolution failures.

## 5. Assigned Scope & Invariant Boundaries
- **IN SCOPE:** ROADMAP §10 Graph Layer only (Graphify integration, code property graph extraction, test-to-code reachability).
- **STRICTLY OUT OF SCOPE (DO NOT TOUCH):** The labelling engine (`src/label/`) and base resolution (`analysis/resolve_bases.py`, `src/label/base_resolve.py`).
  *Reason:* These components enforce **Integrity Invariant 6** (an empty base failure set is never "green" and missing base runs must emit no labels). Modifying them risks invalidating the ground-truth benchmark.

## 6. Day-One Verification Checklist
Run these commands in order upon setting up your environment:
- [ ] `uname -s && pwd && uv run python --version` (Confirms Linux, repo path, Python 3.11.15)
- [ ] `uv sync` (Installs dependencies and synchronizes virtual environment)
- [ ] `uv run pytest -q --tb=no` (Verifies test suite passes; expects 463 passed, 1 skipped)
- [ ] `uv run python analysis/holdout_eval.py` (Confirms 100% precision/recall on `tests/fixtures/holdout/` — development-set fit, not held-out precision (D-37))
- [ ] `make tables` (Regenerates all paper numbers and tables from transferred parquets)
