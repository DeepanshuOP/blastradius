"use client";

import type { Core, ElementDefinition, NodeSingular } from "cytoscape";
import { forwardRef, useEffect, useImperativeHandle, useRef } from "react";
import type { GEdge, GNode } from "./types";

export interface GraphHandle { fit: () => void; zoomIn: () => void; zoomOut: () => void; center: (id: string) => void }

export interface GraphViewProps {
  nodes: GNode[];
  edges: GEdge[];
  changed?: string[];
  hops?: Record<string, number>;
  waveKey?: number;                              // a new value replays the shockwave
  paths?: string[][];                            // node-id paths to highlight
  outcomes?: Record<string, "passed" | "failed">;
  atRisk?: string[];                             // node ids of at-risk test files
  hiddenNodeTypes?: string[];
  hiddenEdgeTypes?: string[];
  search?: string;
  trace?: string[];
  selected?: string | null;
  onSelect?: (id: string | null) => void;
  className?: string;
}

/** A theme colour as `rgb(r, g, b)`, read from the `--<name>-rgb` triplet (Cytoscape cannot resolve `var()`). */
const css = (name: string, fallback: string) => {
  const v = typeof window !== "undefined" ? getComputedStyle(document.documentElement).getPropertyValue(`${name}-rgb`).trim() : "";
  return v ? `rgb(${v.split(/\s+/).join(",")})` : fallback;
};

function styleSheet() {
  const c = {
    file: css("--blue", "#2F7FB0"), cls: css("--amber", "#F2A93B"), fn: css("--muted", "#8E98AB"), test: css("--green", "#2E9E6A"),
    accent: css("--accent", "#E8572A"), red: css("--red", "#C23B30"), green: css("--green", "#2E9E6A"), edge: css("--rule", "#2C3342"),
    ink: css("--ink", "#E7EAF0"), page: css("--page", "#131722"),
  };
  return [
    { selector: "node", style: { "background-color": c.fn, width: "mapData(size, 0, 1, 7, 24)", height: "mapData(size, 0, 1, 7, 24)",
        "border-width": 1, "border-color": c.page, label: "", color: c.ink, "font-size": 9, "text-valign": "bottom", "text-margin-y": 3,
        "min-zoomed-font-size": 8, "overlay-opacity": 0 } },
    { selector: 'node[type = "file"]', style: { shape: "round-rectangle", "background-color": c.file, label: "data(short)" } },
    { selector: 'node[type = "class"]', style: { shape: "diamond", "background-color": c.cls } },
    { selector: 'node[type = "function"]', style: { shape: "ellipse" } },
    { selector: 'node[type = "test"]', style: { shape: "hexagon", "background-color": c.page, "border-color": c.test, "border-width": 2 } },
    { selector: "node.testfile", style: { "border-color": c.test, "border-width": 2 } },
    { selector: "edge", style: { width: 1, "line-color": c.edge, "curve-style": "haystack", opacity: 0.8, "haystack-radius": 0 } },
    { selector: 'edge[type = "call"]', style: { "line-color": css("--muted", "#8E98AB"), opacity: 0.45 } },
    { selector: 'edge[type = "tests"]', style: { "line-color": c.test, opacity: 0.5 } },
    { selector: 'edge[type = "import"]', style: { "line-color": c.file, opacity: 0.35 } },
    { selector: "node.wave", style: { "border-color": c.accent, "border-width": 3, "underlay-color": c.accent, "underlay-opacity": 0.35, "underlay-padding": 6 } },
    { selector: "node.reach", style: { "border-color": c.cls, "border-width": 2, "underlay-color": c.accent, "underlay-opacity": 0.15, "underlay-padding": 4 } },
    { selector: "node.changed", style: { "background-color": c.accent, "border-color": c.accent, "border-width": 3, label: "data(short)", "z-index": 20,
        "underlay-color": c.accent, "underlay-opacity": 0.45, "underlay-padding": 9 } },
    { selector: "edge.path", style: { "line-color": c.accent, width: 3, opacity: 1, "z-index": 15 } },
    { selector: "node.onpath", style: { "border-color": c.accent, "border-width": 3, label: "data(short)" } },
    { selector: "node.atrisk", style: { "border-color": c.accent, "border-width": 3, label: "data(short)" } },
    { selector: "node.pass", style: { "background-color": c.green, "border-color": c.green } },
    { selector: "node.fail", style: { "background-color": c.red, "border-color": c.red, "border-width": 3, "underlay-color": c.red, "underlay-opacity": 0.35, "underlay-padding": 5 } },
    { selector: "node.hit", style: { "border-color": c.ink, "border-width": 3, label: "data(short)" } },
    { selector: "node.trace, node.sel", style: { "border-color": c.ink, "border-width": 4, label: "data(short)", "z-index": 30 } },
    { selector: "edge.trace", style: { "line-color": c.ink, width: 3, opacity: 1, "z-index": 25 } },
    { selector: ".hidden", style: { display: "none" } },
  ] as never;
}

