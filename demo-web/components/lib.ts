"use client";

import { useEffect, useState } from "react";

/** Fetch `/data/<name>.json`; `null` until loaded, and `error` when the file is missing. */
export function useDoc<T>(name: string): { doc: T | null; error: string | null } {
  const [doc, setDoc] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    let live = true;
    fetch(`/data/${name}.json`, { cache: "no-store" })
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`${name}.json: HTTP ${r.status}`))))
      .then((j) => { if (live) setDoc(j as T); })
      .catch((e) => { if (live) setError(String(e)); });
    return () => { live = false; };
  }, [name]);
  return { doc, error };
}

/** The pre-registered E3 sentence of `rq4_repair.md`, read into numbers. Null when the wording changes. */
export function parsePrimary(text: string): null | {
  model: string; variant: string; n: number; r2: [number, number]; r1: [number, number]; r2Only: number; r1Only: number;
  p: string; supported: boolean; interim: boolean;
} {
  const m = /^(\w+) variant, ([\w./-]+), n = (\d+): R2 plausible-fix rate (\d+)\/(\d+) vs R1 (\d+)\/(\d+); R2 only (\d+), R1 only (\d+); exact McNemar one-sided p = ([0-9.e+-]+)/i.exec(
    text.replace(/^Standard/, "standard"));
  if (!m) return null;
  return {
    variant: m[1], model: m[2], n: Number(m[3]), r2: [Number(m[4]), Number(m[5])], r1: [Number(m[6]), Number(m[7])],
    r2Only: Number(m[8]), r1Only: Number(m[9]), p: m[10], supported: /R2 > R1 supported/.test(text), interim: /tasks done/.test(text) && Number(m[3]) < 70,
  };
}
