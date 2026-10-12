import type { GEdge, GNode } from "./types";

/** For every node, how many test functions reach it along the graph's directed edges (a test calls, imports or
 * contains its way to it). A test counts itself. Used for node size, the labels and the hover tooltip. */
export function reachCounts(nodes: GNode[], edges: GEdge[]): { count: Record<string, number>; max: number; tests: number } {
  const out = new Map<string, string[]>();
  edges.forEach((e) => { (out.get(e.source) ?? out.set(e.source, []).get(e.source)!).push(e.target); });
  let tests = nodes.filter((n) => n.type === "test").map((n) => n.id);
  if (tests.length === 0) tests = nodes.filter((n) => n.type === "function" && n.is_test_file).map((n) => n.id);
  const count: Record<string, number> = {};
  for (const t of tests) {
    const seen = new Set<string>([t]);
    const q = [t];
    while (q.length) {
      const cur = q.pop()!;
      for (const nb of out.get(cur) ?? []) if (!seen.has(nb)) { seen.add(nb); q.push(nb); }
    }
    seen.forEach((id) => { count[id] = (count[id] ?? 0) + 1; });
  }
  return { count, max: Math.max(1, ...Object.values(count)), tests: tests.length };
}

/** Node sizes in 0..1 (square-root scale of the reach count; unreached nodes stay small). */
export function sizeByReach(r: { count: Record<string, number>; max: number }, nodes: GNode[]): Record<string, number> {
  const out: Record<string, number> = {};
  nodes.forEach((n) => { out[n.id] = Math.sqrt((r.count[n.id] ?? 0) / r.max); });
  return out;
}

/** The nodes that earn a label: the most-reached functions and classes of the source files. */
export function importantNodes(nodes: GNode[], r: { count: Record<string, number> }, k = 6): string[] {
  return nodes.filter((n) => (n.type === "function" || n.type === "class") && !n.is_test_file && (r.count[n.id] ?? 0) > 0)
    .sort((a, b) => (r.count[b.id] ?? 0) - (r.count[a.id] ?? 0) || a.id.localeCompare(b.id)).slice(0, k).map((n) => n.id);
}