const short = (n: GNode) => (n.type === "file" ? n.file.split("/").slice(-1)[0] : n.label.replace(/^\./, ""));

export const GraphView = forwardRef<GraphHandle, GraphViewProps>(function GraphView(p, ref) {
  const box = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);
  const rings = useRef<HTMLDivElement>(null);
  const timers = useRef<number[]>([]);
  const sig = useRef("");
  const cb = useRef(p.onSelect);
  cb.current = p.onSelect;

  useImperativeHandle(ref, () => ({
    fit: () => cyRef.current?.fit(undefined, 30),
    zoomIn: () => cyRef.current?.zoom({ level: cyRef.current.zoom() * 1.3, renderedPosition: { x: (box.current?.clientWidth ?? 0) / 2, y: (box.current?.clientHeight ?? 0) / 2 } }),
    zoomOut: () => cyRef.current?.zoom({ level: cyRef.current.zoom() / 1.3, renderedPosition: { x: (box.current?.clientWidth ?? 0) / 2, y: (box.current?.clientHeight ?? 0) / 2 } }),
    center: (id: string) => { const n = cyRef.current?.getElementById(id); if (n && n.nonempty()) cyRef.current?.animate({ center: { eles: n }, zoom: 1.6 }, { duration: 250 }); },
  }));

  // build / rebuild the graph when its content changes
  useEffect(() => {
    let dead = false;
    const key = `${p.nodes.length}:${p.edges.length}:${p.nodes[0]?.id ?? ""}:${p.nodes[p.nodes.length - 1]?.id ?? ""}`;
    (async () => {
      const cytoscape = (await import("cytoscape")).default;
      if (dead || !box.current) return;
      if (!cyRef.current) {
        const cy = cytoscape({ container: box.current, style: styleSheet(), wheelSensitivity: 0.25, minZoom: 0.1, maxZoom: 4, boxSelectionEnabled: false });
        cy.on("tap", "node", (e) => cb.current?.((e.target as NodeSingular).id()));
        cy.on("tap", (e) => { if (e.target === cy) cb.current?.(null); });
        cyRef.current = cy;
      }
      const cy = cyRef.current;
      if (sig.current === key) return;
      sig.current = key;
      const maxPr = Math.max(1e-6, ...p.nodes.map((n) => n.pagerank));
      const ids = new Set(p.nodes.map((n) => n.id));
      const els: ElementDefinition[] = [
        ...p.nodes.map((n) => ({ group: "nodes" as const, data: { id: n.id, type: n.type, label: n.label, file: n.file, short: short(n), size: Math.sqrt(n.pagerank / maxPr) }, classes: n.is_test_file && n.type === "file" ? "testfile" : "" })),
        ...p.edges.filter((e) => ids.has(e.source) && ids.has(e.target)).map((e) => ({ group: "edges" as const, data: { id: e.id, source: e.source, target: e.target, type: e.type } })),
      ];
      cy.elements().remove();
      cy.add(els);
      cy.layout({ name: "cose", animate: false, randomize: true, nodeRepulsion: () => 9000, idealEdgeLength: () => 55, numIter: p.nodes.length > 400 ? 300 : 700, fit: true, padding: 30 } as never).run();
    })();
    return () => { dead = true; };
  }, [p.nodes, p.edges]);

  // state classes
  useEffect(() => {
    const cy = cyRef.current;
    if (!cy) return;
    cy.batch(() => {
      cy.elements().removeClass("changed onpath atrisk pass fail hidden hit trace sel path");
      (p.changed ?? []).forEach((id) => cy.getElementById(id).addClass("changed"));
      (p.atRisk ?? []).forEach((id) => cy.getElementById(id).addClass("atrisk"));
      (p.paths ?? []).forEach((path) => {
        path.forEach((id, i) => {
          cy.getElementById(id).addClass("onpath");
          if (i > 0) cy.edges().filter((e) => (e.source().id() === path[i - 1] && e.target().id() === id) || (e.target().id() === path[i - 1] && e.source().id() === id)).addClass("path");
        });
      });
      Object.entries(p.outcomes ?? {}).forEach(([id, o]) => cy.getElementById(id).addClass(o === "failed" ? "fail" : "pass"));
      (p.hiddenNodeTypes ?? []).forEach((t) => cy.nodes(`[type = "${t}"]`).addClass("hidden"));
      (p.hiddenEdgeTypes ?? []).forEach((t) => cy.edges(`[type = "${t}"]`).addClass("hidden"));
      const q = (p.search ?? "").trim().toLowerCase();
      if (q) cy.nodes().filter((n) => String(n.data("label")).toLowerCase().includes(q) || String(n.data("file")).toLowerCase().includes(q)).addClass("hit");
      (p.trace ?? []).forEach((id, i, a) => {
        cy.getElementById(id).addClass("trace");
        if (i > 0) cy.edges().filter((e) => (e.source().id() === a[i - 1] && e.target().id() === id) || (e.target().id() === a[i - 1] && e.source().id() === id)).addClass("trace");
      });
      if (p.selected) cy.getElementById(p.selected).addClass("sel");
    });
  }, [p.changed, p.atRisk, p.paths, p.outcomes, p.hiddenNodeTypes, p.hiddenEdgeTypes, p.search, p.trace, p.selected, p.nodes, p.edges]);

  // the shockwave: hop by hop, a ring expands from each changed node and the nodes of that hop light up
  useEffect(() => {
    const cy = cyRef.current;
    if (!cy || !p.waveKey || !p.hops) return;
    timers.current.forEach((t) => clearTimeout(t));
    timers.current = [];
    cy.nodes().removeClass("wave reach");
    const byHop: Record<number, string[]> = {};
    Object.entries(p.hops).forEach(([id, h]) => (byHop[h] ??= []).push(id));
    const hopsSorted = Object.keys(byHop).map(Number).sort((a, b) => a - b);
    const layer = rings.current;
    hopsSorted.forEach((h, k) => {
      const t = window.setTimeout(() => {
        byHop[h].forEach((id) => cy.getElementById(id).addClass("wave"));
        window.setTimeout(() => byHop[h].forEach((id) => { const n = cy.getElementById(id); n.removeClass("wave"); if (h <= 2) n.addClass("reach"); }), 700);
        if (layer) {
          (p.changed ?? []).slice(0, 3).forEach((cid) => {
            const n = cy.getElementById(cid);
            if (n.empty()) return;
            const pos = n.renderedPosition();
            const el = document.createElement("div");
            el.className = "br-ring";
            el.style.left = `${pos.x}px`;
            el.style.top = `${pos.y}px`;
            layer.appendChild(el);
            window.setTimeout(() => el.remove(), 1100);
          });
        }
      }, k * 420);
      timers.current.push(t);
    });
    return () => { timers.current.forEach((t) => clearTimeout(t)); };
  }, [p.waveKey]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => () => { cyRef.current?.destroy(); cyRef.current = null; }, []);

  return (
    <div className={p.className ?? "relative h-full w-full"}>
      <div ref={box} className="absolute inset-0" role="img" aria-label="Code graph" />
      <div ref={rings} className="pointer-events-none absolute inset-0 overflow-hidden" aria-hidden="true" />
    </div>
  );
});
