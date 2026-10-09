"""Impact Analysis Agent: user story + codebase -> impact analysis document.

Three evidence sources, weighted the way BR-Bench says they deserve:

1. **Requirement -> code.** Story terms are matched to source files (TF-IDF over
   identifiers, paths, docstrings and comments). With an LLM configured, the model
   also reads the story and the candidate files and may add or explain files.
2. **Code -> tests.** Tests that depend on a changed file are found by reverse
   reachability on the commit-pinned code graph (``codebase.CodeIndex``).
3. **History -> tests.** If earlier Regression Suite Agent runs recorded test
   outcomes, a test's past failure rate raises its risk. In BR-Bench (RQ1, k=10,
   n=576) historical failure frequency recalled 0.517 of failing tests on
   average, against 0.051 for co-change, so history is weighted above co-change,
   which is reported only as a weak hint.

Outputs ``impact.md`` (the document) and ``impact.json`` (what the other agents read).
"""

from __future__ import annotations

import json
import math
from collections import Counter
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from src.agents import gitops
from src.agents.codebase import CodeIndex, build_index, is_test_path, tokens
from src.agents.llm import LLMError, OfflineLLM, get_llm

MAX_SEEDS = 4
SEED_RATIO = 0.45


@dataclass
class ImpactedFile:
    """A source file the change will touch (``change``) or that depends on one (``dependent``)."""

    path: str
    role: str
    score: float
    reasons: list[str] = field(default_factory=list)


@dataclass
class ImpactedTest:
    """A test at risk, with why."""

    test_id: str
    file: str
    distance: int
    score: float
    reasons: list[str] = field(default_factory=list)


