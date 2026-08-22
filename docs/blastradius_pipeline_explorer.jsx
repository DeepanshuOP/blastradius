import React, { useState } from "react";

/* ------------------------------------------------------------------ */
/*  BlastRadius — Pipeline Explorer                                    */
/*  Click a stage to see its files. Click a file to see what it does.  */
/* ------------------------------------------------------------------ */

const STAGES = [
  {
    id: "frame",
    num: "01",
    name: "Frame",
    verb: "choose what to study",
    status: "done",
    volumeIn: "3,671",
    volumeInLabel: "candidate repos",
    volumeOut: "300",
    volumeOutLabel: "frozen frame",
    summary:
      "Turn all of GitHub into a defensible sample of 300 repositories, chosen by written-down rules so a reviewer can check we did not cherry-pick.",
    handoff:
      "Writes data/frame/frame_v1.csv — 300 rows, sha-pinned. The harvest daemon reads this file and nothing else to decide where to go.",
    files: [
      {
        path: "scripts/merge_frame.py",
        role: "Merge the two SEART exports",
        status: "done",
        does:
          "SEART is queried once for Java and once for Python, producing two CSV exports. This merges them into one candidate list and prints a stage-0 attrition report.",
        pieces: ["Reads seart_a.csv (1,123 Java) and seart_b.csv (2,548 Python)", "Writes repos_raw.csv (3,671)"],
        input: "data/frame/seart_a.csv, seart_b.csv",
        output: "data/frame/repos_raw.csv",
        why:
          "SEART only gives lifetime statistics, so it cannot filter on recent activity. Everything after this point has to be measured against the live API.",
        tests: null,
      },
      {
        path: "src/harvest/frame.py",
        role: "Apply the liveness and test-intent filters",
        status: "done",
        does:
          "Calls the GitHub API for every candidate: does it have at least 100 workflow runs in the last 90 days, and does at least one workflow look like it runs tests? Records a verdict per repository.",
        pieces: [
          "ATTRITION_COLUMNS — the verdict schema",
          "_write_attrition_csv() — one row per candidate, not just counts",
          "Verdicts: kept / no_ci / no_test_workflow / api_error",
        ],
        input: "data/frame/repos_raw.csv",
        output: "data/frame/attrition_stage.csv (3,671 verdicts), repos.csv (2,333 survivors)",
        why:
          "Recording a verdict per repository rather than a count turns a claim into evidence. When we regenerated the funnel four days later, all four cross-checks reconciled exactly — because the raw verdicts were still there.",
        tests: 11,
      },
      {
        path: "scripts/sample_frame.py",
        role: "Draw the stratified sample",
        status: "done",
        does:
          "Takes a language-stratified random draw of 150 Java + 150 Python under a fixed seed, and puts the other 2,033 survivors in a reserve pool.",
        pieces: [
          "Seed 20261110 — fixed, so the draw is reproducible",
          "build_attrition() — writes the funnel object",
          "Reserve pool for later frame widening",
        ],
        input: "data/frame/repos.csv, attrition_stage.csv",
        output: "frame_v1.csv (300), frame_v1_reserve.csv (2,033), ATTRITION.json",
        why:
          "300 rather than 60 because attrition compounds. We have already watched 3,671 become 300, and four more filters follow. The realistic survival estimate is 60–100 usable repos, so starting at 60 would leave us with 8.",
        tests: 9,
      },
      {
        path: "analysis/attrition_funnel.py",
        role: "Regenerate the funnel table",
        status: "done",
        does:
          "Reads only the frozen frame files and emits the eight-stage attrition table with a Java/Python split. Stages 4–7 print 'not yet measured' and never an estimate.",
        pieces: [
          "Four internal cross-checks, all currently exact",
          "Byte-identical across runs — its inputs are frozen",
        ],
        input: "data/frame/*.csv, ATTRITION.json",
        output: "paper/generated/attrition_funnel.md",
        why:
          "Every number in the paper has to be regenerable by a script. A table typed by hand cannot go in the paper, because nobody can check it.",
        tests: null,
      },
    ],
  },
  {
    id: "harvest",
    num: "02",
    name: "Harvest",
    verb: "download the evidence",
    status: "running",
    volumeIn: "300",
    volumeInLabel: "repos to sweep",
    volumeOut: "63,170",
    volumeOutLabel: "workflow runs captured",
    summary:
      "Walk every pull request in the frame, then every commit, then every CI run, then every job — and store the raw API responses byte for byte without ever parsing them.",
    handoff:
      "Writes gzipped JSONL into data/raw/. Nothing downstream exists yet, so this data is currently sitting on disk waiting for the parsers.",
    files: [
      {
        path: "src/harvest/ratelimit.py",
        role: "The traffic controller",
        status: "done",
        does:
          "Manages three GitHub credentials, rotates between them by remaining quota, retries transient failures with escalating back-off, and logs every single request to a forensic file.",
        pieces: [
          "TokenPool — round-robin over three PATs, evicts on 401",
          "get_with_backoff() — the ONLY function permitted to issue an HTTP request",
          "TransientGovernor — pauses 60s, then 300s, then 900s, then aborts cleanly",
          "TERMINAL_STATUSES = {404, 410, 451} — gone, do not retry",
        ],
        input: "A URL and a request kind",
        output: "A raw Response, plus one line in logs/requests.jsonl",
        why:
          "Rate limiting, retries, credential rotation and logging must happen on every request. If a second developer writes requests.get() anywhere else, that request bypasses all of it — and nothing fails until the whole harvest is blocked.",
        tests: 27,
        note:
          "The governor ladder ran for real at 04:38 today: the network died, it climbed 60 → 300 → 900, and shut down in an orderly way after 21 minutes instead of spinning.",
      },
      {
        path: "src/harvest/cursor.py",
        role: "The resume ledger",
        status: "done",
        does:
          "A SQLite database recording every fetchable unit and its status. Before fetching, mark in_flight. After success, mark complete. On restart, anything complete is skipped entirely.",
        pieces: [
          "repo_cursor — per-repo position in the PR walk",
          "capture_unit — one row per fetchable thing, PK (repo, kind, unit_key)",
          "CHECK constraints on kind and status — the database refuses a typo",
          "~118,000 rows today, 99.99% complete",
        ],
        input: "Fetch attempts from the daemon",
        output: "data/state/cursor.db",
        why:
          "A harvest takes days and the process has died four times in 24 hours. Without this you would restart from zero and re-spend quota you cannot get back. Verified in code, not assumed: zero HTTP requests are issued for a unit already marked complete.",
        tests: 19,
      },
      {
        path: "src/harvest/rawstore.py",
        role: "The immutable archive",
        status: "done",
        does:
          "Writes each API response, wrapped in a provenance envelope, to a gzipped file. Atomic write then rename, so a crash mid-write leaves either the old file or the new one — never half.",
        pieces: [
          "Path: data/raw/<owner>__<repo>/<category>/<shard>/<id>/<kind>.jsonl.gz",
          "Envelope: url, status, fetched_at, etag, encoding, body",
          "_encode_body() — utf8 with a base64 fallback for binary",
          "KIND_SCOPE — which kinds are scoped to a job, a run, a SHA",
        ],
        input: "Raw response bytes",
        output: "data/raw/ — 118,000 files, 1.08 GB on disk",
        why:
          "Never parse at capture time. If a parser has a bug, we fix the parser and re-parse. If we had parsed on the way in, a parser bug would mean re-downloading — and by then the logs are gone.",
        tests: 24,
        note:
          "Measured quirk: 189.8 MB of actual bytes occupies 1.08 GB on disk — a 5.83× ratio, because 118,000 files averaging under 2 KB sit in 4 KB blocks. The dashboard reports both, labelled.",
      },
      {
        path: "src/harvest/daemon.py",
        role: "The orchestrator",
        status: "running",
        does:
          "The loop that actually harvests. For each repo: sweep pull requests (stage 1), discover runs and jobs per commit (stage 2), capture check runs and annotations (stage 3).",
        pieces: [
          "sweep_repo() — pages through PRs, stops at the window edge",
          "discover_repo() — runs per SHA, then jobs per run",
          "capture_checkruns() — skips the annotation fetch when the count is exactly 0",
          "_fetch_job_log() — built but not yet wired into a loop",
          "Conservation counters — six mutually exclusive paths must sum to the total",
        ],
        input: "data/frame/frame_v1.csv",
        output: "Everything under data/raw/, and rows in cursor.db",
        why:
          "The conservation counters are the part worth pointing at. After every loop it checks that every item seen was accounted for by exactly one path. Non-zero prints one stderr line and never raises — a counting bug must not kill a multi-hour harvest.",
        tests: 59,
        note:
          "Known defect, filed not fixed: --dry-run is stage-agnostic, so --stage 1 and --stage both produce byte-identical output.",
      },
      {
        path: "run_supervised.sh",
        role: "Keep it alive",
        status: "done",
        does: "Restarts the daemon 120 seconds after any exit.",
        pieces: ["Eight lines of bash", "Written after the fourth death in 24 hours"],
        input: "—",
        output: "logs/supervisor_*.log",
        why:
          "Four interruptions in a day: an expired credential, a GitHub API incident, two network drops. Every one was absorbed without data loss, which is the resume design working. What was missing was anyone noticing for hours.",
        tests: null,
      },
    ],
  },
  {
    id: "parse",
    num: "03",
    name: "Parse",
    verb: "read the verdicts",
    status: "partial",
    volumeIn: "0",
    volumeInLabel: "job logs captured",
    volumeOut: "0",
    volumeOutLabel: "test verdicts",
    summary:
      "Turn raw CI output into one canonical record per test: which test, what verdict. Four different tools describe the same event four different ways, and all four must normalise to one identical string.",
    handoff:
      "Will write outcomes.parquet. The join key is already built and green; the parsers that feed it are not.",
    files: [
      {
        path: "src/parse/test_ids.py",
        role: "The join key",
        status: "done",
        does:
          "Takes any raw test reference — Surefire XML, a Maven error line, a Gradle line, a pytest line, a check annotation — and produces one canonical identifier. Returns None for anything it cannot parse.",
        pieces: [
          "Java form: com.example.FooTest#testBar",
          "Python form: tests/test_foo.py::TestFoo::test_bar",
          "Strips ANSI codes, ISO timestamps, parameterisation, Windows separators",
          "derive_node_id() — the lossy internal key for graph binding",
        ],
        input: "A raw string from any of six sources",
        output: "A frozen TestId, or None",
        why:
          "This is the single blocking dependency in the whole project. Parsers and graph nodes must agree on one exact string or nothing joins and every downstream number is silently wrong.",
        tests: 50,
        note:
          "Two decisions worth defending: identifiers are never casefolded, because Java is case-sensitive and a merged key does not raise an error — it looks like a successful join. And a prose annotation title returns None rather than a fabricated method name.",
      },
      {
        path: "src/parse/junit_xml.py",
        role: "Surefire and pytest XML",
        status: "todo",
        does: "Will read structured test report XML — the cleanest label source available.",
        pieces: ["<testcase classname= name=> extraction", "Feeds normalize_test_id()"],
        input: "Artifacts captured from CI runs",
        output: "Canonical outcome records",
        why:
          "Now the top parser priority, because the annotation census proved annotations carry almost no test identity.",
        tests: null,
      },
      {
        path: "src/parse/log_*.py",
        role: "Console log parsers",
        status: "todo",
        does: "Will read Maven, Gradle and pytest console output from job logs.",
        pieces: ["One parser per output family", "Per-parser coverage and precision, reported every run"],
        input: "Job logs — the artefact that expires in 90 days",
        output: "Canonical outcome records",
        why:
          "Job logs are the only artefact that records which individual test failed, and they are the tier on the clock.",
        tests: null,
      },
    ],
  },
  {
    id: "label",
    num: "04",
    name: "Label",
    verb: "work out what broke",
    status: "todo",
    volumeIn: "0",
    volumeInLabel: "verdicts",
    volumeOut: "0",
    volumeOutLabel: "labelled instances",
    summary:
      "The heart of the method. Tests failing at the head commit, minus tests failing at the base commit, minus flaky tests, equals the set of tests this change actually broke.",
    handoff: "Will write instances.parquet — the rows that make up BR-Bench.",
    files: [
      {
        path: "src/label/engine.py",
        role: "The subtraction",
        status: "todo",
        does:
          "For each instance: collect failures at head, resolve the base run by walking up to ten ancestor commits, collect failures at base, subtract, filter flakiness, emit labels with provenance.",
        pieces: [
          "base_run_distance — how far back we had to walk",
          "Same-SHA flip detection — a test that passes and fails on identical code is flaky by definition",
          "Matrix builds union across legs, with the leg count recorded",
        ],
        input: "outcomes.parquet",
        output: "instances.parquet",
        why:
          "The subtraction is what makes the label causal rather than correlational. A test failing at both commits was already broken and proves nothing about this change.",
        tests: null,
        note:
          "The most dangerous bug in the project lives here. If no base run resolves, the engine must emit NO labels. Reading 'no base failures found' as 'the base was green' would manufacture false positives at industrial scale. There is an explicit no_base path that emits nothing.",
      },
    ],
  },
  {
    id: "graph",
    num: "05",
    name: "Graph",
    verb: "map the code",
    status: "todo",
    volumeIn: "0",
    volumeInLabel: "instances",
    volumeOut: "0",
    volumeOutLabel: "commit-pinned graphs",
    summary:
      "Build a method-level dependency graph of each repository, pinned to the base commit of each instance, without needing the code to compile.",
    handoff: "Will write graph_nodes.parquet and graph_edges.parquet, and bind test nodes to test_ids.",
    files: [
      {
        path: "vendor/graphify-br/",
        role: "The third-party graph tool",
        status: "vendored",
        does:
          "Cloned, read, not yet used. Provides tree-sitter based extraction and the node-ID recipe our binding key has to match.",
        pieces: [
          "ids.normalize_id() — NFKC, casefold, non-word to underscore",
          "Java method nodes carry the simple method name, no parameter signature",
        ],
        input: "A repository at a commit",
        output: "Graph nodes and edges",
        why:
          "Reading it settled a real question: graphify's node IDs are casefolded and lossy, so they cannot be our published key. That is why we now carry two keys — recorded as decision D-25.",
        tests: null,
      },
      {
        path: "src/graph/build.py",
        role: "Commit-pinned graph construction",
        status: "todo",
        does:
          "Will build a typed graph per instance base commit using tree-sitter, incrementally against the nearest already-built ancestor via Git worktrees.",
        pieces: [
          "Nodes: repo, module, package, file, class, method, function, test, dependency",
          "Edges: contains, imports, calls, extends, implements, tests, co-changed-with",
        ],
        input: "A repository at a base SHA",
        output: "graph_nodes.parquet, graph_edges.parquet",
        why:
          "Tree-sitter rather than a compiler because you cannot reliably build a repository at an arbitrary historical commit — dependencies moved, the build tool changed, the JDK is different. Less precise, but it works on every commit instead of maybe a third of them.",
        tests: null,
      },
    ],
  },
  {
    id: "measure",
    num: "06",
    name: "Measure",
    verb: "answer the question",
    status: "todo",
    volumeIn: "0",
    volumeInLabel: "graphs + labels",
    volumeOut: "—",
    volumeOutLabel: "the paper",
    summary:
      "Compute the two proxy sets, measure how far each diverges from what actually failed, and report it with proper statistics. This is the contribution.",
    handoff: "Writes the tables that go in the MSR 2027 submission.",
    files: [
      {
        path: "analysis/divergence.py",
        role: "RQ1 — the headline",
        status: "todo",
        does:
          "For each instance computes C (co-change), R (reachability) and F (what actually failed), then measures the distance between them.",
        pieces: [
          "Pairwise Jaccard, precision, recall, symmetric difference",
          "Wilcoxon signed-rank, Holm–Bonferroni, Cliff's delta",
          "Per-repository random effects so no single repo drives the result",
        ],
        input: "instances.parquet, graph_*.parquet, cochange.parquet",
        output: "The paper's central table",
        why:
          "This is the whole project. Everything upstream is scaffolding for this one measurement, and it is publishable whether or not any model works.",
        tests: null,
      },
      {
        path: "src/model/",
        role: "The demonstration",
        status: "todo",
        does: "A graph-based predictor trained on execution outcomes, compared against nine baselines.",
        pieces: [
          "Baselines: retest-all, random, path similarity, k-hop reachability, Ekstazi, historical failure frequency, co-change rules, and two graphify heuristics",
          "Leakage audit: trailing windows cut at each instance's own run start",
        ],
        input: "instances.parquet + graph features",
        output: "A ranking of tests by likelihood of failing",
        why:
          "Explicitly not the contribution. If it loses to historical failure frequency we report that, and the measurement still stands. Claiming the model would mean a weak model sinks the paper.",
        tests: null,
      },
    ],
  },
];

