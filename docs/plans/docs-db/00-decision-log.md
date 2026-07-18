# 00 — Decision log (docs-DB enhancement)

Planning session date: 2026-07-18. This log records every decision, the alternatives weighed, the choice, and who decided. The next (implementation) session should treat these as settled unless it finds a concrete blocker — in which case, surface it, don't silently deviate.

Legend for "Decided by": **User** = the user chose it via AskUserQuestion; **Engineer** = Claude decided it as the acting senior engineer, documented here for the user to review/override; **Joint** = converged in discussion.

---

## D1 — Architecture: DB-only replaces the two delta reference files
- **Options:** (a) two-tier — keep the curated delta references as an always-on fast path *and* add the DB as a completeness fallback; (b) DB-only — delete the two delta files, route all current-API knowledge through a searchable DB.
- **Chosen:** (b) DB-only.
- **Rationale:** The user's two goals are (1) stop distillation from silently dropping content and (2) make refresh cheap. A comprehensive, re-buildable DB serves both. The user accepted the tradeoff (see D2 for the mitigation).
- **Decided by:** User (chosen twice: "replace references" then "완전 DB-only").
- **Scope note:** "references" here means the two *delta* files only — `references/deepagents.md` and `references/langchain-langgraph.md`. `references/consultant.md` is the skill's own consulting **process**, not LangChain docs, and **stays** (edited per D8).

## D2 — DB-only's load-bearing mitigation: a forcing function + a tiny gotchas list
- **Problem:** DB-only's failure mode is Claude *skipping* the search and answering from stale memory. Separately, a DB of current docs can show what *exists* but not what was *removed* or what Claude habitually over-reaches for (absence isn't searchable).
- **Chosen:** Two safeguards in SKILL.md — (1) a **forcing function**: an explicit instruction that Claude does not reliably know the current API and must query the DB before proposing or writing any ecosystem code; (2) a **~10-line gotchas list** covering only the blind spots the DB structurally cannot surface (removed `supervisor` package, `.with_fallbacks()` misuse for agents, `create_react_agent`/`AgentExecutor` habits, `instructions=` vs `system_prompt=`, and the intentionally-current model IDs Claude tends to "correct" backward).
- **Decided by:** User (gotchas: "소량 gotchas만 SKILL.md에 남김"); Engineer (forcing function, as the DB-only safety requirement).

## D3 — Corpus scope: core ~187 files only
- **Options:** (a) core only (~187); (b) core + `python/integrations` catalog (~763); (c) everything minus JS.
- **Chosen:** (a) core only. Exact set: `src/oss/{langchain,langgraph,deepagents,concepts,reference}` + `src/oss/python/{migrate,releases}`. Verified counts (2026-07-18): langchain 73, langgraph 42, deepagents 53, concepts 4, reference 9, migrate+releases 6 = **187**.
- **Excluded:** `javascript/` (Python skill — including JS risks Claude emitting JS as Python); `python/integrations/` (579 files — a parts catalog, marginal for agent *design*, 4× the size).
- **Rationale:** Highest signal-to-noise; small enough to ship. Corpus scope is enforced at **build time** by the selection globs, independent of what is cloned (see D4).
- **Decided by:** User.

## D4 — Clone the whole repo; select at build time
- **Options:** (a) copy only `src/oss/` + `src/snippets/`; (b) `git clone` the whole `langchain-ai/docs` repo.
- **Chosen:** (b) whole repo (the user already did this into `.tmp/docs_langchain`, 583 MB).
- **Rationale:** "What we clone" ≠ "what we index." The clone lands only in `.tmp/` (gitignored, throwaway). Cloning everything **guarantees snippets are present** (they live at `src/snippets/`, outside the old `src/oss/`-only copy — which is exactly why the first snapshot was missing them) and removes a fragile "copy these subdirs" step, making refresh a single `git clone --depth 1`.
- **Decided by:** User ("레포 전체를 가져올까?" → yes).

## D5 — Snippet resolution is mandatory in the build
- **Finding:** Core MDX files render code via `import X from '/snippets/code-samples/*.mdx'` + `<X />` tags. In the `src/oss`-only snapshot these files were absent, so distilled docs lost their actual code. With the full clone, `src/snippets/code-samples/` exists (900 files) and the referenced files resolve (verified: `dynamic-subagents-quickstart-py.mdx` is real `<CodeGroup>` code).
- **Chosen:** The build script MUST resolve every `import ... from '/snippets/...'` + `<Name />` into inlined content before storing `body`. A doc stored with an unresolved `<Name />` tag is a build error.
- **Decided by:** Engineer (mechanical requirement).

