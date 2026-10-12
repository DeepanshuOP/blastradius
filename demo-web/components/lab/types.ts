/** Event stream of the Live Lab (`python -m src.lab`), as it arrives over SSE or from a recorded run. */
export type Stage = "meta" | "repo" | "graph" | "change" | "impact" | "tests" | "arena" | "triage" | "repair" | "validate" | "report";
export type Data = Record<string, any>; // eslint-disable-line @typescript-eslint/no-explicit-any
export type Status = "running" | "ok" | "failed" | "skipped";

export const STAGES: Stage[] = ["repo", "graph", "change", "impact", "tests", "triage", "repair", "validate", "report"];

export interface LabEvent {
  seq: number;
  ts: string;
  stage: Stage;
  type: string;
  status: Status;
  dur_ms: number;
  data: Data;
  replay?: boolean;
}

export type NodeType = "file" | "class" | "function" | "test";
export interface GNode { id: string; label: string; type: NodeType; file: string; line: number | null; community: number | null; pagerank: number; is_test_file: boolean }
export interface GEdge { id: string; source: string; target: string; type: string; relation: string; line: string }
export interface GraphDoc { nodes: GNode[]; edges: GEdge[]; counts?: { nodes: Record<string, number>; edges: Record<string, number> }; repo?: string; commit?: string; parse_failures?: number; files_considered?: number }

export interface TestResult { id: string; nodeid?: string; outcome: string; duration_s: number; message: string; index: number; t?: number }
export interface Lane { name: string; label: string; ticks: { i: number; id: string; outcome: string; ms: number }[]; total_ms: number; first_failure_position: number | null; first_failure_id: string | null; elapsed_to_first_failure_ms: number | null; basis: string; measured_wall_to_first_failure_ms?: number }
export interface TriageRow { test: string; class: "mine" | "inherited" | "flaky"; confidence: number; reason: string; head_outcome?: string; base_outcome?: string; message?: string }
export interface Check { attempt: number; name: string; status: Status; ok: boolean | null; evidence: string }

export interface LabState {
  mode: "idle" | "live" | "replay";
  running: boolean;
  error: string | null;
  events: LabEvent[];
  header: Data | null;
  stage: Record<string, { status: Status; dur_ms: number }>;
  repo: Data | null;
  graph: (GraphDoc & { graph_id?: string; truncated?: boolean; n_nodes?: number; n_edges?: number; reason?: string; streamed_nodes?: number }) | null;
  change: Data | null;
  impact: { ranking: Data | null; paths: Data | null }; // eslint-disable-line @typescript-eslint/no-explicit-any
  tests: { started: boolean; results: TestResult[]; done: Data | null; race: { lanes: Lane[]; order_respected: boolean; order_note: string; unit: string } | null }; // eslint-disable-line @typescript-eslint/no-explicit-any
  triage: { rows: TriageRow[]; counts: Record<string, number>; model?: string; failing_cases?: number; unit?: string; skipped?: string } | null;
  repair: {
    chunks: Data[]; requests: Data[]; replies: Data[]; blocks: Data[];
    patch: Data | null; skipped: string | null; unavailable: { kind: string; reason: string } | null; // eslint-disable-line @typescript-eslint/no-explicit-any
  };
  validate: { checks: Check[]; verdict: Data | null }; // eslint-disable-line @typescript-eslint/no-explicit-any
  report: { comment: string | null; summary: Data | null }; // eslint-disable-line @typescript-eslint/no-explicit-any
  tokens: { prompt: number; completion: number; total: number; cached: number; calls: number };
  startedAt: number | null;
  elapsedMs: number;
}
