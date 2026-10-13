"use client";

import { useDoc } from "../lib";
import { Prov } from "./common";
import { Term } from "./Glossary";

type Curve = { method: string; points: { rate: number; value: number }[] };
export type PtsDoc = {
  source: string; meta_source: string; candidates_mean: string; candidates_median: string;
  test_recall: Curve[]; change_recall: Curve[];
  targets: { method: string; test_recall_95: string; change_recall_999: string }[];
  meta: { test_recall: { target: string; rate: string }; change_recall: { target: string; rate: string } };
};
export type GlanceRow = { reference: string; metric: string; theirs: string; ours: string; same_data: string; verdict: string; chip: string };
export type GlanceDoc = { source: string; rows: GlanceRow[] };

const OURS = "BlastRadius ranker";
const FLOOR = "B1 random (mean of 20 seeds)";

function Card({ id, title, right, children, source }: { id: string; title: string; right?: React.ReactNode; children: React.ReactNode; source: string }) {
  return (
    <section id={id} aria-label={title} className="min-w-0 rounded-md border border-rule bg-panel">
      <header className="flex min-h-[40px] items-center justify-between gap-3 border-b border-rule px-3 py-2">
        <h2 className="ui m-0 text-sm font-semibold text-ink">{title}</h2>
        <div className="flex items-center gap-2"><Prov mode="bench" />{right}</div>
      </header>
      <div className="p-3">{children}</div>
      <p className="cap m-0 border-t border-rule px-3 py-1.5 text-2xs">Source: <span className="mono text-2xs">{source}</span></p>
    </section>
  );
}

export function Skeleton({ rows = 4 }: { rows?: number }) {
  return (
    <div className="space-y-2" aria-busy="true" aria-label="Loading">
      {Array.from({ length: rows }, (_, i) => <div key={i} className="br-skel h-4 rounded" style={{ width: `${90 - i * 12}%` }} />)}
    </div>
  );
}

/** Test recall against selection rate: our ranker, the random floor, and Meta's reported operating point. */
function RateChart({ doc }: { doc: PtsDoc }) {
  const ours = doc.test_recall.find((c) => c.method === OURS);
  const floor = doc.test_recall.find((c) => c.method === FLOOR);
  const t = doc.targets.find((x) => x.method === OURS);
  if (!ours || !t) return null;
  const W = 300, H = 170, L = 38, B = 26, T = 8, R = 10;
  const x = (v: number) => L + v * (W - L - R), y = (v: number) => H - B - v * (H - B - T);
  const oursPts = [{ rate: 0, value: 0 }, ...ours.points, { rate: Number(t.test_recall_95), value: 0.95 }];
  const floorPts = floor ? [{ rate: 0, value: 0 }, ...floor.points] : [];
  const metaRate = Number(doc.meta.test_recall.rate.replace(/[<>]/g, ""));
  const line = (ps: { rate: number; value: number }[]) => ps.map((p, i) => `${i ? "L" : "M"}${x(p.rate).toFixed(1)},${y(p.value).toFixed(1)}`).join("");
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="ui h-auto w-full max-w-[420px]" role="img"
      aria-label={`Test recall against selection rate. Our ranker reaches 0.95 at rate ${t.test_recall_95}; Meta reports 0.95 at a rate below ${metaRate} on private data.`}>
      {[0, 0.25, 0.5, 0.75, 1].map((v) => (
        <g key={v}>
          <line x1={L} x2={W - R} y1={y(v)} y2={y(v)} stroke="var(--rule)" strokeWidth={1} />
          <text x={L - 4} y={y(v) + 3} fontSize={9} textAnchor="end" fill="var(--muted)">{v}</text>
          <text x={x(v)} y={H - B + 12} fontSize={9} textAnchor="middle" fill="var(--muted)">{v}</text>
        </g>
      ))}
      <text x={(L + W - R) / 2} y={H - 2} fontSize={9} textAnchor="middle" fill="var(--muted)">selection rate (share of candidate tests run)</text>
      <rect x={x(0)} y={y(1)} width={x(metaRate) - x(0)} height={y(0.95) - y(1)} fill="rgb(var(--red-rgb) / 0.12)" />
      {floorPts.length > 0 && <path d={line(floorPts)} fill="none" stroke="var(--muted)" strokeWidth={1.5} strokeDasharray="3 3" />}
      <path d={line(oursPts)} fill="none" stroke="rgb(var(--chart-1-rgb))" strokeWidth={2} />
      {oursPts.slice(1).map((p) => (
        <circle key={p.rate} cx={x(p.rate)} cy={y(p.value)} r={3.5} fill="rgb(var(--chart-1-rgb))" stroke="var(--panel)" strokeWidth={2}>
          <title>{`ours: rate ${p.rate} → test recall ${p.value}`}</title>
        </circle>
      ))}
      <circle cx={x(metaRate)} cy={y(0.95)} r={4.5} fill="var(--ink)" stroke="var(--panel)" strokeWidth={2}><title>{`Meta (reported, private): 0.95 at rate ${doc.meta.test_recall.rate}`}</title></circle>
      <text x={x(metaRate) + 7} y={y(0.95) - 6} fontSize={9.5} fill="var(--ink)">Meta {doc.meta.test_recall.rate}</text>
      <text x={8} y={(T + H - B) / 2} fontSize={9} fill="var(--muted)" transform={`rotate(-90 8 ${(T + H - B) / 2})`} textAnchor="middle">test recall</text>
      <text x={x(Number(t.test_recall_95)) + 7} y={y(0.95) + 4} fontSize={9.5} fill="var(--ink)">ours {t.test_recall_95}</text>
      {floor && <text x={x(0.5) + 4} y={y(floor.points[floor.points.length - 1].value) + 12} fontSize={9} fill="var(--muted)">random</text>}
    </svg>
  );
}

