# Phase 025: Data Transfer Manifest for Prisha Handover

**Generated**: 2026-09-02
**Target User**: Prisha
**Purpose**: Complete, measured verification manifest of all data assets required to reproduce BR-Bench and execute graph-layer pipeline tasks.

---

## 1. Required Untracked Data Assets (Must be Transferred)

These assets are not in git due to size and the 90-day GitHub Actions log retention expiry clock. They must be copied directly into the workspace root.

| Path | Size (Bytes) | Size (Human) | SHA256 Checksum | In Git? | Description |
|---|---:|---:|---|:---:|---|
| `data/raw/` | 2,734,020,926 | 4.9 GB | *[Tree of 304,534 gzipped logs]* | No | Irreplaceable raw job logs and workflow runs |
| `data/state/cursor.db` | 136,785,920 | 131 MB | `66097674f0b298597288999de6122a8e4e50bd958517410b1f0fc2ac832c9051` | No | SQLite harvest cursor state for `--as-of` reproduction |
| `data/interim/instances_raw.parquet` | 20,915,876 | 20.0 MB | `e46310f6f8cf97dce09058ac6a42b6dae54950338f45d1090d15bc933e45e3ad` | No | Harvested instance run metadata (165,349 rows) |
| `data/interim/changesets.parquet` | 9,125,179 | 8.7 MB | `147026892141e5d57ba459b7e8a35a399968a4276752281eb23ccea50f2b0dd3` | No | Extracted pull request file changesets |
| `data/interim/cochange.parquet` | 1,999,482 | 1.9 MB | `354992d670d73934f2f8939a071e3be53aa6a04de2190bd30e0f65273a5179c8` | No | Mined co-change support/confidence pairs |
| `data/interim/parsed_outcomes.parquet` | 285,109 | 278 KB | `c22e669d1c12a112ff3a4b178d99094c79918df6cef493cedd8666932cf844f9` | No | Extracted per-test execution outcomes |
| `data/interim/base_resolution_new.parquet` | 265,142 | 259 KB | `9d1a9c3045d3d2df7fcf2c2bd464ca4bc6144f263f70dde1696b6ad3869ddb3c` | No | Base resolution mapping across all failed runs |
| `data/interim/binding.parquet` | 183,289 | 179 KB | `0a7dc43c14c7ec49956c10791014cbd806fbea1dc6c03e61123be8e20ba8120f` | No | Test identifier to source file binding index |
| `data/interim/base_resolution.parquet` | 178,338 | 174 KB | `e630ea288db7a1d13f9f9d658c1fe1a3a411516f4948835848bb2fb7e03eb156` | No | Baseline resolution parquet |
| `data/interim/base_resolution_targeted.parquet` | 149,433 | 146 KB | `60991378bf823127e95495cacc8047f11d05751733362b1c5b4f2ae054f6641c` | No | Targeted group resolution parquet |
| `data/interim/outcomes.parquet` | 127,727 | 125 KB | `53479e36766bb80a5073c910daa0a904bc4baddee6926def500318604b769757` | No | Processed outcomes for RQ1 divergence |
| `data/interim/exact_green_verification.parquet` | 58,187 | 57 KB | `c0d800507a2389050771f758f0052dbb672c8cbc1714df0ff4a76a187d7d4301` | No | Exact green verification audit dataset |
| `data/interim/exact_green_verification_unattended_backup.parquet` | 58,801 | 57 KB | `ef1b9dbd6ea12fae2e5052309ce24bcfe76f49c09c252fc7c52ecaa7641ca62c` | No | Exact green verification unattended backup |
| `data/interim/exact_green_verification_pre019b_snapshot.parquet` | 58,550 | 57 KB | `f99a3a93db0425026df1f5108a79d3950fb2bf1359c3e9a7e0258d4a961cfb3c` | No | Exact green pre-019b snapshot |
| `data/interim/base_resolution_new_sampled.parquet` | 51,820 | 51 KB | `52c6f1406456012c8b02137aa599026da68a35e80dcdd11bf5a191cffc9ea08c` | No | Sampled base resolution dataset |
| `data/interim/parsed_outcomes_pre_d3.parquet` | 286,851 | 280 KB | `32dc7fb5c5c963628e8334ddbbd1573c6600c0f8664ba01579d45e4e20ae19dc` | No | Pre-D3 parsed outcomes |
| `data/interim/base_outcomes.parquet` | 18,134 | 18 KB | `e706c2ae301e3b1565b97dbe2e00106e891dd3f0c72d6d1d89fa4ac0f1a3cc92` | No | Base test outcomes |
| `data/interim/exact_green_verification_unattended_round2_removed.parquet` | 6,339 | 6 KB | `188a1005b6fae7c4f4cb696ec0f8a9e7f41cf63d395bf580eb5a71a4f02fdf75` | No | Exact green unattended removed entries |

