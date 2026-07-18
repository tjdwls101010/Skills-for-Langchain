# 05 — SKILL.md & references rewrite

## Files touched

- **Rewrite:** `.claude/skills/langchain/SKILL.md`
- **Edit:** `.claude/skills/langchain/references/consultant.md`
- **Delete:** `.claude/skills/langchain/references/deepagents.md`, `.claude/skills/langchain/references/langchain-langgraph.md`
- **Add (built artifact):** `.claude/skills/langchain/references/docs_official.db`
- Mirror all of the above into `plugins/skills-for-langchain/skills/langchain/...`.

## SKILL.md — what changes

Keep unchanged: the frontmatter `description` (still accurate — it already frames the skill as consultant + current-API guide; do **not** narrow it), the "Consult or deltas — decide which behavior" section, the consultant posture, the ten dimensions, "Orient by layer."

**Replace** the current knowledge-substrate sections — "Reference-usage discipline", "Deltas-only knowledge", "Cross-cutting corrections", "Load the relevant reference", "Staying current" — with:

### (a) Forcing function (new, prominent, near the top of the knowledge section)
Wording to convey (adapt prose, keep the conviction + the why):
> You do **not** reliably know the current LangChain / LangGraph / Deep Agents API. Your training predates the releases this skill targets, and several APIs you "remember" have changed or been removed. Before you propose an architecture or write, edit, or review any ecosystem code, **query `references/docs_official.db`** for every API you are about to rely on, and treat the DB — not your memory — as ground truth. The gotchas below are the one exception: they cover things the DB *cannot* show you, so internalize them directly.

### (b) Gotchas the DB can't surface (~10 lines — the irreplaceable residue of the old delta files)
- **`create_deep_agent` uses `system_prompt=`, not `instructions=`** (the latter `TypeError`s). Declarative subagent specs likewise use `system_prompt`, not `prompt`.
- **`from langchain.agents import create_agent`** — not `create_react_agent`, `AgentExecutor`, or `initialize_agent`, and no extra `.compile()` (it returns a compiled graph).
- **The `supervisor` package was removed.** For multi-agent coordination use subagents or the agent-as-tool pattern; do not import a supervisor package.
- **Model fallback is middleware**, not agent `.with_fallbacks()`.
- **Pass the model explicitly** as a `provider:model` string (`init_chat_model`), e.g. `"anthropic:claude-sonnet-4-6"`. IDs like `claude-sonnet-4-6`, `claude-opus-4-8`, `gpt-5.5`, `gemini-3.5-flash` are **current and intentional — do not "correct" them backward.**

(These mirror the current SKILL.md cross-cutting corrections + the removed-supervisor/`.with_fallbacks()` traps from the deleted delta files. This is the *only* curated knowledge that survives, precisely because absence/removal isn't searchable.)

### (c) How to query the DB (schema + examples)
Embed the `docs` / `docs_fts` / `changelog` / `meta` shape (compact) and the five canonical queries from `03-db-schema.md`, plus the FTS5 `MATCH` syntax notes and the `sqlite3 -readonly <relative path>` invocation. This is what makes "Claude writes SQL" actually work.

### (d) "Staying current" — rewrite to the DB-refresh workflow
Replace the probe-based refresh description with: re-clone `langchain-ai/docs`, run `scripts/build_docs_db.py`, eyeball the report, re-stamp `meta`, bump the version, update CHANGELOG, mirror + `diff -rq`. Point to `docs/plans/docs-db/` for the full procedure.

### Removed pointers
Delete every mention of `references/deepagents.md` and `references/langchain-langgraph.md` (there are several — in "Reference-usage discipline", "Load the relevant reference", and "If one task crosses both branches"). `validate_harness.py` will flag any dangling pointer; treat a clean run as the check.

## consultant.md — what changes

One section: **"Reference-usage discipline"** (it currently says "read `references/deepagents.md` / `references/langchain-langgraph.md` before proposing/writing"). Re-point it to: "before proposing an architecture or writing code, **query `references/docs_official.db`** for the APIs involved (see SKILL.md for schema + example queries); treat the DB as ground truth over your memory, and apply the SKILL.md gotchas for removed/renamed APIs the DB can't show." Leave the interview protocol, the ten-dimension expansion, the build/agreement rules, and the worked example **unchanged** — but scan the worked example for any hard reference to the deleted files and update it if present.

## Verification stamp

The three skill files carried a "verified against the April-2026 snapshot" stamp. Update it to reference the new `meta` snapshot date in the DB (single source of truth), rather than a hand-typed date in prose.