## D6 — Storage: single SQLite file with FTS5 + relational metadata
- **Options:** (a) SQLite FTS5 + helper script; (b) raw `.mdx` folder + ripgrep; (c) embedding/semantic vector search.
- **Chosen:** SQLite (`docs_official.db`) — one `docs` table (relational metadata: package, tag, url, path) + a `docs_fts` FTS5 virtual table over the body + a `changelog` table + a `meta` provenance/version table.
- **Rationale:** Honors the user's "clean schema + Claude writes SQL" model. FTS5 is the body-search component that plain SQL `LIKE` can't do well (ranking, tokenization). Embedding search rejected: needs an embedding model + API key + cost, fragile to ship in a plugin. Ripgrep-only rejected: no ranking/metadata filtering, ships a folder not a file.
- **Decided by:** Joint (user favored the schema+SQL model; engineer folded FTS5 in as the text-search part).

## D7 — Query interface: Claude writes raw SQL via the `sqlite3` CLI
- **Options:** (a) Claude writes SQL directly against `sqlite3`; (b) a `query_docs.py` helper wrapper.
- **Chosen:** (a). SKILL.md documents the schema and 3–4 canonical example queries; Claude issues SQL through the `sqlite3` CLI in Bash.
- **Rationale:** Matches the user's vision, zero extra code to maintain, maximally flexible. The one cost — FTS5 `MATCH` syntax quirks — is handled by giving worked examples in SKILL.md.
- **Decided by:** User.

## D8 — `consultant.md` stays but is re-pointed to the DB
- The consult path currently instructs "read `references/deepagents.md` / `references/langchain-langgraph.md` before proposing." Those files are being deleted (D1), so `consultant.md`'s "Reference-usage discipline" must be rewritten to "query `docs_official.db` before proposing/writing." No other consultant behavior changes.
- **Decided by:** Engineer (follows mechanically from D1).

## D9 — Evidence/probe framework: retire & lighten
- **Context:** `scripts/validate_evidence.py` pins `SKILL.md`'s SHA256 in `docs/plans/research/probe-codex-results.json` and enforces the deltas-only justification. Under DB-only there is no per-API delta-selection to justify.
- **Options:** (a) retire/lighten; (b) keep and re-purpose probes to measure "Claude + DB produces correct code"; (c) keep as-is and just re-stamp the hash.
- **Chosen:** (a). Retire the delta-justification role: remove the SKILL-hash pin, **preserve** the historical probe records under `docs/plans/research/` as-is (they're a real record of the v1.0.0/v1.1.0 measurements), and replace the check with a lightweight **DB-build validation** (schema present, row counts sane, zero unresolved `<Snippet/>` tags, FTS query returns hits, version stamp present).
- **Decided by:** User ("은퇴·경량화").

## D10 — Release mechanics
- **SemVer:** user-facing capability change → **minor bump to v1.2.0**. `plugin.json` version and a matching `## [1.2.0]` CHANGELOG heading are required (enforced by validate_evidence.py's remaining checks).
- **Plugin mirror:** `plugins/skills-for-langchain/skills/langchain/` is a byte-identical **copy** (not a symlink). Every changed skill file **and the new `.db`** must be mirrored; verify with `diff -rq`. This roughly doubles the committed `.db` size in the repo.
- **Decided by:** Engineer (repo conventions from the prior release; see memory `consultant-enhancement-plan`).

## D11 — Engineer-set build defaults (open to override by the implementer/user)
These were not put to the user individually; they are reasonable senior-engineer defaults, logged for review:
1. **`.db` location:** `.claude/skills/langchain/references/docs_official.db` (and the mirror). `references/` will then hold `consultant.md` + the DB.
2. **Body format:** store lightly-cleaned Markdown — inline all snippets (D5), and **strip `:::js ... :::` conditional blocks** while keeping `:::python` (Python-only skill; this also removes JS/Python confusion, the same reason JS docs are excluded). Keep `<Note>/<Tip>/<Warning>` prose and inline `bash` blocks.
3. **URL mapping:** `src/oss/<rest>.mdx` → `https://docs.langchain.com/oss/<rest>` (strip `src/`, strip `.mdx`).
4. **Chunking:** store **whole docs** (one row per file). 187 docs averaging ~18 KB is small; whole-doc reads are fine and simpler than section-splitting. Revisit only if retrieval returns unwieldy blobs.
5. **Committed binary:** the `.db` is a committed binary (plugins ship as-is with no install-time build step). Accept modest git-history growth on refresh; use `--depth 1` clones and don't commit `.tmp/`.
- **Decided by:** Engineer (flagged for user review).
