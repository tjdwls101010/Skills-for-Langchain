# 01 — Overview

## The problem this solves

The `langchain` skill (v1.1.0) carries current-API knowledge as **hand-distilled delta references** — `references/deepagents.md` and `references/langchain-langgraph.md` — plus inline corrections in `SKILL.md`. Two structural weaknesses surfaced:

1. **Distillation silently drops content.** Example measured this session: `deepagents/dynamic-subagents.mdx` is a 369-line doc with 10+ orchestration patterns (tournament, loop, adversarial, fan-out, …); the delta reference compresses it to a single section header. The substance evaporated. No distillation process can guarantee it won't happen again.
2. **Refresh is expensive.** Updating on a new Claude release or a LangChain update means re-running blind probes and re-curating by hand.

## The shift

Replace the two delta reference files with a **searchable database of the current official docs** (`docs_official.db`), which Claude queries with SQL before proposing or writing any LangChain-ecosystem code.

- **Completeness:** the DB holds the full body of the core docs (with code snippets inlined), so nothing is pre-dropped.
- **Cheap refresh:** re-clone the docs repo, re-run one build script, re-stamp the version. No manual re-curation.

This is a deliberate philosophy change: from *curated-deltas-in-context* to *full-docs-on-demand-via-search*. The skill's **two behaviors are unchanged** — it is still (a) a solutions **consultant** on an abstract agent-building goal, and (b) a passive **current-API guide** when editing existing code. Only the *knowledge substrate* changes.

## Architecture

```
                    ┌─────────────────────────────────────────┐
                    │ SKILL.md  (always loaded)                │
                    │  • consultant posture + 10 dimensions    │
                    │  • FORCING FUNCTION: "you don't know the │
                    │    current API — query the DB first"     │
                    │  • ~10-line gotchas (removed/traps —     │
                    │    the DB can't surface these)           │
                    │  • DB schema + example SQL queries       │
                    └───────────────┬─────────────────────────┘
                                    │ query before proposing/writing code
                                    ▼
      ┌──────────────────────────────────────────────────────────┐
      │ references/docs_official.db  (SQLite, shipped in plugin)  │
      │   docs(id,path,package,title,tag,url,body)                │
      │   docs_fts   ── FTS5 over (title, body)                   │
      │   changelog(date,package,version,summary)                 │
      │   meta(snapshot_date,built_at,source_repo,source_commit)  │
      └──────────────────────────────────────────────────────────┘
                                    ▲
                                    │ built by (refresh workflow)
      ┌──────────────────────────────────────────────────────────┐
      │ scripts/build_docs_db.py                                  │
      │   git clone --depth 1 langchain-ai/docs → .tmp (gitignore)│
      │   select core ~187 files → resolve /snippets imports      │
      │   → strip :::js → parse changelog → write docs_official.db │
      └──────────────────────────────────────────────────────────┘

  references/consultant.md          (stays; "read delta ref" → "query DB")
```

## Scope

**In scope**
- New `scripts/build_docs_db.py` (stdlib-only) that produces `docs_official.db`.
- The built `docs_official.db` committed under `references/` (+ plugin mirror).
- `SKILL.md` rewrite: forcing function, gotchas list, DB schema + example queries, "Staying current" rewritten to the DB-refresh workflow; remove the delta-file pointers and the bulk inline corrections.
- `references/consultant.md` edit: re-point reference-usage discipline to the DB.
- Delete `references/deepagents.md` and `references/langchain-langgraph.md`.
- Lighten the evidence framework (D9); v1.2.0 release mechanics (D10).

**Out of scope / non-goals**
- No embedding/semantic search, no external services, no network calls at skill runtime.
- No `python/integrations` catalog, no JavaScript docs.
- No change to the consultant *interview* behavior or the ten dimensions.
- No install-time build step — the `.db` ships prebuilt.

## Success criteria

1. `build_docs_db.py` produces a `docs_official.db` with ~187 doc rows, **zero unresolved `<Snippet/>` tags**, a populated `changelog` table, and a `meta` version stamp.
2. A blind spot that failed before now succeeds: `SELECT body FROM docs WHERE path LIKE '%dynamic-subagents%'` returns the full doc **including** the inlined `<CodeGroup>` Python code.
3. `SKILL.md` instructs the query-first behavior, carries the schema + working example queries, and keeps the gotchas list; the two delta files are gone and nothing points to them.
4. `validate_harness.py` exits 0; the lightweight DB-build validation passes; `plugin.json`/CHANGELOG at v1.2.0; plugin mirror `diff -rq` clean.
