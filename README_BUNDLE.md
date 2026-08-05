# BlastRadius working files

Drop-in bundle. Place as follows in the repo root:

```
CLAUDE.md                        ← repo root, Claude Code reads it automatically
docs/ROADMAP.md                  ← the 352 KB master (add it yourself)
docs/SCHEMAS.md
docs/DECISIONS.md
docs/TASKS.md
prompts/T0.1a_repo_frame.md
```

## The loop

1. **You → Claude (chat):** a task ID plus what's changed. e.g. `T1.1g. Fixtures at tests/fixtures/logs/, 40 files. Fork at vendor/graphify-br/.`
2. **Claude (chat) → you:** one self-contained prompt.
3. **You → Claude Code:** paste it. One task, one session. Close and commit when green.
4. **You → Claude (chat):** only if it's one of the four escalations below.

## The four escalations — everything else stays in Claude Code

1. **Gate results** (1, 1.5, 2, 3) — each may change the plan
2. **Schema changes** — any column added or renamed
3. **A Decision's revisit trigger firing** — see `docs/DECISIONS.md` right-hand column
4. **Anything Claude Code proposes that isn't in the roadmap** — usually scope creep, occasionally a real gap

## Weekly

Sunday: dashboard numbers + ROADMAP §41.3 health indicators + the `TASKS.md` diff. Twenty minutes.

## This week

ROADMAP §46 items 1–7 only. Prompt order: `T0.1a` (in `prompts/`) → `T0.2a` (verbatim at ROADMAP §34.4 C.1, paste as-is) → `T0.2b` → `T0.3a` → `T0.3b`.

Do not start `T1.1g` until the harvester is running. The 90-day log clock is the only thing in this project that cannot be recovered.
