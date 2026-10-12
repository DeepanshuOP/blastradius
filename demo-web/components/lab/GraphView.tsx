"use client";

import type { Core, ElementDefinition, NodeSingular } from "cytoscape";
import { forwardRef, useEffect, useImperativeHandle, useMemo, useRef, useState, type ReactNode } from "react";
import { UNREACHABLE, groupLayout, ringLayout, type RingLayout } from "./rings";
import type { GEdge, GNode } from "./types";

export interface GraphHandle { fit: () => void; zoomIn: () => void; zoomOut: () => void; center: (id: string) => void }
export type LayoutMode = "rings" | "force" | "groups";
export interface CardInfo { hop: number | null; ring: number; mode: RingLayout["mode"] }

export interface GraphViewProps {
  nodes: GNode[];
  edges: GEdge[];
  changed?: string[];
  layout?: LayoutMode;
  seeds?: string[];                              // ring centre; defaults to `changed`
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
  onContext?: (id: string, x: number, y: number) => void;
  renderCard?: (id: string, info: CardInfo) => ReactNode;
  ariaLabel?: string;
  className?: string;
}

/** A theme colour as `rgb(r, g, b)`, read from the `--<name>-rgb` triplet (Cytoscape cannot resolve `var()`). */
const css = (name: string, fallback: string) => {
  const v = typeof window !== "undefined" ? getComputedStyle(document.documentElement).getPropertyValue(`${name}-rgb`).trim() : "";
  return v ? `rgb(${v.split(/\s+/).join(",")})` : fallback;
};
const reduced = () => typeof window !== "undefined" && window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;

function styleSheet() {
  const c = {
    file: css("--blue", "#2F7FB0"), cls: css("--amber", "#F2A93B"), fn: css("--muted", "#8E98AB"), test: css("--green", "#2E9E6A"),
    accent: css("--accent", "#E8572A"), red: css("--red", "#C23B30"), green: css("--green", "#2E9E6A"), edge: css("--rule", "#2C3342"),
    ink: css("--ink", "#E7EAF0"), page: css("--page", "#131722"), panel2: css("--panel2", "#222836"), muted: css("--muted", "#8E98AB"),
  };
  const font = getComputedStyle(document.body).fontFamily;
  return [
    { selector: "node", style: { "background-color": c.fn, width: "mapData(size, 0, 1, 8, 20)", height: "mapData(size, 0, 1, 8, 20)",
        "border-width": 1, "border-color": c.page, label: "", color: c.ink, "font-size": 11, "font-family": font, "text-valign": "bottom", "text-margin-y": 4,
        "text-background-color": c.page, "text-background-opacity": 0.85, "text-background-padding": 2, "text-background-shape": "roundrectangle",
        "min-zoomed-font-size": 6, "overlay-opacity": 0, "transition-property": "background-color, border-color, border-width", "transition-duration": 180 } },
    { selector: 'node[type = "file"]', style: { shape: "round-rectangle", "background-color": c.file } },
    { selector: 'node[type = "class"]', style: { shape: "diamond", "background-color": c.cls } },
    { selector: 'node[type = "function"]', style: { shape: "ellipse" } },
    { selector: 'node[type = "test"]', style: { shape: "hexagon", "background-color": c.page, "border-color": c.test, "border-width": 2 } },
    { selector: "node.testfile", style: { "border-color": c.test, "border-width": 2 } },
    { selector: ":parent", style: { shape: "round-rectangle", "background-color": c.panel2, "background-opacity": 0.35, "border-color": c.edge, "border-width": 1,
        label: "data(short)", "text-valign": "top", "text-halign": "center", "text-margin-y": -4, "font-size": 11, color: c.muted, padding: 10 } },
    { selector: "edge", style: { width: 1, "line-color": c.edge, "curve-style": "haystack", opacity: 0.5, "haystack-radius": 0 } },
    { selector: 'edge[type = "call"]', style: { "line-color": c.muted, opacity: 0.22 } },
    { selector: 'edge[type = "tests"]', style: { "line-color": c.test, opacity: 0.28 } },
    { selector: 'edge[type = "import"]', style: { "line-color": c.file, opacity: 0.2 } },
    { selector: "edge.faded", style: { opacity: 0.07 } },
    { selector: "node.reach", style: { "border-color": c.accent, "border-width": 2 } },
    { selector: "node.wave", style: { "border-color": c.accent, "border-width": 4, "underlay-color": c.accent, "underlay-opacity": 0.4, "underlay-padding": 6 } },
    { selector: "node.changed", style: { "background-color": c.accent, "border-color": c.ink, "border-width": 2, width: 24, height: 24, label: "data(short)", "z-index": 20,
        "font-weight": 600, "underlay-color": c.accent, "underlay-opacity": 0.35, "underlay-padding": 10, "underlay-shape": "ellipse" } },
    { selector: "edge.path", style: { "line-color": c.accent, width: 2.5, opacity: 0.95, "z-index": 15 } },
    { selector: "node.onpath", style: { "border-color": c.accent, "border-width": 3 } },
    { selector: "node.atrisk", style: { "border-color": c.accent, "border-width": 3, label: "data(short)" } },
    { selector: "node.pass", style: { "background-color": c.green, "border-color": c.green } },
    { selector: "node.fail", style: { "background-color": c.red, "border-color": c.ink, "border-width": 3, "border-style": "double", width: 16, height: 16, "z-index": 18 } },
    { selector: "node.hit", style: { "border-color": c.ink, "border-width": 3, label: "data(short)" } },
    { selector: "node.hover", style: { label: "data(short)", "z-index": 40 } },
    { selector: "node.kbd", style: { label: "data(short)", "border-color": c.ink, "border-width": 3, "z-index": 40 } },
    { selector: "node.trace, node.sel", style: { "border-color": c.ink, "border-width": 4, label: "data(short)", "z-index": 30 } },
    { selector: "edge.trace", style: { "line-color": c.ink, width: 3, opacity: 1, "z-index": 25 } },
    { selector: ".hidden", style: { display: "none" } },
  ] as never;
}

