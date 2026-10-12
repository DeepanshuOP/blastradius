import type { ReactNode } from "react";
import { Caption } from "./ui";

export type Bar = { label: string; value: number; text: string; lo?: number; hi?: number; strong?: boolean };

/**
 * Horizontal bar figure drawn in SVG. Bars are ink, the bar the sentence is about is the accent.
 * `max` is the value at full width. The values are printed at the bar ends, so the picture needs no legend;
 * `summary` is its text alternative.
 */
export function BarFigure({ bars, max, summary, caption, unit = "", log = false }: {
  bars: Bar[]; max: number; summary: string; caption: ReactNode; unit?: string; log?: boolean;
}) {
  const row = 30;
  const left = 250;
  const right = 112;
  const w = 720;
  const plot = w - left - right;
  const h = bars.length * row + 8;
  const frac = (v: number) => (log ? Math.log10(Math.max(1, v)) / Math.log10(max) : Math.max(0, Math.min(v, max)) / max);
  const x = (v: number) => left + Math.min(1, frac(v)) * plot;
  return (
    <figure className="wide-col my-6">
      <svg viewBox={`0 0 ${w} ${h}`} role="img" aria-label={summary} className="ui h-auto w-full" style={{ maxWidth: 720 }}>
        <line x1={left} x2={left} y1={0} y2={h - 4} stroke="var(--rule)" />
        {bars.map((b, i) => {
          const y = i * row + 4;
          return (
            <g key={b.label}>
              <text x={left - 8} y={y + 16} textAnchor="end" fontSize={13} fill="var(--ink)" fontWeight={b.strong ? 600 : 400}>{b.label}</text>
              <rect x={left} y={y + 4} width={Math.max(1, x(b.value) - left)} height={16} fill={b.strong ? "rgb(var(--blue-text-rgb))" : "var(--muted)"} />
              {b.lo !== undefined && b.hi !== undefined && (
                <g stroke="var(--ink)" strokeWidth={1.5}>
                  <line x1={x(b.lo)} x2={x(b.hi)} y1={y + 12} y2={y + 12} />
                  <line x1={x(b.lo)} x2={x(b.lo)} y1={y + 7} y2={y + 17} />
                  <line x1={x(b.hi)} x2={x(b.hi)} y1={y + 7} y2={y + 17} />
                </g>
              )}
              <text x={Math.max(x(b.value), b.hi !== undefined ? x(b.hi) : 0) + 8} y={y + 17} fontSize={13} fill="var(--ink)">{b.text}{unit}</text>
            </g>
          );
        })}
      </svg>
      <Caption kind="Figure">{caption}</Caption>
    </figure>
  );
}

const STAGES: { n: string; title: string; what: string; model: string }[] = [
  { n: "1", title: "Predict", what: "Rank the test files a change will break.", model: "E1, LightGBM ranker" },
  { n: "2", title: "Run", what: "The CI server runs the risky tests first.", model: "Jenkins or GitHub Actions" },
  { n: "3", title: "Triage", what: "Label each failure mine, inherited or flaky.", model: "E2, LightGBM classifier" },
  { n: "4", title: "Repair", what: "Patch failures that are mine; show the patch only if the suite passes.", model: "E3, language-model agent" },
];

/** The four stages over BR-Bench, as SVG with a text alternative. */
export function PipelineFigure() {
  const bw = 164;
  const gap = 20;
  return (
    <figure className="wide-col my-6">
      <svg viewBox="0 0 740 190" role="img" className="ui hidden h-auto w-full sm:block"
        aria-label="Four stages in a row: 1 Predict, 2 Run, 3 Triage, 4 Repair. Below them, one bar: BR-Bench trains stages 1 and 3 and scores all four.">
        <defs>
          <marker id="pf-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto">
            <path d="M0 0 L10 5 L0 10 z" fill="var(--muted)" />
          </marker>
        </defs>
        {STAGES.map((s, i) => {
          const x = 4 + i * (bw + gap);
          return (
            <g key={s.n}>
              <rect x={x} y={4} width={bw} height={104} fill="var(--panel)" stroke="var(--rule)" />
              <text x={x + 10} y={26} fontSize={14} fontWeight={600} fill="var(--ink)">{s.n}. {s.title}</text>
              <foreignObject x={x + 8} y={32} width={bw - 16} height={62}>
                <div className="ui" style={{ fontSize: 12, lineHeight: 1.35, color: "var(--ink)" }}>{s.what}</div>
              </foreignObject>
              <text x={x + 10} y={98} fontSize={11.5} fill="rgb(var(--blue-text-rgb))">{s.model}</text>
              {i < STAGES.length - 1 && <line x1={x + bw + 2} x2={x + bw + gap - 2} y1={56} y2={56} stroke="var(--muted)" strokeWidth={1.5} markerEnd="url(#pf-arrow)" />}
            </g>
          );
        })}
        <path d="M86 108 V130 M450 108 V130" stroke="var(--rule)" strokeDasharray="4 3" />
        <rect x={4} y={130} width={732} height={52} fill="var(--panel2)" stroke="var(--rule)" />
        <text x={16} y={152} fontSize={14} fontWeight={600} fill="var(--ink)">BR-Bench</text>
        <text x={16} y={171} fontSize={12.5} fill="var(--ink)">Tests that really failed in GitHub Actions runs. It trains stages 1 and 3 and measures all four.</text>
      </svg>
      <svg viewBox="0 0 360 520" role="img" className="ui block h-auto w-full sm:hidden"
        aria-label="Four stages in a column: 1 Predict, 2 Run, 3 Triage, 4 Repair. Below them, one bar: BR-Bench trains stages 1 and 3 and scores all four.">
        <defs>
          <marker id="pf-arrow-v" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto">
            <path d="M0 0 L10 5 L0 10 z" fill="var(--muted)" />
          </marker>
        </defs>
        {STAGES.map((s, i) => {
          const y = 4 + i * 100;
          return (
            <g key={s.n}>
              <rect x={4} y={y} width={352} height={78} fill="var(--panel)" stroke="var(--rule)" />
              <text x={14} y={y + 24} fontSize={16} fontWeight={600} fill="var(--ink)">{s.n}. {s.title}</text>
              <foreignObject x={12} y={y + 30} width={336} height={26}>
                <div className="ui" style={{ fontSize: 13, lineHeight: 1.3, color: "var(--ink)" }}>{s.what}</div>
              </foreignObject>
              <text x={14} y={y + 70} fontSize={13} fill="rgb(var(--blue-text-rgb))">{s.model}</text>
              {i < STAGES.length - 1 && <line x1={180} x2={180} y1={y + 80} y2={y + 98} stroke="var(--muted)" strokeWidth={1.5} markerEnd="url(#pf-arrow-v)" />}
            </g>
          );
        })}
        <rect x={4} y={406} width={352} height={104} fill="var(--panel2)" stroke="var(--rule)" />
        <text x={14} y={432} fontSize={16} fontWeight={600} fill="var(--ink)">BR-Bench</text>
        <foreignObject x={12} y={440} width={336} height={64}>
          <div className="ui" style={{ fontSize: 13, lineHeight: 1.35, color: "var(--ink)" }}>Tests that really failed in GitHub Actions runs. It trains stages 1 and 3 and measures all four.</div>
        </foreignObject>
      </svg>
      <Caption kind="Figure">
        The BlastRadius pipeline. Each stage is one experiment on BR-Bench (stages 1 to 3) or BR-Seeded (stage 4), and each may
        come out negative: Gate 3 for stage 1 was not met.
      </Caption>
    </figure>
  );
}