const SUPPORT = {
  id: "support",
  num: "—",
  name: "Instruments",
  verb: "watch the machine",
  status: "done",
  volumeIn: "—",
  volumeInLabel: "",
  volumeOut: "202",
  volumeOutLabel: "tests passing",
  summary:
    "Not part of the pipeline — the instruments that let us see it. Both of the project's real findings came from here rather than from reading code.",
  handoff: "Everything published traces back through these.",
  files: [
    {
      path: "dashboard.py",
      role: "The live monitor",
      status: "done",
      does:
        "A Streamlit app with eight panels: headline counts, frame progress by language, units by kind and status, capture timeline, per-repo table, zero-yield repos, storage, and a Phase 1 placeholder.",
      pieces: [
        "Reads only cursor.db and frame_v1.csv",
        "Never decompresses a capture file",
        "Everything cached with a 30-second TTL",
      ],
      input: "cursor.db (read-only), frame_v1.csv",
      output: "A page at localhost:8501",
      why:
        "It is Figure 1 of the paper, it is the live demo, and it is how you notice the harvest went wrong before losing a day.",
      tests: null,
    },
    {
      path: "analysis/expiry_cliff.py",
      role: "The clock",
      status: "done",
      does:
        "Parses every captured run, computes its age, and buckets failed runs by how much log lifetime is left.",
      pieces: [
        "1,517 of 5,119 failed runs already expired (29.6%)",
        "3,602 still recoverable",
        "1,238 expiring within 30 days",
      ],
      input: "data/raw/**/runs.jsonl.gz",
      output: "paper/generated/expiry_cliff.md",
      why:
        "This produces the number that orders the entire build schedule: the corpus loses about 41 recoverable failed runs every day that log capture is delayed.",
      tests: null,
    },
    {
      path: "analysis/annotation_census.py",
      role: "The assumption killer",
      status: "done",
      does:
        "Takes a stratified random sample of captured annotation files under a fixed seed and measures what annotations actually contain.",
      pieces: [
        "1,500 of 16,240 files, 9.24%",
        "1,103 of 1,106 annotations have no title (99.73%)",
        "0 of 1,106 carry both a test path and a usable title",
      ],
      input: "data/raw/**/annotations.jsonl.gz",
      output: "paper/generated/annotation_census.md",
      why:
        "We assumed annotations would be our best label source. This measured that assumption and refuted it, and the parser roadmap was reordered as a result. Recorded as decision D-24.",
      tests: null,
    },
    {
      path: "analysis/corpus_stats.py",
      role: "The scoreboard",
      status: "done",
      does:
        "Reports harvest state, storage as two separately labelled quantities, the Phase 0 exit criteria scored honestly, and the most active repositories.",
      pieces: ["37 of 300 repos", "1 of 5 exit criteria met, 1 partial, 3 not met"],
      input: "cursor.db, data/raw/, frame_v1.csv",
      output: "paper/generated/corpus_stats.md",
      why:
        "Scoring ourselves against a bar we set weeks earlier is what makes the rest of the numbers believable.",
      tests: null,
    },
    {
      path: "tests/",
      role: "202 tests against real fixtures",
      status: "done",
      does: "Every data-touching function is tested against a real captured response, never a mock.",
      pieces: [
        "test_daemon 59 · test_test_ids 50 · test_rawstore 24",
        "test_ratelimit 22 · test_cursor 19 · test_frame 11",
        "test_sample_frame 9 · test_transient_governor 5 · test_scaffold 3",
      ],
      input: "tests/fixtures/ — real checked-in responses",
      output: "Pass or fail",
      why:
        "A mock proves your code matches your assumption about GitHub. A real captured response proves it matches GitHub. And fixture values are ground truth: if a test fails, fix the code, never the expectation.",
      tests: 202,
    },
    {
      path: "docs/DECISIONS.md",
      role: "Twenty-five decisions on the record",
      status: "done",
      does:
        "One row per decision: what was decided, the measured evidence, whether the door swings both ways, and the specific observation that would make us reconsider.",
      pieces: [
        "D-02 the contribution is the dataset, not the model",
        "D-23 capture what expires before what persists",
        "D-24 annotations demoted to fallback",
        "D-25 two keys — canonical and internal",
      ],
      input: "Arguments that would otherwise be forgotten",
      output: "A register you can audit months later",
      why:
        "Numbers are reserved and never reused. D-21 is deliberately empty, held for a decision we know is coming.",
      tests: null,
    },
  ],
};

