/**
 * The blast-radius layout: the changed functions at the centre, every other node on a concentric ring by its hop
 * distance from the change (1, 2, 3, 4 or more), unreachable nodes on an outer ring, and nodes grouped by file inside
 * each ring. Positions are computed here and handed to cytoscape's `preset` layout, so no layout library is involved.
 *
 * Hop distance is measured on the undirected graph (impact travels both ways along an edge, as the engine's
 * `graphview.hops_from` measures it), over the graph that is on screen.
 */
import type { GEdge, GNode } from "./types";

export const MAX_RING = 4;                  // ring 4 holds "4 or more hops"
export const UNREACHABLE = MAX_RING + 1;
const TYPE_ORDER: Record<string, number> = { file: 0, class: 1, function: 2, test: 3 };
const SLOT = 20;                            // model units between neighbouring nodes on a ring
const RING_GAP = 64;                        // minimum distance between consecutive rings

export interface Ring { index: number; radius: number; label: string; count: number }
export interface RingLayout {
  positions: Record<string, { x: number; y: number }>;
  ring: Record<string, number>;             // node id -> ring index
  hops: Record<string, number | null>;      // node id -> hop distance (null: not reachable)
  rings: Ring[];
  mode: "change" | "type";                  // "type": no change yet, rings by node type
}

/** Hop distance from the nearest seed over undirected edges, unlimited (null for nodes no path reaches). */
export function hopsFrom(nodes: GNode[], edges: GEdge[], seeds: string[]): Record<string, number | null> {
  const adj = new Map<string, string[]>();
  nodes.forEach((n) => adj.set(n.id, []));
  edges.forEach((e) => {
    if (adj.has(e.source) && adj.has(e.target)) { adj.get(e.source)!.push(e.target); adj.get(e.target)!.push(e.source); }
  });
  const dist: Record<string, number | null> = {};
  nodes.forEach((n) => (dist[n.id] = null));
  const q: string[] = [];
  seeds.forEach((s) => { if (adj.has(s)) { dist[s] = 0; q.push(s); } });
  for (let i = 0; i < q.length; i++) {
    const cur = q[i];
    for (const nb of adj.get(cur) ?? []) if (dist[nb] === null) { dist[nb] = (dist[cur] as number) + 1; q.push(nb); }
  }
  return dist;
}

const byFile = (a: GNode, b: GNode) =>
  a.file.localeCompare(b.file) || (TYPE_ORDER[a.type] ?? 9) - (TYPE_ORDER[b.type] ?? 9) || (a.line ?? 0) - (b.line ?? 0) || a.id.localeCompare(b.id);

export function ringLabel(index: number, mode: "change" | "type"): string {
  if (mode === "type") return ["", "files", "classes", "functions", "tests"][index] ?? "";
  if (index === 0) return "changed";
  if (index === UNREACHABLE) return "not reachable";
  if (index === MAX_RING) return `${MAX_RING}+ hops`;
  return `${index} hop${index === 1 ? "" : "s"}`;
}

