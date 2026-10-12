"use client";

import { useState, type ReactNode } from "react";

/** A table behind a "Show table" toggle. The table stays in the DOM (hidden), so the page text and the caption and
 * source line below it are unchanged; only the reader's view of the rows is deferred. */
export function ShowTable({ children, label = "table" }: { children: ReactNode; label?: string }) {
  const [open, setOpen] = useState(false);
  return (
    <div>
      <button type="button" onClick={() => setOpen(!open)} aria-expanded={open}
        className="ui min-h-[32px] rounded border border-rule px-3 text-sm text-ink hover:border-muted">
        {open ? `Hide ${label}` : `Show ${label}`}
      </button>
      <div hidden={!open} className="mt-2 overflow-x-auto" tabIndex={open ? 0 : -1} role="region" aria-label="Table, scrolls horizontally">{children}</div>
    </div>
  );
}