const ALL = [...STAGES, SUPPORT];

const STATUS = {
  done: { label: "built", fg: "text-emerald-300", bg: "bg-emerald-400/10", ring: "ring-emerald-400/30", dot: "bg-emerald-400" },
  running: { label: "running now", fg: "text-amber-300", bg: "bg-amber-400/10", ring: "ring-amber-400/40", dot: "bg-amber-400" },
  partial: { label: "part built", fg: "text-sky-300", bg: "bg-sky-400/10", ring: "ring-sky-400/30", dot: "bg-sky-400" },
  todo: { label: "not started", fg: "text-slate-400", bg: "bg-slate-400/5", ring: "ring-slate-500/25", dot: "bg-slate-500" },
  vendored: { label: "vendored", fg: "text-violet-300", bg: "bg-violet-400/10", ring: "ring-violet-400/30", dot: "bg-violet-400" },
};

function Dot({ status, pulse }) {
  const s = STATUS[status] || STATUS.todo;
  return (
    <span className="relative inline-flex h-2 w-2 shrink-0">
      {pulse && <span className={`absolute inline-flex h-full w-full rounded-full ${s.dot} opacity-60 animate-ping`} />}
      <span className={`relative inline-flex h-2 w-2 rounded-full ${s.dot}`} />
    </span>
  );
}