/** Compute the ring layout. With no seeds, nodes are ringed by type (files innermost, tests outermost). */
export function ringLayout(nodes: GNode[], edges: GEdge[], seeds: string[]): RingLayout {
  const present = seeds.filter((s) => nodes.some((n) => n.id === s));
  const mode: "change" | "type" = present.length ? "change" : "type";
  const hops = present.length ? hopsFrom(nodes, edges, present) : Object.fromEntries(nodes.map((n) => [n.id, null]));
  const ring: Record<string, number> = {};
  nodes.forEach((n) => {
    if (mode === "type") ring[n.id] = 1 + (TYPE_ORDER[n.type] ?? 2);
    else { const h = hops[n.id]; ring[n.id] = h === null ? UNREACHABLE : Math.min(h, MAX_RING); }
  });
  const members = new Map<number, GNode[]>();
  nodes.forEach((n) => (members.get(ring[n.id]) ?? members.set(ring[n.id], []).get(ring[n.id])!).push(n));
  const positions: RingLayout["positions"] = {};
  const rings: Ring[] = [];
  let prev = 0;
  const indices = Array.from(members.keys()).sort((a, b) => a - b);
  for (const k of indices) {
    const ns = members.get(k)!.slice().sort(byFile);
    if (k === 0) {                                   // the change: a small cluster at the centre
      const r0 = ns.length > 1 ? Math.max(18, (ns.length * SLOT) / (2 * Math.PI)) : 0;
      ns.forEach((n, i) => {
        const a = -Math.PI / 2 + (2 * Math.PI * i) / ns.length;
        positions[n.id] = { x: r0 * Math.cos(a), y: r0 * Math.sin(a) };
      });
      rings.push({ index: 0, radius: r0, label: ringLabel(0, mode), count: ns.length });
      prev = r0;
      continue;
    }
    // slots: one per node plus one empty slot between consecutive files, so a file reads as an arc
    const slots: (GNode | null)[] = [];
    ns.forEach((n, i) => { if (i > 0 && ns[i - 1].file !== n.file) slots.push(null); slots.push(n); });
    if (ns.length > 1 && ns[0].file !== ns[ns.length - 1].file) slots.push(null);
    // a crowded ring is split into bands (a ring of 300 nodes would otherwise dwarf the rings inside it);
    // a gap at twelve o'clock keeps the ring's label clear of its nodes
    const bands: (GNode | null)[][] = [];
    let r = prev + RING_GAP, i0 = 0;
    const radii: number[] = [];
    while (i0 < slots.length) {
      const cap = Math.max(8, Math.floor((2 * Math.PI * r) / SLOT) - 3);
      const rest = slots.length - i0;
      const take = bands.length === 0 && rest <= cap * 1.15 ? rest : Math.min(cap, rest);   // no band of a handful of nodes
      bands.push(slots.slice(i0, i0 + take));
      radii.push(r);
      i0 += take;
      r += SLOT * 1.4;
    }
    bands.forEach((band, b) => {
      const rb = Math.max(radii[b], ((band.length + 3) * SLOT) / (2 * Math.PI));
      radii[b] = rb;
      const gap = Math.min((3 * SLOT) / rb, Math.PI / 2);
      band.forEach((n, i) => {
        if (!n) return;
        const a = -Math.PI / 2 + gap / 2 + ((2 * Math.PI - gap) * (i + 0.5)) / band.length;
        positions[n.id] = { x: rb * Math.cos(a), y: rb * Math.sin(a) };
      });
    });
    r = radii[radii.length - 1];
    rings.push({ index: k, radius: r, label: ringLabel(k, mode), count: ns.length });
    prev = r;
  }
  return { positions, ring, hops, rings, mode };
}

/**
 * Files as groups, deterministically: each file is a box holding its nodes on a small grid (file node first, then
 * classes, functions and tests by line), and the boxes are packed in rows, sorted by path. Returns child positions;
 * cytoscape sizes each compound parent around its children.
 */
export function groupLayout(nodes: GNode[]): Record<string, { x: number; y: number }> {
  const CELL = 30, PAD = 46;
  const byPath = new Map<string, GNode[]>();
  nodes.forEach((n) => (byPath.get(n.file) ?? byPath.set(n.file, []).get(n.file)!).push(n));
  const files = Array.from(byPath.keys()).sort();
  const boxes = files.map((f) => {
    const ns = byPath.get(f)!.slice().sort(byFile);
    const cols = Math.max(1, Math.ceil(Math.sqrt(ns.length * 1.8)));
    const label = f.split("/").slice(-2).join("/");   // the group's caption must fit over its box
    return { f, ns, cols, w: Math.max(cols * CELL, label.length * 7), h: Math.ceil(ns.length / cols) * CELL };
  });
  const area = boxes.reduce((a, b) => a + (b.w + PAD) * (b.h + PAD), 0);
  const rowW = Math.max(Math.sqrt(area) * 1.5, ...boxes.map((b) => b.w));
  const pos: Record<string, { x: number; y: number }> = {};
  let x = 0, y = 0, rowH = 0;
  boxes.forEach((b) => {
    if (x > 0 && x + b.w > rowW) { x = 0; y += rowH + PAD; rowH = 0; }
    b.ns.forEach((n, i) => { pos[n.id] = { x: x + (i % b.cols) * CELL, y: y + Math.floor(i / b.cols) * CELL }; });
    x += b.w + PAD;
    rowH = Math.max(rowH, b.h);
  });
  return pos;
}