@dataclass
class ImpactAnalysis:
    """The impact analysis; ``impact.json`` is ``asdict`` of this."""

    title: str
    story: str
    repo: str
    base_branch: str
    base_sha: str
    generated_at: str
    provider: str
    interpretation: str
    acceptance_criteria: list[str]
    files: list[ImpactedFile]
    tests: list[ImpactedTest]
    unaffected_tests: list[str]
    risk: str
    risk_reasons: list[str]
    gaps: list[str]
    cochange_hints: list[dict]
    history_used: bool
    graph_stats: dict

    @property
    def change_files(self) -> list[str]:
        """Files expected to change."""
        return [f.path for f in self.files if f.role == "change"]

    @property
    def scope_files(self) -> set[str]:
        """Files a PR for this story may reasonably touch: change + dependents + their tests."""
        return {f.path for f in self.files} | {t.file for t in self.tests}

    def to_json(self) -> str:
        """Serialise."""
        return json.dumps(asdict(self), indent=2)

    @classmethod
    def load(cls, path: Path | str) -> "ImpactAnalysis":
        """Read ``impact.json``."""
        d = json.loads(Path(path).read_text(encoding="utf-8"))
        d["files"] = [ImpactedFile(**f) for f in d["files"]]
        d["tests"] = [ImpactedTest(**t) for t in d["tests"]]
        return cls(**d)

    def to_markdown(self) -> str:
        """The human-readable impact analysis document."""
        L: list[str] = [f"# Impact Analysis: {self.title}", ""]
        L += ["| | |", "|---|---|",
              f"| Repository | `{self.repo}` |",
              f"| Base | `{self.base_branch}` @ `{self.base_sha[:12]}` |",
              f"| Generated | {self.generated_at} by the BlastRadius Impact Analysis Agent ({self.provider}) |",
              f"| Risk | **{self.risk.upper()}** |",
              f"| Scope | {len(self.change_files)} file(s) to change, "
              f"{sum(1 for f in self.files if f.role == 'dependent')} dependent, "
              f"{len(self.tests)} test(s) at risk, {len(self.unaffected_tests)} unaffected |", ""]
        L += ["## 1. User story", "", f"> {self.story}", ""]
        L += ["## 2. Interpretation", "", self.interpretation, ""]
        if self.acceptance_criteria:
            L += ["**Acceptance criteria**", ""] + [f"- {c}" for c in self.acceptance_criteria] + [""]
        L += ["## 3. Components to change", "", "| File | Score | Why |", "|---|---:|---|"]
        L += [f"| `{f.path}` | {f.score:.2f} | {'; '.join(f.reasons)} |" for f in self.files if f.role == "change"]
        dependents = [f for f in self.files if f.role == "dependent"]
        L += ["", "## 4. Dependent components", ""]
        if dependents:
            L += ["| File | Why |", "|---|---|"] + [f"| `{f.path}` | {'; '.join(f.reasons)} |" for f in dependents]
        else:
            L += ["None: no other source file depends on the files above."]
        L += ["", "## 5. Tests at risk (ranked)", "", "| # | Test | Graph distance | Risk score | Why |", "|---:|---|---:|---:|---|"]
        L += [f"| {i} | `{t.test_id}` | {t.distance} | {t.score:.2f} | {'; '.join(t.reasons)} |" for i, t in enumerate(self.tests, 1)]
        L += ["", "## 6. Tests not affected", ""]
        by_file = Counter(t.split("::")[0] if "::" in t else t.split("#")[0] for t in self.unaffected_tests)
        L += [f"- `{f}`: {n} test(s)" for f, n in sorted(by_file.items())] or ["- none"]
        L += ["", "## 7. Recommended regression scope", "",
              f"Run the {len(self.tests)} test(s) in section 5 on every PR for this story "
              f"({len(self.tests)} of {len(self.tests) + len(self.unaffected_tests)} tests); "
              "run the full suite in the build before deploy.", ""]
        L += ["## 8. Risks and gaps", ""]
        L += [f"- {r}" for r in self.risk_reasons]
        L += [f"- Gap: {g}" for g in self.gaps]
        if self.cochange_hints:
            L += ["- Co-change hints (weak signal; in BR-Bench co-change recalled 0.051 of failing tests at k=10):"]
            L += [f"  - `{h['file']}` changed together with `{h['partner']}` in {h['count']} commit(s)" for h in self.cochange_hints]
        L += ["", "## 9. Method", "",
              f"- Code graph at `{self.base_sha[:12]}`: {self.graph_stats.get('nodes')} nodes, {self.graph_stats.get('edges')} edges, "
              f"{self.graph_stats.get('files_parsed')} files parsed, {self.graph_stats.get('parse_failures')} parse failures "
              f"(BlastRadius graph layer, Graphify `{str(self.graph_stats.get('graphify_commit', ''))[:12]}`).",
              "- Tests at risk = tests that reach a changed file along calls/imports/uses/tests edges (reverse reachability).",
              "- Risk score = 0.55 x graph proximity + 0.15 x story terms in the test name + 0.3 x past failure rate"
              + (" (failure history from earlier regression runs)." if self.history_used else " (no failure history recorded yet, so proximity only)."),
              "- Static reachability over-approximates for direct callers and can miss dynamic dispatch and reflection; "
              "treat this as a ranked scope, not a safety guarantee.", ""]
        return "\n".join(L)


def _history(state_dir: Path) -> dict[str, tuple[int, int]]:
    """test_id -> (failures, runs) from earlier regression reports."""
    path = state_dir / "history" / "test_outcomes.jsonl"
    stats: dict[str, list[int]] = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            r = json.loads(line)
            s = stats.setdefault(r["test_id"], [0, 0])
            s[0] += r["outcome"] in ("failed", "error")
            s[1] += 1
    return {k: (v[0], v[1]) for k, v in stats.items()}


def _cochange(repo: Path, files: list[str], max_commits: int = 300) -> list[dict]:
    """Partners that changed together with ``files`` in at least two recent commits."""
    log = gitops.git(repo, "log", f"-n{max_commits}", "--name-only", "--format=@@%H", check=False)
    commits = [set(c.strip().splitlines()[1:]) for c in log.split("@@") if c.strip()]
    hints = []
    for f in files:
        partners = Counter(p for c in commits if f in c for p in c if p != f)
        hints += [{"file": f, "partner": p, "count": n} for p, n in partners.most_common(3) if n >= 2]
    return hints