export default function PipelineExplorer() {
  const [stageId, setStageId] = useState("harvest");
  const [fileIdx, setFileIdx] = useState(0);

  const stage = ALL.find((s) => s.id === stageId);
  const file = stage.files[Math.min(fileIdx, stage.files.length - 1)];
  const s = STATUS[stage.status];
  const fs = STATUS[file.status] || STATUS.todo;

  const pick = (id) => {
    setStageId(id);
    setFileIdx(0);
  };

  return (
    <div className="min-h-screen w-full bg-[#0C1417] text-[#E4E0D6] antialiased">
      <div className="mx-auto max-w-6xl px-5 py-8 sm:px-8">

        {/* masthead */}
        <header className="mb-8 border-b border-white/10 pb-6">
          <div className="flex flex-wrap items-baseline gap-x-4 gap-y-1">
            <h1 className="font-mono text-xl font-semibold tracking-tight text-[#E4E0D6]">
              BlastRadius
            </h1>
            <span className="font-mono text-[11px] uppercase tracking-[0.18em] text-slate-500">
              pipeline explorer
            </span>
          </div>
          <p className="mt-2 max-w-2xl text-[15px] leading-relaxed text-slate-400">
            Six stages turn all of GitHub into a dataset that says which tests a
            code change actually broke. Pick a stage, then a file, to see what it
            does and where its output goes.
          </p>
        </header>

        {/* stage rail */}
        <div className="-mx-5 mb-8 overflow-x-auto px-5 sm:mx-0 sm:px-0">
          <div className="flex min-w-max items-stretch gap-1.5 pb-2">
            {ALL.map((st, i) => {
              const active = st.id === stageId;
              const c = STATUS[st.status];
              return (
                <React.Fragment key={st.id}>
                  {i === STAGES.length && (
                    <div className="mx-2 w-px shrink-0 self-stretch bg-white/10" aria-hidden="true" />
                  )}
                  <button
                    onClick={() => pick(st.id)}
                    aria-pressed={active}
                    className={`group w-[136px] shrink-0 rounded-md px-3 py-3 text-left ring-1 transition
                      focus:outline-none focus-visible:ring-2 focus-visible:ring-amber-300
                      ${active ? `${c.bg} ${c.ring}` : "bg-white/[0.02] ring-white/10 hover:bg-white/[0.05]"}`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-mono text-[10px] tracking-[0.2em] text-slate-500">
                        {st.num}
                      </span>
                      <Dot status={st.status} pulse={st.status === "running"} />
                    </div>
                    <div className={`mt-1.5 font-mono text-[13px] font-semibold ${active ? c.fg : "text-slate-300"}`}>
                      {st.name}
                    </div>
                    <div className="mt-0.5 text-[11px] leading-tight text-slate-500">
                      {st.verb}
                    </div>
                    <div className="mt-2.5 border-t border-white/[0.07] pt-2">
                      <div className={`font-mono text-[15px] font-semibold tabular-nums ${st.volumeOut === "0" ? "text-slate-600" : c.fg}`}>
                        {st.volumeOut}
                      </div>
                      <div className="text-[10px] leading-tight text-slate-500">
                        {st.volumeOutLabel}
                      </div>
                    </div>
                  </button>
                </React.Fragment>
              );
            })}
          </div>
        </div>

        {/* stage summary */}
        <section className={`mb-6 rounded-lg px-5 py-4 ring-1 ${s.bg} ${s.ring}`}>
          <div className="flex flex-wrap items-center gap-3">
            <h2 className="font-mono text-lg font-semibold">
              <span className="text-slate-500">{stage.num}</span>{" "}
              <span className={s.fg}>{stage.name}</span>
            </h2>
            <span className={`rounded-full px-2 py-0.5 font-mono text-[10px] uppercase tracking-wider ring-1 ${s.fg} ${s.ring}`}>
              {s.label}
            </span>
          </div>
          <p className="mt-2 max-w-3xl text-[15px] leading-relaxed text-slate-300">
            {stage.summary}
          </p>
          <p className="mt-3 border-t border-white/[0.07] pt-3 text-[13px] leading-relaxed text-slate-400">
            <span className="font-mono text-[10px] uppercase tracking-[0.16em] text-slate-500">
              hands off to next stage ·{" "}
            </span>
            {stage.handoff}
          </p>
        </section>

        {/* files + detail */}
        <div className="grid gap-5 lg:grid-cols-[260px_1fr]">

          {/* file list */}
          <nav aria-label="Files in this stage" className="space-y-1">
            <div className="mb-2 font-mono text-[10px] uppercase tracking-[0.18em] text-slate-500">
              {stage.files.length} file{stage.files.length > 1 ? "s" : ""}
            </div>
            {stage.files.map((f, i) => {
              const active = i === fileIdx;
              const c = STATUS[f.status] || STATUS.todo;
              return (
                <button
                  key={f.path}
                  onClick={() => setFileIdx(i)}
                  aria-pressed={active}
                  className={`block w-full rounded px-3 py-2.5 text-left ring-1 transition
                    focus:outline-none focus-visible:ring-2 focus-visible:ring-amber-300
                    ${active ? "bg-white/[0.07] ring-white/20" : "bg-transparent ring-white/[0.06] hover:bg-white/[0.03]"}`}
                >
                  <div className="flex items-start gap-2">
                    <span className="mt-1.5"><Dot status={f.status} /></span>
                    <span className="min-w-0 flex-1">
                      <span className="block break-all font-mono text-[12px] leading-tight text-slate-200">
                        {f.path}
                      </span>
                      <span className="mt-0.5 block text-[11px] leading-tight text-slate-500">
                        {f.role}
                      </span>
                    </span>
                  </div>
                </button>
              );
            })}
          </nav>

          {/* detail */}
          <article className="rounded-lg bg-white/[0.02] p-5 ring-1 ring-white/10 sm:p-6">
            <div className="flex flex-wrap items-center gap-3">
              <h3 className="break-all font-mono text-base font-semibold text-[#E4E0D6]">
                {file.path}
              </h3>
              <span className={`rounded-full px-2 py-0.5 font-mono text-[10px] uppercase tracking-wider ring-1 ${fs.fg} ${fs.ring}`}>
                {fs.label}
              </span>
              {file.tests != null && (
                <span className="font-mono text-[11px] text-slate-500">
                  {file.tests} tests
                </span>
              )}
            </div>

            <p className="mt-3 text-[15px] leading-relaxed text-slate-200">
              {file.does}
            </p>

            {/* flow */}
            <div className="mt-5 grid gap-3 sm:grid-cols-[1fr_auto_1fr]">
              <div className="rounded border border-white/[0.08] px-3 py-2.5">
                <div className="font-mono text-[10px] uppercase tracking-[0.16em] text-slate-500">
                  takes in
                </div>
                <div className="mt-1 break-words font-mono text-[12px] leading-snug text-slate-300">
                  {file.input}
                </div>
              </div>
              <div className="hidden items-center justify-center text-slate-600 sm:flex" aria-hidden="true">
                →
              </div>
              <div className="rounded border border-white/[0.08] px-3 py-2.5">
                <div className="font-mono text-[10px] uppercase tracking-[0.16em] text-slate-500">
                  gives out
                </div>
                <div className="mt-1 break-words font-mono text-[12px] leading-snug text-slate-300">
                  {file.output}
                </div>
              </div>
            </div>

            {/* pieces */}
            <div className="mt-5">
              <div className="font-mono text-[10px] uppercase tracking-[0.16em] text-slate-500">
                what is inside
              </div>
              <ul className="mt-2 space-y-1.5">
                {file.pieces.map((p) => (
                  <li key={p} className="flex gap-2.5 text-[13px] leading-relaxed text-slate-300">
                    <span className="mt-[7px] h-px w-3 shrink-0 bg-slate-600" aria-hidden="true" />
                    <span className="font-mono">{p}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* why */}
            <div className="mt-5 border-l-2 border-amber-400/40 pl-4">
              <div className="font-mono text-[10px] uppercase tracking-[0.16em] text-amber-300/70">
                why it exists
              </div>
              <p className="mt-1.5 text-[14px] leading-relaxed text-slate-300">
                {file.why}
              </p>
            </div>

            {file.note && (
              <div className="mt-4 rounded bg-white/[0.03] px-4 py-3 ring-1 ring-white/[0.07]">
                <div className="font-mono text-[10px] uppercase tracking-[0.16em] text-slate-500">
                  worth knowing
                </div>
                <p className="mt-1.5 text-[13px] leading-relaxed text-slate-400">
                  {file.note}
                </p>
              </div>
            )}
          </article>
        </div>

        <footer className="mt-10 border-t border-white/10 pt-5">
          <p className="font-mono text-[11px] leading-relaxed text-slate-500">
            Measured 18 Aug 2026 · 37/300 repos · 63,170 runs · 207,853 jobs · 202 tests
            <br />
            Every figure regenerable with{" "}
            <span className="text-slate-400">make tables</span>. Zeros in stages 03–06 are
            real, not placeholders.
          </p>
        </footer>
      </div>
    </div>
  );
}