/** The base paper (Machalica et al., Meta) against our ranker, in the base paper's own metrics. */
export function MetaCard() {
  const { doc, error } = useDoc<PtsDoc>("pts");
  const t = doc?.targets.find((x) => x.method === OURS);
  return (
    <Card id="card-meta" title="vs Meta (base paper)" source={doc ? `${doc.source}; Meta: ${doc.meta_source}` : "paper/generated/pts_comparison.md"}>
      {error ? <p className="ui m-0 text-sm text-red">{error}</p> : !doc || !t ? <Skeleton /> : (
        <div className="grid gap-3 md:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
          <RateChart doc={doc} />
          <div className="min-w-0">
            <table className="w-full text-sm" data-testid="meta-table">
              <thead><tr className="ui text-left text-2xs uppercase tracking-wide text-muted"><th className="py-1 pr-2 font-medium"><Term k="selection rate">Rate</Term> needed for</th><th className="pr-2 font-medium">Meta</th><th className="font-medium">Ours</th></tr></thead>
              <tbody>
                <tr className="border-t border-rule"><td className="ui py-1.5 pr-2">TestRecall ≥ {doc.meta.test_recall.target}</td><td className="num mono pr-2">{doc.meta.test_recall.rate}</td><td className="num mono font-semibold" data-testid="ours-tr">{t.test_recall_95}</td></tr>
                <tr className="border-t border-rule"><td className="ui py-1.5 pr-2">ChangeRecall ≥ {doc.meta.change_recall.target}</td><td className="num mono pr-2">{doc.meta.change_recall.rate}</td><td className="num mono font-semibold" data-testid="ours-cr">{t.change_recall_999}</td></tr>
              </tbody>
            </table>
            <p className="ui m-0 mt-2 text-xs font-semibold text-muted">Why Meta needs fewer tests</p>
            <ul className="ui m-0 mt-1 list-disc space-y-0.5 pl-4 text-sm">
              <li>Their candidates are already filtered by the build graph.</li>
              <li>They rank build test targets; we rank individual test files.</li>
              <li>They have months of dense, private failure history per test.</li>
            </ul>
          </div>
        </div>
      )}
    </Card>
  );
}

const CHIP: Record<string, string> = {
  better: "border-green text-green", tie: "border-blue text-blue", lower: "border-amber text-amber",
  "different task": "border-rule text-muted", illustration: "border-rule text-muted italic",
};

/** The paper's results-at-a-glance table, row by row, with one verdict chip per row. */
export function GlanceCard() {
  const { doc, error } = useDoc<GlanceDoc>("glance");
  return (
    <Card id="card-glance" title="Results at a glance" source={doc?.source ?? "paper/full/main.tex (tab:glance)"}>
      {error ? <p className="ui m-0 text-sm text-red">{error}</p> : !doc ? <Skeleton rows={6} /> : (
        <div>
          <div className="overflow-x-auto"><table className="w-full text-sm" data-testid="glance-table">
            <thead><tr className="ui text-left text-2xs uppercase tracking-wide text-muted">
              <th className="py-1 pr-3 font-medium">Reference</th><th className="pr-3 font-medium">Metric</th><th className="pr-3 font-medium">Theirs</th>
              <th className="pr-3 font-medium">Ours</th><th className="pr-3 font-medium">Same data</th><th className="font-medium">Verdict</th></tr></thead>
            <tbody>
              {doc.rows.map((r) => (
                <tr key={r.reference} className="border-t border-rule align-top">
                  <td className="ui py-1.5 pr-3 font-medium">{r.reference}</td>
                  <td className="ui pr-3 text-muted">{r.metric}</td>
                  <td className="num mono pr-3 text-xs">{r.theirs}</td>
                  <td className="num mono pr-3 text-xs">{r.ours}</td>
                  <td className="ui pr-3 text-muted">{r.same_data}</td>
                  <td className="ui"><span className={`inline-block whitespace-nowrap rounded-full border px-2 py-0.5 text-2xs font-semibold ${CHIP[r.chip] ?? CHIP["different task"]}`} title={r.verdict}>{r.chip}</span></td>
                </tr>
              ))}
            </tbody>
          </table></div>
          <div className="ui mt-2 flex flex-wrap gap-x-3 gap-y-1 text-xs text-muted">
            <span>Terms:</span><Term k="Recall@10" /><Term k="APFD" /><Term k="selection rate" /><Term k="co-change" /><Term k="binding" /><Term k="flaky" />
          </div>
        </div>
      )}
    </Card>
  );
}