def _llm_refine(llm, story: str, index: CodeIndex, ranked: list[tuple[str, float, list[str]]]) -> dict | None:
    candidates = []
    for path, _, _ in ranked[:10]:
        text = (index.repo / path).read_text(encoding="utf-8", errors="replace")
        candidates.append(f"### {path}\n{text[:2500]}")
    prompt = (
        f"User story:\n{story}\n\nRepository source files (most relevant first):\n\n" + "\n\n".join(candidates)
        + "\n\nAll source files: " + ", ".join(index.source_files)
        + '\n\nReturn JSON: {"title": short title, "interpretation": 2-4 sentences on what must change, '
          '"acceptance_criteria": [testable statements], "files": [{"path": file that must change, "reason": why}], '
          '"risks": [short risk statements]}. Only list files from the list above.'
    )
    try:
        return llm.complete_json("You are a senior engineer writing an impact analysis for a change request.", prompt)
    except LLMError:
        return None


class ImpactAnalysisAgent:
    """User story + codebase -> impact analysis document."""

    def __init__(self, provider: str | None = None) -> None:
        self.llm = get_llm(provider)

    def run(self, story: str, repo: Path | str, state_dir: Path | str | None = None, title: str | None = None) -> tuple[ImpactAnalysis, Path]:
        """Analyse ``story`` against ``repo`` at HEAD.

        Returns:
            The analysis and the directory holding ``impact.md`` / ``impact.json``.
        """
        repo = Path(repo).resolve()
        state = Path(state_dir) if state_dir else repo / ".blastradius"
        gitops.exclude_state_dir(repo)
        index = build_index(repo, state)
        story_terms = Counter(tokens(story))
        idf = index.idf()

        ranked: list[tuple[str, float, list[str]]] = []
        for f in index.source_files:
            ft = index.file_tokens.get(f, Counter())
            hits = {t: ft[t] for t in story_terms if ft.get(t)}
            score = sum(idf.get(t, 0) * (1 + math.log(c)) for t, c in hits.items())
            if score > 0:
                top = sorted(hits, key=lambda t: -idf.get(t, 0) * hits[t])[:5]
                ranked.append((f, score, [f"matches story terms: {', '.join(top)}"]))
        ranked.sort(key=lambda r: (-r[1], r[0]))
        best = ranked[0][1] if ranked else 1.0
        seeds = {p: (s / best, why) for p, s, why in ranked[:MAX_SEEDS] if s >= SEED_RATIO * best}

        interpretation = (
            "No language model is configured, so this interpretation is keyword-based: the story's terms "
            f"({', '.join(_keywords(story))}) were matched against identifiers, paths, docstrings and comments, "
            "and the matched files were expanded through the code graph."
        )
        criteria: list[str] = []
        llm_risks: list[str] = []
        provider = self.llm.name
        if not isinstance(self.llm, OfflineLLM):
            refined = _llm_refine(self.llm, story, index, ranked)
            if refined:
                title = title or refined.get("title")
                interpretation = refined.get("interpretation", interpretation)
                criteria = [str(c) for c in refined.get("acceptance_criteria", [])]
                llm_risks = [str(r) for r in refined.get("risks", [])]
                for item in refined.get("files", []):
                    p = item.get("path")
                    if p in index.source_files:
                        score, why = seeds.get(p, (0.5, []))
                        seeds[p] = (max(score, 0.5), [*why, f"model: {item.get('reason', '')}".strip()])
            else:
                provider += " (model call failed; keyword fallback used)"

        seed_nodes = [n for p in seeds for n in index.file_nodes.get(p, [])]
        reach = index.reverse_reach(seed_nodes)
        reach_by_seed = {p: index.reverse_reach(index.file_nodes.get(p, [])) for p in seeds}

        files = [ImpactedFile(p, "change", round(s, 3), why) for p, (s, why) in sorted(seeds.items(), key=lambda kv: -kv[1][0])]
        dep_files: dict[str, int] = {}
        for node, d in reach.items():
            sf = index.graph.nodes[node].get("source_file")
            if sf and sf not in seeds and not is_test_path(sf) and sf.endswith((".py", ".java")) and d > 0:
                dep_files[sf] = min(d, dep_files.get(sf, 99))
        files += [ImpactedFile(p, "dependent", round(1 / (1 + d), 3), [f"depends on a changed file ({d} hop(s) in the code graph)"])
                  for p, d in sorted(dep_files.items(), key=lambda kv: (kv[1], kv[0]))]

        history = _history(state)
        tests: list[ImpactedTest] = []
        for tid, tc in index.tests.items():
            if tc.node not in reach:
                continue
            d = reach[tc.node]
            fails, runs = history.get(tid, (0, 0))
            rate = fails / runs if runs else 0.0
            name_terms = set(tokens(tc.name))
            lex = len(name_terms & set(story_terms)) / len(name_terms) if name_terms else 0.0
            score = 0.55 * (1 / (1 + d)) + 0.15 * lex + 0.3 * rate
            reached = sorted(p for p, r in reach_by_seed.items() if tc.node in r)
            why = [f"reaches {', '.join(f'`{r}`' for r in reached[:2]) or 'a changed file'} in {d} hop(s)"]
            if lex:
                why.append(f"test name mentions {', '.join(sorted(name_terms & set(story_terms)))}")
            if runs:
                why.append(f"failed {fails}/{runs} past runs")
            tests.append(ImpactedTest(tid, tc.file, d, round(score, 3), why))
        tests.sort(key=lambda t: (-t.score, t.test_id))
        unaffected = [tid for tid in index.tests if tid not in {t.test_id for t in tests}]

        gaps = []
        for p, r in reach_by_seed.items():
            if not any(index.tests[t.test_id].node in r for t in tests):
                gaps.append(f"no test reaches `{p}`; add tests for the new behaviour")
        n_change, n_dep = len(seeds), len(dep_files)
        risk_reasons = [f"{n_change} file(s) to change, {n_dep} dependent file(s), {len(tests)} test(s) at risk"]
        total_tests = len(tests) + len(unaffected)
        share = len(tests) / total_tests if total_tests else 0.0
        if total_tests:
            risk_reasons.append(f"{len(tests)}/{total_tests} tests ({share:.0%}) reach a changed file")
        if n_change + n_dep >= 5 or gaps or share >= 0.5:
            risk = "high"
        elif n_change <= 1 and n_dep == 0 and share < 0.2:
            risk = "low"
        else:
            risk = "medium"
        risk_reasons += llm_risks

        base_branch = gitops.current_branch(repo)
        analysis = ImpactAnalysis(
            title=title or " ".join(story.split()[:10]).rstrip(".,"),
            story=story.strip(), repo=repo.name, base_branch=base_branch, base_sha=index.sha,
            generated_at=datetime.now(timezone.utc).isoformat(timespec="seconds"), provider=provider,
            interpretation=interpretation, acceptance_criteria=criteria, files=files, tests=tests,
            unaffected_tests=unaffected, risk=risk, risk_reasons=risk_reasons, gaps=gaps,
            cochange_hints=_cochange(repo, list(seeds)), history_used=bool(history), graph_stats=index.stats,
        )
        out = state / "impact" / index.sha[:12]
        out.mkdir(parents=True, exist_ok=True)
        (out / "impact.json").write_text(analysis.to_json(), encoding="utf-8")
        (out / "impact.md").write_text(analysis.to_markdown(), encoding="utf-8")
        return analysis, out


def _keywords(story: str) -> list[str]:
    """Distinct story words that survive the stopword filter, in order of appearance."""
    import re

    from src.agents.codebase import STOPWORDS

    seen: list[str] = []
    for w in re.findall(r"[A-Za-z][A-Za-z0-9]*", story):
        if len(w) > 1 and w.lower() not in STOPWORDS and w.lower() not in {x.lower() for x in seen}:
            seen.append(w)
    return seen[:14]