const shortLabel = (n: GNode) => (n.type === "file" ? n.file.split("/").slice(-1)[0] : n.label.replace(/^\./, ""));
const edgeBetween = (cy: Core, a: string, b: string) =>
  cy.edges().filter((e) => (e.source().id() === a && e.target().id() === b) || (e.target().id() === a && e.source().id() === b));

export const GraphView = forwardRef<GraphHandle, GraphViewProps>(function GraphView(p, ref) {
  const box = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);
  const guide = useRef<SVGGElement>(null);
  const labels = useRef<HTMLDivElement>(null);
  const waves = useRef<SVGGElement>(null);
  const timers = useRef<number[]>([]);
  const sig = useRef("");
  const cb = useRef({ select: p.onSelect, context: p.onContext });
  cb.current = { select: p.onSelect, context: p.onContext };
  const [ready, setReady] = useState(0);
  const [cardAt, setCardAt] = useState<{ x: number; y: number } | null>(null);
  const [kbd, setKbd] = useState<number>(-1);
  const layout = p.layout ?? "rings";
  const seeds = useMemo(() => p.seeds ?? p.changed ?? [], [p.seeds, p.changed]);
  const rl = useMemo(() => (layout === "rings" ? ringLayout(p.nodes, p.edges, seeds) : null), [layout, p.nodes, p.edges, seeds]);
  const rlRef = useRef(rl);
  rlRef.current = rl;
  const order = useMemo(() => {                    // keyboard order: ring by ring, then around the ring
    if (!rl) return p.nodes.map((n) => n.id);
    return p.nodes.map((n) => n.id).sort((a, b) => (rl.ring[a] - rl.ring[b]) ||
      Math.atan2(rl.positions[a]?.y ?? 0, rl.positions[a]?.x ?? 0) - Math.atan2(rl.positions[b]?.y ?? 0, rl.positions[b]?.x ?? 0));
  }, [rl, p.nodes]);

  /** Ring guides and their hop labels follow the viewport (drawn in screen space, so strokes stay 1 px). */
  const drawGuides = () => {
    const cy = cyRef.current;
    const g = guide.current, lab = labels.current;
    if (!cy || !g || !lab) return;
    const r = rlRef.current;
    const pan = cy.pan(), z = cy.zoom();
    const rings = r ? r.rings.filter((x) => x.index > 0 && x.radius > 0) : [];
    while (g.childNodes.length > rings.length) g.removeChild(g.lastChild!);
    while (lab.childNodes.length > rings.length) lab.removeChild(lab.lastChild!);
    rings.forEach((ring, i) => {
      let c = g.childNodes[i] as SVGCircleElement | undefined;
      if (!c) { c = document.createElementNS("http://www.w3.org/2000/svg", "circle"); g.appendChild(c); }
      c.setAttribute("cx", String(pan.x)); c.setAttribute("cy", String(pan.y)); c.setAttribute("r", String(ring.radius * z));
      c.setAttribute("class", ring.index === UNREACHABLE ? "br-guide br-guide-far" : "br-guide");
      let l = lab.childNodes[i] as HTMLSpanElement | undefined;
      if (!l) { l = document.createElement("span"); lab.appendChild(l); }
      l.className = "ui br-guide-label";
      l.textContent = `${ring.label} · ${ring.count}`;
      l.style.left = `${pan.x}px`;
      l.style.top = `${pan.y - ring.radius * z}px`;
    });
  };

  useImperativeHandle(ref, () => ({
    fit: () => cyRef.current?.fit(undefined, 24),
    zoomIn: () => cyRef.current?.zoom({ level: cyRef.current.zoom() * 1.3, renderedPosition: { x: (box.current?.clientWidth ?? 0) / 2, y: (box.current?.clientHeight ?? 0) / 2 } }),
    zoomOut: () => cyRef.current?.zoom({ level: cyRef.current.zoom() / 1.3, renderedPosition: { x: (box.current?.clientWidth ?? 0) / 2, y: (box.current?.clientHeight ?? 0) / 2 } }),
    center: (id: string) => { const n = cyRef.current?.getElementById(id); if (n && n.nonempty()) cyRef.current?.animate({ center: { eles: n }, zoom: Math.max(cyRef.current.zoom(), 1.4) }, { duration: reduced() ? 0 : 220 }); },
  }));

  // create the instance once
  useEffect(() => {
    let dead = false;
    (async () => {
      const cytoscape = (await import("cytoscape")).default;
      if (dead || !box.current || cyRef.current) return;
      const cy = cytoscape({ container: box.current, style: styleSheet(), wheelSensitivity: 0.25, minZoom: 0.08, maxZoom: 4, boxSelectionEnabled: false });
      cy.on("tap", "node", (e) => { const n = e.target as NodeSingular; if (!n.isParent()) cb.current.select?.(n.id()); });
      cy.on("tap", (e) => { if (e.target === cy) cb.current.select?.(null); });
      const ctx = (e: { target: unknown }) => { const n = e.target as NodeSingular; const rp = n.renderedPosition(); if (!n.isParent()) cb.current.context?.(n.id(), rp.x, rp.y); };
      cy.on("cxttap", "node", ctx);
      cy.on("taphold", "node", ctx);                // long-press on a touch screen
      cy.on("mouseover", "node", (e) => (e.target as NodeSingular).addClass("hover"));
      cy.on("mouseout", "node", (e) => (e.target as NodeSingular).removeClass("hover"));
      cy.on("viewport resize", drawGuides);
      cyRef.current = cy;
      setReady((x) => x + 1);
    })();
    const ro = typeof ResizeObserver !== "undefined" ? new ResizeObserver(() => { cyRef.current?.resize(); cyRef.current?.fit(undefined, 24); drawGuides(); }) : null;
    if (box.current && ro) ro.observe(box.current);
    return () => { dead = true; ro?.disconnect(); };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // build / lay out the graph when its content or the layout changes
  useEffect(() => {
    const cy = cyRef.current;
    if (!cy) return;
    const content = `${layout}:${p.nodes.length}:${p.edges.length}:${p.nodes[0]?.id ?? ""}:${p.nodes[p.nodes.length - 1]?.id ?? ""}`;
    const maxPr = Math.max(1e-6, ...p.nodes.map((n) => n.pagerank));
    if (sig.current !== content) {
      sig.current = content;
      const ids = new Set(p.nodes.map((n) => n.id));
      const els: ElementDefinition[] = [];
      if (layout === "groups") {                   // files as compound groups: one parent per file
        const files = Array.from(new Set(p.nodes.map((n) => n.file)));
        files.forEach((f) => els.push({ group: "nodes", data: { id: `grp:${f}`, short: f.split("/").slice(-2).join("/"), type: "group", file: f } }));
      }
      p.nodes.forEach((n) => els.push({ group: "nodes", data: { id: n.id, type: n.type, label: n.label, file: n.file, short: shortLabel(n), size: Math.sqrt(n.pagerank / maxPr),
        ...(layout === "groups" ? { parent: `grp:${n.file}` } : {}) }, classes: n.is_test_file && n.type === "file" ? "testfile" : "" }));
      p.edges.filter((e) => ids.has(e.source) && ids.has(e.target)).forEach((e) => els.push({ group: "edges", data: { id: e.id, source: e.source, target: e.target, type: e.type } }));
      cy.elements().remove();
      cy.add(els);
      if (layout === "rings" && rl) cy.layout({ name: "preset", positions: (n: NodeSingular) => rl.positions[n.id()] ?? { x: 0, y: 0 }, fit: true, padding: 24 } as never).run();
      else if (layout === "groups") {
        const pos = groupLayout(p.nodes);
        cy.layout({ name: "preset", positions: (n: NodeSingular) => pos[n.id()] ?? { x: 0, y: 0 }, fit: true, padding: 24 } as never).run();
      } else cy.layout({ name: "cose", animate: false, randomize: false, nodeRepulsion: () => 12000, idealEdgeLength: () => 60,
        componentSpacing: 60, gravity: 0.6, numIter: p.nodes.length > 400 ? 400 : 900, fit: true, padding: 24 } as never).run();
    } else if (layout === "rings" && rl) {        // same graph, new centre (the change arrived): move to the rings
      cy.layout({ name: "preset", positions: (n: NodeSingular) => rl.positions[n.id()] ?? { x: 0, y: 0 }, fit: true, padding: 24, animate: !reduced(), animationDuration: 450,
        animationEasing: "ease-out-cubic" } as never).run();
    }
    drawGuides();
    window.setTimeout(drawGuides, 500);
  }, [ready, layout, p.nodes, p.edges, rl]); // eslint-disable-line react-hooks/exhaustive-deps

  // state classes
  useEffect(() => {
    const cy = cyRef.current;
    if (!cy) return;
    cy.batch(() => {
      cy.elements().removeClass("changed onpath atrisk pass fail hidden hit trace sel path faded");
      (p.changed ?? []).forEach((id) => cy.getElementById(id).addClass("changed"));
      (p.atRisk ?? []).forEach((id) => cy.getElementById(id).addClass("atrisk"));
      const paths = p.paths ?? [];
      paths.forEach((path) => {
        path.forEach((id, i) => {
          cy.getElementById(id).addClass("onpath");
          if (i > 0) edgeBetween(cy, path[i - 1], id).addClass("path");
        });
      });
      if (paths.length || (layout === "rings" && rlRef.current?.mode === "type")) cy.edges().not(".path").addClass("faded");
      Object.entries(p.outcomes ?? {}).forEach(([id, o]) => cy.getElementById(id).addClass(o === "failed" ? "fail" : "pass"));
      (p.hiddenNodeTypes ?? []).forEach((t) => cy.nodes(`[type = "${t}"]`).addClass("hidden"));
      (p.hiddenEdgeTypes ?? []).forEach((t) => cy.edges(`[type = "${t}"]`).addClass("hidden"));
      const q = (p.search ?? "").trim().toLowerCase();
      if (q) cy.nodes().filter((n) => !n.isParent() && (String(n.data("label")).toLowerCase().includes(q) || String(n.data("file")).toLowerCase().includes(q))).addClass("hit");
      (p.trace ?? []).forEach((id, i, a) => {
        cy.getElementById(id).addClass("trace");
        if (i > 0) edgeBetween(cy, a[i - 1], id).addClass("trace");
      });
      if (p.selected) cy.getElementById(p.selected).addClass("sel");
    });
  }, [ready, p.changed, p.atRisk, p.paths, p.outcomes, p.hiddenNodeTypes, p.hiddenEdgeTypes, p.search, p.trace, p.selected, p.nodes, p.edges, layout]);

  // the card sits beside the selected node, kept inside the graph box
  useEffect(() => {
    const cy = cyRef.current;
    if (!cy || !p.selected) { setCardAt(null); return; }
    const n = cy.getElementById(p.selected);
    if (n.empty()) { setCardAt(null); return; }
    const rp = n.renderedPosition();
    setCardAt({ x: rp.x, y: rp.y });
  }, [p.selected, ready]);

  // the shockwave: ring by ring, an accent ring sweeps out to that ring's radius and its nodes light up
  useEffect(() => {
    const cy = cyRef.current;
    const r = rlRef.current;
    if (!cy || !p.waveKey || !r || r.mode !== "change") return;
    timers.current.forEach((t) => clearTimeout(t));
    timers.current = [];
    cy.nodes().removeClass("wave reach");
    const byRing = new Map<number, string[]>();
    Object.entries(r.ring).forEach(([id, k]) => { if (k > 0 && k < UNREACHABLE) (byRing.get(k) ?? byRing.set(k, []).get(k)!).push(id); });
    const ks = Array.from(byRing.keys()).sort((a, b) => a - b);
    if (reduced()) {                               // no motion: the end state, at once
      ks.forEach((k) => { if (k <= 2) byRing.get(k)!.forEach((id) => cy.getElementById(id).addClass("reach")); });
      return;
    }
    const radius = new Map(r.rings.map((x) => [x.index, x.radius]));
    ks.forEach((k, i) => {
      const t = window.setTimeout(() => {
        const ids = byRing.get(k)!;
        ids.forEach((id) => cy.getElementById(id).addClass("wave"));
        timers.current.push(window.setTimeout(() => ids.forEach((id) => { const n = cy.getElementById(id); n.removeClass("wave"); if (k <= 2) n.addClass("reach"); }), 650));
        const g = waves.current;
        if (g) {
          const pan = cy.pan(), z = cy.zoom();
          const c = document.createElementNS("http://www.w3.org/2000/svg", "circle");
          c.setAttribute("cx", String(pan.x)); c.setAttribute("cy", String(pan.y));
          c.setAttribute("class", "br-wave-ring");
          g.appendChild(c);
          const from = (radius.get(ks[i - 1] ?? 0) ?? 0) * z, to = (radius.get(k) ?? 0) * z;
          const anim = c.animate([{ r: `${from}px`, opacity: 0.9, strokeWidth: "6px" }, { r: `${to}px`, opacity: 0.15, strokeWidth: "1.5px" }],
            { duration: 520, easing: "cubic-bezier(0.16, 1, 0.3, 1)", fill: "forwards" });
          anim.onfinish = () => window.setTimeout(() => c.remove(), 250);
        }
      }, 120 + i * 420);
      timers.current.push(t);
    });
    return () => { timers.current.forEach((t) => clearTimeout(t)); };
  }, [p.waveKey]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => () => { cyRef.current?.destroy(); cyRef.current = null; }, []);

  const focusNode = (i: number) => {
    const cy = cyRef.current;
    if (!cy || !order.length) return;
    const k = (i + order.length) % order.length;
    cy.nodes().removeClass("kbd");
    cy.getElementById(order[k]).addClass("kbd");
    setKbd(k);
  };
  const kbdNode = kbd >= 0 ? p.nodes.find((n) => n.id === order[kbd]) : undefined;
  const sel = p.selected ? p.nodes.find((n) => n.id === p.selected) : undefined;
  const W = box.current?.clientWidth ?? 800, H = box.current?.clientHeight ?? 500;
  const card = sel && cardAt && p.renderCard ? p.renderCard(sel.id, { hop: rl?.hops[sel.id] ?? null, ring: rl?.ring[sel.id] ?? -1, mode: rl?.mode ?? "type" }) : null;
  const CW = 340;
  const left = cardAt ? (cardAt.x + 18 + CW < W ? cardAt.x + 18 : Math.max(8, cardAt.x - 18 - CW)) : 0;
  const top = cardAt ? Math.min(Math.max(8, cardAt.y - 40), Math.max(8, H - 330)) : 0;

  return (
    <div className={p.className ?? "relative h-full w-full"}>
      <svg className="pointer-events-none absolute inset-0 h-full w-full" aria-hidden="true"><g ref={guide} /><g ref={waves} /></svg>
      <div ref={labels} className="pointer-events-none absolute inset-0 overflow-hidden" aria-hidden="true" />
      <div ref={box} className="absolute inset-0 rounded outline-none focus-visible:ring-2 focus-visible:ring-accent" tabIndex={0} role="application"
        aria-label={`${p.ariaLabel ?? "Code graph"}: ${p.nodes.length} nodes. Arrow keys move between nodes ring by ring, Enter opens the node card, Escape closes it.`}
        onKeyDown={(e) => {
          if (e.key === "ArrowRight" || e.key === "ArrowDown") { e.preventDefault(); focusNode(kbd + 1); }
          else if (e.key === "ArrowLeft" || e.key === "ArrowUp") { e.preventDefault(); focusNode(kbd - 1); }
          else if (e.key === "Enter" && kbd >= 0) { e.preventDefault(); p.onSelect?.(order[kbd]); }
          else if ((e.key === "ContextMenu" || (e.shiftKey && e.key === "F10")) && kbd >= 0 && p.onContext) {
            e.preventDefault(); const n = cyRef.current?.getElementById(order[kbd]); const rp = n?.renderedPosition(); if (rp) p.onContext(order[kbd], rp.x, rp.y);
          } else if (e.key === "Escape") { p.onSelect?.(null); }
        }}
        onContextMenu={(e) => e.preventDefault()} />
      <p className="sr-only" aria-live="polite">{kbdNode ? `${kbdNode.type} ${kbdNode.label} in ${kbdNode.file}${rl && rl.mode === "change" ? `, ${rl.hops[kbdNode.id] === null ? "not reachable from the change" : `${rl.hops[kbdNode.id]} hops from the change`}` : ""}` : ""}</p>
      {card && (
        <div className="absolute z-20" style={{ left, top, width: CW }}>{card}</div>
      )}
    </div>
  );
});