**Total Required Untracked Transfer:** **2,904,575,102 bytes** (~2.90 GB payload / 5.07 GB disk footprint).

---

## 2. Tracked Repository Assets (Present in Git Clone)

These assets are already tracked in git and require **no manual file transfer**.

| Path | Size (Bytes) | Size (Human) | SHA256 Checksum | In Git? | Description |
|---|---:|---:|---|:---:|---|
| `vendor/graphify-br/` | 28,683,955 | 31 MB | *[Flat tree of 1,082 files]* | **Yes** | Graphify graph dependency layer |
| `data/frame/repos_raw.csv` | 8,857,455 | 8.4 MB | `e963a678e89aa27bf31ae2a9c26ec210a0bd6f7d9755f510aa1cf7bf8a619fa8` | **Yes** | Raw candidate repo list |
| `data/frame/seart_b.csv` | 5,754,941 | 5.5 MB | `d8de15dd99bcc2e09f94a259a72bfd98e5513a4f1c881aefc2603c43af441d78` | **Yes** | SEART query partition B |
| `data/frame/seart_a.csv` | 3,060,860 | 2.9 MB | `ec8fe63a145f5ef48bdc7820d41be44471680d97413c1e464f574fc03239529c` | **Yes** | SEART query partition A |
| `data/frame/repos.csv` | 228,570 | 223 KB | `71c265d63d4ba1ae0846ae159090a8748927864afd185b95ab66bcaa5995c079` | **Yes** | Candidate repository sampling frame |
| `data/frame/frame_v1_reserve.csv` | 206,799 | 202 KB | `ae597553db73531b038bb42af1a2c4c7efb0ed4eb3b44a581562c04bd57b4408` | **Yes** | Reserve sample frame |
| `data/frame/attrition_stage.csv` | 169,519 | 166 KB | `9037ea6a117f699cd3e3620ee7fc03c97360f1c8de9e9b4e40425b17b4c823ed` | **Yes** | Repository attrition stages |
| `data/frame/frame_v1.csv` | 31,277 | 31 KB | `c8d76b512e55932c42c4c9234dcd8dc6d216374bbe486e0b776ce0319d7d630c` | **Yes** | Primary sampling frame |
| `data/frame/QUERY.md` | 9,946 | 10 KB | `9d709b3b632df0627ca57861b046a915d95300d57818d371b6c21ea7fb91f3e4` | **Yes** | Frame SEART query definition |
| `data/frame/ATTRITION.json` | 2,383 | 2.3 KB | `fe6e1b7eb16fec320b4a24d929d57524476db9438a662305d41bb55f12c4bca6` | **Yes** | Frame attrition metadata |
| `data/interim/COCHANGE_PIN.json` | 33,524 | 33 KB | `ac6006c80ba3140018719464ac472ebc973c643166169f1f943d4f22e4de08ab` | **Yes** | Co-change corpus pin |
| `data/interim/INSTANCES_PIN.json` | 1,116 | 1.1 KB | `4ee54c77a90082c1c8dd6882118fe8e584afcff2f6aff339b0161a2ff1d8c486` | **Yes** | Instances table pin |
| `data/interim/CORPUS_PIN.json` | 328 | 328 B | `db3f59ed0bed984c70f2bf0b5efaab16dd181613a36706a621a6d34da7ce156f` | **Yes** | Harvest corpus pin |

---

## 3. Optional Regenerable Assets

| Path | Size (Bytes) | Size (Human) | In Git? | Notes |
|---|---:|---:|:---:|---|
| `data/clones/` | 1,748,135,633 | 1.7 GB | No | 12 blobless repository clones (can be re-cloned via `git clone --filter=blob:none`) |

---

## 4. Transfer Verification Procedure

1. Extract `blastradius_data.tar.gz` in workspace root.
2. Verify checksum of cursor database:
   ```bash
   sha256sum data/state/cursor.db
   # Expected: 66097674f0b298597288999de6122a8e4e50bd958517410b1f0fc2ac832c9051
   ```
3. Verify checksum of raw instances parquet:
   ```bash
   sha256sum data/interim/instances_raw.parquet
   # Expected: e46310f6f8cf97dce09058ac6a42b6dae54950338f45d1090d15bc933e45e3ad
   ```
4. Verify total uncompressed byte count:
   ```bash
   du -sb data/raw data/state/cursor.db data/interim
   ```
