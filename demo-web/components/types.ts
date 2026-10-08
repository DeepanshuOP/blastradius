export type Rate = { n: number; d: number; text: string };

export type IndexEntry = {
  id: string;
  repo: string;
  pr_number: number;
  run_id: number;
  failure_class: string;
  test_count: number;
  selected_test: string;
};

export type IndexDoc = {
  generated_at_git_sha: string;
  default: string;
  instances: IndexEntry[];
  selection: string[];
};

export type GraphNode = { id: string; label: string; file: string | null; kind: string };
export type GraphEdge = { source: string; target: string; relation: string; direction: string };
export type GraphPath = { changed_file: string; hops: number; nodes: GraphNode[]; edges: GraphEdge[] };

export type BlastNode = {
  id: string; label: string; path: string | null; kind: string; hop: number | null; in_graph: boolean;
  changed: boolean; actual_failing: boolean; cochange_pred: boolean; history_pred: boolean;
};
export type BlastDoc = {
  nodes: BlastNode[];
  edges: { source: string; target: string }[];
  max_hops: number;
  caps: { nodes: number; edges: number };
  truncated: { nodes: boolean; edges: boolean };
  within_hops_total: number;
  note: string;
};

export type InstanceDoc = {
  id: string;
  generated_at_git_sha: string;
  stages: {
    change: {
      repo: string;
      pr_number: number;
      run_id: number;
      workflow_name: string;
      language: string;
      head_sha: string;
      base_sha: string;
      base_status: string;
      changed_files: { path: string; status: string; additions: number; deletions: number }[];
    };
    raw_log: { job_id: number; test_name_token: string; lines: { text: string; failing: boolean }[] };
    parsed_outcome: {
      raw_log_line: string;
      test_id: string;
      status: string;
      harness: string;
      parser_confidence: number;
      is_fqcn_qualified: boolean;
      params: string | null;
      failure_message: string;
      failure_class: string;
      failure_rule: string;
    };
    head_vs_base: {
      base_run_id: number | null;
      base_run_distance: number | null;
      base_run_conclusion: string | null;
      tests: { test_id: string; head: string; base: string }[];
    };
    verdict: {
      t_head_fail: string[];
      t_base_fail: string[];
      flaky: string[];
      t_reveal: string[];
      sibling_runs: number;
      selected_test: string;
      selected_is_fault_revealing: boolean;
      agrees_with_outcomes_parquet: boolean;
      recorded_strict: number;
    };
    binding: {
      selected: { test_id: string; resolved_path: string | null; status: string; candidates_considered: number };
      all: { test_id: string; resolved_path: string | null; status: string; candidates_considered: number }[];
      pins_file: string;
    };
    graph: {
      graph_commit: string;
      built_offline_from_local_git: boolean;
      n_nodes: number;
      n_edges: number;
      test_node: GraphNode | null;
      test_node_how: string;
      changed_distances: { file: string; node: string | null; hops: number | null; in_graph: boolean }[];
      paths: GraphPath[];
      min_distance_to_any_changed: number | null;
      distance_note: string;
      blast: BlastDoc | null;
    };
    predictions: {
      k: number;
      run_started_at: string;
      cochange: { path: string; confidence: number; hit: boolean }[];
      history: { path: string; past_failures: number; hit: boolean }[];
      actual: { path: string; caught_by_cochange: boolean; caught_by_history: boolean }[];
      metrics: {
        cochange: { precision: number; recall: number; hits: number; predicted: number };
        history: { precision: number; recall: number; hits: number; predicted: number };
        n_actual: number;
      };
    };
  };
};

export type Sourced = { source: string; source_generated_at_git_sha: string | null };

export type ResultsDoc = {
  generated_at_git_sha: string;
  rq1_k10: Sourced & {
    k: number;
    methods: {
      method: string;
      n: number;
      mean_precision: number;
      mean_recall: number;
      mean_jaccard: number;
      micro_precision: Rate;
      micro_recall: Rate;
      median_size: number;
    }[];
  };
  runs_funnel: Sourced & { stages: { stage: string; count: number; of_previous: string; source: string }[] };
  gates: Sourced & { rows: { gate: string; measured: Rate; threshold: string; verdict: string }[] };
  binding: Sourced & { rows: { measure: string; value: Rate }[] };
  leakage: Sourced & {
    audited: Rate;
    legacy_check: string;
    legacy_violations: Rate;
    current_check: string;
    current_violations: Rate;
  };
  environment_audit: Sourced & {
    labels_by_class: { class: string; labels: Rate }[];
    instances: { measure: string; value: Rate }[];
  };
};

export type OverviewDoc = {
  generated_at_git_sha: string;
  kpis: { label: string; value: number; source: string }[];
  binding: { source: string; combined: Rate; full_confidence: Rate };
  headline: Sourced & { k: number; methods: { method: string; n: number; micro_recall: Rate }[] };
};
