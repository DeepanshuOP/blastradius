"use client";

import { createContext, useContext, useEffect, useId, useRef, useState, type ReactNode } from "react";

/** The Explain switch of the top bar. Off by default: the main screen carries no explanations until a reader asks. */
export const ExplainContext = createContext(false);
export const useExplain = () => useContext(ExplainContext);

export const reducedMotion = () =>
  typeof window !== "undefined" && Boolean(window.matchMedia?.("(prefers-reduced-motion: reduce)").matches);

/** A sentence that exists only while Explain is on (it is not in the DOM otherwise). */
export function Explain({ children, className = "" }: { children: ReactNode; className?: string }) {
  return useExplain() ? <p className={`cap m-0 ${className}`}>{children}</p> : null;
}

/** An "i" button that opens a small popover (Esc, a click outside, or the button closes it). */
export function Info({ label = "More", children, className = "", align = "left", up = false }: {
  label?: string; children: ReactNode; className?: string; align?: "left" | "right"; up?: boolean;
}) {
  const [open, setOpen] = useState(false);
  const id = useId();
  const root = useRef<HTMLSpanElement>(null);
  useEffect(() => {
    if (!open) return;
    const off = (e: MouseEvent) => { if (!root.current?.contains(e.target as Node)) setOpen(false); };
    const key = (e: KeyboardEvent) => { if (e.key === "Escape") setOpen(false); };
    document.addEventListener("mousedown", off);
    document.addEventListener("keydown", key);
    return () => { document.removeEventListener("mousedown", off); document.removeEventListener("keydown", key); };
  }, [open]);
  return (
    <span ref={root} className={`relative inline-flex align-middle ${className}`}>
      <button type="button" onClick={() => setOpen(!open)} aria-expanded={open} aria-controls={open ? id : undefined} aria-label={label}
        className="info-btn ui inline-grid h-[22px] w-[22px] place-items-center rounded-full border border-rule text-2xs font-semibold italic text-muted hover:border-muted hover:text-ink">i</button>
      {open && (
        <span id={id} role="note" className={`ui absolute ${up ? "bottom-[28px]" : "top-[26px]"} z-40 block ${up ? "w-[30rem] text-base" : "w-72 text-xs"} rounded-md border border-rule bg-panel p-3 text-left font-normal normal-case leading-snug tracking-normal text-ink shadow-[0_8px_28px_rgb(0_0_0/0.45)] ${align === "right" ? "right-0" : "left-0"}`}>
          {children}
        </span>
      )}
    </span>
  );
}

/** A number that counts up to its value when the value changes (an event arrived); never on first paint. */
export function Counter({ value, format, className = "" }: { value: number; format?: (n: number) => string; className?: string }) {
  const [shown, setShown] = useState(value);
  const prev = useRef(value);
  useEffect(() => {
    if (prev.current === value) return;
    const from = prev.current;
    prev.current = value;
    if (reducedMotion() || value < from) { setShown(value); return; }
    const t0 = performance.now();
    let raf = 0;
    const step = (t: number) => {
      const k = Math.min(1, (t - t0) / 650);
      setShown(Math.round(from + (value - from) * (1 - (1 - k) ** 3)));
      if (k < 1) raf = requestAnimationFrame(step);
    };
    raf = requestAnimationFrame(step);
    return () => cancelAnimationFrame(raf);
  }, [value]);
  return <span className={`num mono ${className}`}>{(format ?? ((n: number) => n.toLocaleString()))(shown)}</span>;
}
