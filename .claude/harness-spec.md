# Harness Spec — Skills for LangChain

## Context

This repository is a documentation-first Claude Code skill project. It contains no application build system or test runner; its product is a Python-only consultant-plus-current-API skill for LangChain 1.x, LangGraph 1.x, and the Deep Agents SDK.

As of **v1.2.0** the skill's knowledge substrate is a searchable database of the current official docs — `references/docs_official.db` (SQLite + FTS5) — that Claude queries with SQL before proposing or writing ecosystem code. This replaced the two hand-distilled delta references (`deepagents.md`, `langchain-langgraph.md`) that v1.0.0/v1.1.0 shipped; those files, and the deltas-only philosophy behind them, are retired. The DB is rebuilt from a `git clone` of `langchain-ai/docs` by `scripts/build_docs_db.py`. The planning basis is `docs/plans/docs-db/` (00–07); the historical probe evidence under `docs/plans/research/` is preserved as a record of how the v1.0.0/v1.1.0 correction knowledge was measured, but is no longer the live substrate. The measured consumer baseline remains Claude Opus 4.8 with a January 2026 knowledge cutoff.

Generated harness content is written in English to preserve API terminology and reduce translation drift. The interview and handoff remain in Korean.

The existing `CLAUDE.md` contains general engineering guidance plus one pointer to this spec. No user-scope `~/.claude/CLAUDE.md` exists, so there is no concatenation conflict to resolve.

## Goals

Original goals (v1.0.0/v1.1.0), still in force except where the v1.2.0 substrate change supersedes them:

- Keep the skill a Python-only consultant + current-API guide for the LangChain ecosystem, with Deep Agents as the center of gravity.
- Preserve progressive disclosure with one short always-loaded `SKILL.md` and depth loaded on demand.
- Package the same canonical skill as a public Claude Code plugin and marketplace with a byte-verified release copy that cannot drift silently.

v1.2.0 goals (docs-DB substrate; supersedes "deltas-only" curation):

- Stop distillation from silently dropping content: hold the **full body** of the ~187 core docs (with code snippets inlined) in a searchable DB, so nothing is pre-dropped by hand-curation.
- Make refresh cheap: re-clone `langchain-ai/docs`, run one build script, re-stamp the version — no manual re-probing or re-curation.
- Make the query-first behavior load-bearing: a `SKILL.md` forcing function plus a compact gotchas list for the removed/renamed APIs the DB structurally cannot surface.

## Behavior inventory

| id | behavior/knowledge/constraint | layer | component | status |
|----|-------------------------------|-------|-----------|--------|
| B1 | Auto-trigger for Python work involving LangChain, LangGraph, or Deep Agents, while excluding unrelated agent frameworks and raw provider SDK work. | skill | `.claude/skills/langchain/` | validated |
| B2 | Orient the model around LangChain as framework, LangGraph as runtime, and Deep Agents as harness. | skill | `.claude/skills/langchain/SKILL.md` | validated |
| B3 | Gotcha: `create_deep_agent(instructions=...)` and legacy subagent `prompt` are wrong; use `system_prompt`. | skill | `.claude/skills/langchain/SKILL.md` (gotchas) | validated |
| B4 | Gotcha: preserve current-looking model IDs and require an explicit `provider:model` string or `BaseChatModel`. | skill | `.claude/skills/langchain/SKILL.md` (gotchas) | validated |
| B5 | Gotcha: `langchain.agents.create_agent` is the already-compiled baseline, not `create_react_agent`/`AgentExecutor`/`initialize_agent`; and model fallback is middleware, not `.with_fallbacks()`; the `supervisor` package was removed. | skill | `.claude/skills/langchain/SKILL.md` (gotchas) | validated |
| B42 | Knowledge substrate is `docs_official.db` — the full body of the ~187 core docs (langchain, langgraph, deepagents, concepts, reference, migrate, releases) with every `/snippets` code sample inlined, searchable via SQL/FTS5. Nothing is pre-dropped by curation. | skill | `.claude/skills/langchain/references/docs_official.db` | validated |
| B43 | Forcing function: the model does not reliably know the current API and must query the DB (ground truth over memory) before proposing an architecture or writing/editing/reviewing ecosystem code. | skill | `.claude/skills/langchain/SKILL.md` | validated |
| B44 | Carry the DB schema, five canonical FTS5 example queries, the MATCH-syntax notes, and the `sqlite3 -readonly` invocation so "Claude writes SQL" actually works. | skill | `.claude/skills/langchain/SKILL.md` | validated |
| B45 | Build the DB deterministically from a `langchain-ai/docs` clone: recursive `/snippets` inlining, `:::js` stripping (keep `:::python`), changelog parse, provenance `meta` stamp; fail the build on any unresolved snippet tag. | script | `scripts/build_docs_db.py` | validated |
| B46 | Lightweight DB-artifact validation: schema present, row count in band, zero unresolved snippet tags, snippet-inlining regression, FTS returns hits, `meta` populated. | script | `scripts/validate_docs_db.py` | validated |
| B31 | Version-stamp the DB (`meta.snapshot_date`, `source_commit`) and carry a one-command refresh workflow (re-clone → build → validate → bump → mirror) instead of a probe-based refresh. | skill | `.claude/skills/langchain/SKILL.md` ("Staying current") + scripts | validated |
| B32 | Point project-level sessions to this spec without duplicating a component inventory in `CLAUDE.md`. | CLAUDE.md | `CLAUDE.md` | validated |
| B34 | Publish a byte-verified release copy of the canonical project skill — including `docs_official.db` — through a strict Claude Code plugin manifest with SemVer metadata. | plugin | `plugins/skills-for-langchain/` | validated |
| B35 | Expose the repository as an installable same-repository Claude Code marketplace using stable public identifiers. | marketplace | `.claude-plugin/marketplace.json` | validated |
| B36 | Enter consultant mode on an abstract agent-building goal (outcome/automation/answer-from-data), even with no framework named and no code shown, and interview before proposing. | skill | `.claude/skills/langchain/SKILL.md` + `references/consultant.md` | validated |
| B37 | Preserve the current-API path: existing LangChain-ecosystem code work still gets silent correction with no interview — now by querying the DB for the APIs in play (no v1.0.0 regression). | skill | `.claude/skills/langchain/SKILL.md` | validated |
| B38 | Broaden the trigger to natural-language goals while keeping the CrewAI/AutoGen/LlamaIndex/raw-SDK near-miss boundary explicit. | skill | `.claude/skills/langchain/SKILL.md` description | validated |
| B39 | Supply a thin ten-dimension checklist of what to ask about (each naming the decision it drives), not a goal-to-architecture decision tree. | skill | `.claude/skills/langchain/SKILL.md` + `references/consultant.md` | validated |
| B40 | Enforce the agreement gate: design is always free, implementation waits for an explicit go-ahead, and build scope (code-only vs runnable scaffold vs full project) is agreed per case. | skill | `.claude/skills/langchain/references/consultant.md` | validated |
| B41 | Require querying the DB (not memory) before proposing or coding so proposals reflect the current API, not pre-cutoff reflexes. | skill | `.claude/skills/langchain/SKILL.md` + `references/consultant.md` | validated |

Retired in v1.2.0: **B6–B30 and B33** were per-topic curated deltas authored into `references/deepagents.md` and `references/langchain-langgraph.md`. Both files were deleted and the knowledge is now carried in full by the DB (B42); the ids are retired rather than remapped so the history stays legible. The irreplaceable residue — removed/renamed APIs that a search over *current* docs cannot surface — survives as the gotchas B3–B5.

## Component specs

### `.claude/skills/langchain/SKILL.md`

- Frontmatter name: `langchain`.
- Invocation contract: `/langchain` standalone and `/skills-for-langchain:langchain` when installed from the marketplace, derived from the directory name.
- Description: consultant clause first (design/build an agent, automate a task, answer from data — even with no framework named and no code shown), then the current-API triggers for LangChain, LangGraph, and Deep Agents Python work; explicit near-miss boundary for CrewAI, AutoGen, LlamaIndex, and raw OpenAI or Anthropic SDK usage unless bridged through LangChain. Description was **not** narrowed in v1.2.0 — it already framed the skill as consultant + current-API guide, which the DB substrate preserves.
- Invocation policy: model-invocable and user-invocable; no `disable-model-invocation`, `allowed-tools`, hooks, or forked context. The consultant is an interactive main-thread conversation, and pre-approving Write/Edit would surprise users during a design-only conversation (the agreement gate, B40, governs when files are written).
- Body (v1.2.0 rewrite): the consultant gist first (identity, the consult-vs-current-API branch B37, the compact persona, the thin ten-dimension checklist B39), then the knowledge-substrate sections — the **forcing function** (B43, query the DB first), the three-layer mental model, the **gotchas** the DB can't surface (B3–B5), the **"How to query the DB"** block (B44: schema, five example FTS5 queries, MATCH notes, `sqlite3 -readonly` invocation), and **"Staying current"** (B31, the DB-refresh workflow). The prior deltas-only knowledge sections ("Reference-usage discipline", "Deltas-only knowledge", "Cross-cutting corrections", "Load the relevant reference", the probe-based "Staying current") were removed; no pointer to the deleted delta files remains.

### `.claude/skills/langchain/references/consultant.md`

- Read only on the consult path (progressive disclosure per consultant DC8): the interview walkthrough, the ten-dimension checklist expanded as principles, the build rules, and one worked example — none of it needed on the current-API path, which is why it lives here rather than in the always-loaded SKILL.md.
- Consulting process and posture only; it re-teaches no LangChain API (consultant DC4). v1.2.0 re-pointed it: each dimension's "*Find in the DB:*" clause names the package/topic to search (was "*Informs from:* deepagents.md / langchain-langgraph.md"), and the persona/build-rules/worked-example say "query `docs_official.db`" (was "read the delta reference"). Interview protocol, ten dimensions, and agreement gate otherwise unchanged.
- Contents in order: the persona (full), the interview protocol (divergent-open / convergent-AskUserQuestion, plus the every-question-must-move-the-design test), the expanded dimension checklist, the agreement-gate build rules, and one worked example dialogue.
- Not covered by the v1.0.0 probe suite; consult quality is judgment, validated by behavioral dry-run rather than a probe flip-rate (consultant DC10).

### `.claude/skills/langchain/references/docs_official.db` (v1.2.0)

- Single SQLite file, FTS5 required. Tables: `docs(id, path, package, title, tag, url, body)`, `docs_fts` (external-content FTS5 over title+body, porter/unicode61, kept in sync by triggers), `changelog(date, package, version, summary)`, `meta(key, value)`.
- Corpus = the ~187 core docs only: `src/oss/{langchain,langgraph,deepagents,concepts,reference}` + `src/oss/python/{migrate,releases}`. JavaScript docs and `python/integrations` (the parts catalog) are excluded at build-time by the selection globs — a Python-only skill must never surface JS as Python.
- `body` is lightly-cleaned Markdown: all `/snippets` imports inlined (recursively — some snippets import further snippets), `:::js` conditional blocks stripped while `:::python` is unwrapped, `<Note>/<Tip>/<Warning>` prose and `<CodeGroup>` provider variants kept. The only mandatory transforms are snippet inlining and `:::js` removal; cleaning is otherwise conservative.
- Committed as a binary (~4.4 MB) under `references/` and mirrored into the plugin — plugins ship prebuilt with no install-time build step. Rebuilt by `scripts/build_docs_db.py`; **not** `.gitignore`d.
- Claude queries it read-only via the `sqlite3` CLI; the schema and worked queries live in `SKILL.md` (B44), not only in the DB.

### `scripts/build_docs_db.py` (v1.2.0)

- Stdlib-only Python 3.10+, no network at build time (the `git clone` is a separate step). Deterministic and idempotent on a fixed clone.
- CLI: `--src <clone> --out <db> [--commit <sha>] [--mirror <path>]`. Preflights that the running `sqlite3` has FTS5; builds to a temp file, self-validates, then atomically moves to `--out`.
- Pipeline: index `src/snippets/` → select corpus by glob → per file split frontmatter, **recursively** inline `/snippets` imports (missing target or cycle → hard build error), strip `:::js` via a **colon-count fence stack** (mintlify nests conditionals with more colons, e.g. `::::::js` around inner `:::`), compute the canonical `docs.langchain.com` URL → parse the changelog → stamp `meta` → optimize/vacuum → self-validate → report per-package counts and snippet substitutions.
- Residual check is scoped to *imported* names, not a blanket self-closing-tag regex, so legit JSX in code examples (e.g. `<LoadingIndicator />`) is preserved.

### `scripts/validate_docs_db.py` (v1.2.0)

- Stdlib-only; opens the shipped artifact read-only and asserts: the four tables exist, `doc_count` in the 150–250 band, changelog non-empty, no leftover `/snippets` import lines, no `:::js` leakage, the dynamic-subagents snippet-inlining regression (`create_deep_agent(` present in that body), `docs_fts MATCH 'agent'` returns rows, and `meta` is fully populated. Exits non-zero on the first failure.

### `CLAUDE.md`

- Preserve the existing general engineering guidance.
- Add one concise pointer to `.claude/harness-spec.md` and one trigger-oriented sentence for loading current LangChain-ecosystem knowledge.
- Do not enumerate reference topics or components; the filesystem and this spec remain the inventory sources of truth.

### `plugins/skills-for-langchain/.claude-plugin/plugin.json`

- Stable plugin name: `skills-for-langchain`; display name: `Skills for LangChain`.
- Explicit SemVer is the release cache key and must be bumped with every published release.
- The plugin root is `plugins/skills-for-langchain/`, isolating the package from project-only `CLAUDE.md` and other harness files so direct strict validation passes.
- The packaged `skills/langchain/` files mirror the canonical `.claude/skills/langchain/` files, verified byte-for-byte with `diff -rq` on every skill edit (consultant DC9). As of v1.2.0 the mirror is `SKILL.md` + `references/consultant.md` + `references/docs_official.db` (the `.db` is committed in both places — accepted binary duplication). `scripts/validate_evidence.py` was slimmed in v1.2.0 to check SemVer↔CHANGELOG coupling and full-tree mirror byte-identity (walking the whole skill tree); it no longer pins `SKILL.md`'s hash, since SKILL.md is rewritten on every DB refresh.
- The explicit SemVer bump for a user-facing capability is at least a minor version: v1.1.0 added the consultant behavior; v1.2.0 replaced the knowledge substrate (delta files → `docs_official.db`).
- Metadata links to the public repository, MIT license, and maintainer identity.

### `.claude-plugin/marketplace.json`

- Stable marketplace name: `skills-for-langchain`.
- The single entry uses `source: "./plugins/skills-for-langchain"`, so users must add the GitHub repository or a git/local checkout rather than a raw marketplace JSON URL.
- The marketplace entry intentionally omits `version`; `plugin.json` is the sole version authority.
- `strict: true` makes the plugin manifest authoritative for component discovery.

### Components deliberately not generated

- No rules: the knowledge is task-triggered, not path-specific, and there is no application tree to target with `paths:` globs.
- No hooks or permissions: no requirement must deterministically block an action, and hooks would add latency without enforcing a project safety boundary.
- No agents: this is reference knowledge, not a read-heavy role whose exploration should be isolated.
- No workflows: implementation and future refreshes vary with the measured delta set; a fixed orchestration would freeze the wrong shape.

## Design rationale

One skill is the correct consolidation boundary because all included behaviors share one user intent: writing current Python for the LangChain ecosystem. Multiple skills would spend shared description budget and create competing triggers.

The knowledge substrate is a searchable DB queried on demand, not curated deltas in context (v1.2.0). The prior two-reference split (a fat Deep Agents file, a thin LangChain/LangGraph file) was a distillation, and distillation silently dropped content — measured: `deepagents/dynamic-subagents.mdx`'s ten-plus orchestration patterns and their code compressed to a single header. A DB of the full docs (snippets inlined) can't pre-drop what it stores, and refresh is one build script instead of a re-probing cycle. Raw SQL via `sqlite3` (not a `query_docs.py` wrapper) matches the "clean schema + Claude writes SQL" model and adds zero code to maintain; its one cost — FTS5 MATCH quirks — is covered by worked examples in SKILL.md.

The load-bearing risk of DB-only is the model *skipping* the query and answering from stale memory, and that a DB of current docs shows what *exists* but not what was *removed*. Two safeguards address it: a SKILL.md forcing function (B43) and a compact gotchas list (B3–B5) for exactly the removed/renamed APIs a search over current docs structurally cannot surface. This is the only curated knowledge that survives the substrate change, precisely because absence isn't searchable. The former empirical content boundary (excluding topics the 38 probes graded correct) no longer applies — the DB carries everything, and the gotchas are scoped to un-searchable absences rather than to probe verdicts.

Advisory knowledge belongs in a skill, not in hooks or permissions. The task requires better judgment when an ecosystem request appears, not deterministic interception of a tool call or path.

The v1.1.0 consultant is a second *behavior* over the same one skill and the same shared knowledge, not a second skill (consultant DC1). Two skills would duplicate the knowledge or spend competing description budget; one auto-triggering skill that branches in its body keeps the current-API path intact (DC2) while letting a natural-language goal enter consultant mode (DC3). The consultant's content is deliberately process, not more knowledge (DC4): a capable model already designs conceptually sound architectures, and the gap it has — the current API at implementation time — is closed by querying the DB (v1.2.0; formerly the two frozen delta references), so the consultant adds only a persona, a thin dimension checklist (DC5), and the discipline to query the DB before proposing (B41). The interview walkthrough and worked example split into `references/consultant.md` because they are needed only inside a consult, never on the always-loaded current-API path (DC8). The agreement gate (DC6) mirrors the hard side-effect boundary of harness authoring: design always, implement only on an explicit go-ahead, scope agreed per case. Validation is honestly lighter than v1.0.0's probe suite because consult quality is a judgment call, not a mechanically gradable fact (DC10).

## Validation

### Free deterministic checks

- Run the harness-creator validator after each component-writing pass and again after the change history and CLAUDE.md pointer are final. Delivery requires zero errors; strict mode should also be reviewed so warnings are intentional.
- Re-read the final skill description against positive and near-miss prompts in `docs/plans/05-validation.md`, because structural validation cannot grade trigger quality.
- Check every backticked `references/...` pointer resolves and keep the `SKILL.md` body under the validator's 500-line guideline.
- Validate the marketplace and plugin manifests separately with `claude plugin validate <manifest> --strict`, then run an isolated marketplace add/install/details smoke test before publishing a release.
- Run `python3 scripts/validate_docs_db.py` after every DB build (schema, row-count band, zero unresolved snippets, snippet-inlining regression, FTS hits, `meta` populated).
- Run `python3 scripts/validate_evidence.py` (slimmed in v1.2.0) to verify SemVer↔CHANGELOG coupling and plugin-mirror byte-identity across the whole skill tree, including `docs_official.db`.

### Content verification (historical, v1.0.0/v1.1.0 — superseded by the DB in v1.2.0)

- Verify all 16 Deep Agents and 10 LangChain/LangGraph sections against their cited official `.mdx` sources in `.tmp/docs_langchain/`.
- Pre-generation source audit completed on 2026-07-12: constructor names, middleware parameters, backend security, namespace isolation, context thresholds, subagent fields and tools, HITL, permissions, rubrics, profiles, interpreter semantics, sandbox backends, MCP transport, production invocation, event streaming, error handling, interrupts, and `DeltaChannel` were checked against the local official docs. The pre-generation audit corrected the planned LangSmith sandbox cleanup and MCP source selection. The first after-probe then exposed two additional plan-level precision gaps: async subagent specs must be passed directly through `subagents=` for automatic middleware attachment, and `skills=` entries are top-level source directories rather than individual skill directories. Independent post-probe review also tightened the 20,000-token input-offload precondition and distinguished per-pass rubric results from terminal `max_iterations_reached` state.
- Re-run include-list probe scenarios with the relevant generated skill content injected and require each original `outdated_confident`, `partial`, or `unknown` key delta to disappear.
- Re-run the 11 measured-correct exclusion scenarios as a regression guard; they must remain correct.
- Record the resulting flip rate and any repair iterations in `docs/plans/research/probe-results.md` and this section.

### Results

- `validate_harness.py --path .`: PASS with 0 errors and 0 warnings.
- `validate_harness.py --path . --strict`: PASS with 0 errors and 0 warnings.
- `audit_harness.py --path .`: no component drift, dead links, hook issues, or user-scope conflicts.
- Manual trigger review: the 911-character description covers all seven positive scenarios and explicitly excludes the four near-miss classes in `docs/plans/05-validation.md`; no structural option disables model or user invocation.
- Historical Round-1 first after-pass: 23/26 correct. C6 and C8 revealed real reference gaps; later Codex review established that A2 also contained a real deprecated compatibility call and belonged in scope.
- Round-2 after-pass: 12/12 correct without repair.
- Targeted A2/C6/C8 repair-context retry after reference and prompt repair: 3/3 correct, using concise correction context and a shorter same-schema grader rather than the strict full-suite mechanism.
- Strict full-suite proof using generated files and the original grader: 35/38 correct, comprising 24/27 include-list flips and 11/11 measured-correct exclusions under the corrected baseline; residuals were A2, C6, and C8.
- Historical combined observed result across the strict full suites and separately labeled repair-context retry: 38/38 correct. The attempted historical faithful retry returned HTTP 429 and is not counted as final evidence.
- By explicit user decision, final residual validation used Codex subagents only and did not invoke Claude. Isolated attempts for A2, C6, and C8 embedded the exact current generated-file hashes; two independent official-doc graders per task returned `correct` (6/6), and a separate synthesis reviewer confirmed all attempt/grader hashes and found no material residuals.
- The Codex gate exposed and repaired A2 before its final pass: `ModelRequest.override(system_prompt=...)` is deprecated compatibility behavior. The reference now prefers `@dynamic_prompt`, or `request.override(system_message=SystemMessage(...))` when full wrapper control is required.
- Independent Codex API audit against the official snapshot passed after correcting summarization-helper wiring, interpreter import, rubric naming, model fallback wording, delete version gates, and sandbox path precision. The final split review also separated `deepagents deploy` from direct `langgraph deploy`, corrected stateful MCP sessions to `client.session("server_name")`, preserved "LangGraph Server" as a technical runtime term, and added the `langgraph>=1.2` error-handler gate; a focused re-review passed on the corrected hashes.
- Headless e2e: skipped by explicit user decision; it is optional and not part of the content-closure proof.
- Reclassified final baseline: 27/27 included probe tasks are correct after loading the skill, and all 11 exclusions remain correct. Exact Codex attempts, grader records, hashes, and synthesis are preserved in `docs/plans/research/probe-codex-results.json`.
- Public plugin normalization changed the canonical identifier to `langchain`; the three residual attempts and six independent grader records were regenerated against the release-candidate hashes, again producing 6/6 `correct`, synthesis pass, and no material residuals.
- Direct strict validation passed separately for `.claude-plugin/marketplace.json` and `plugins/skills-for-langchain/.claude-plugin/plugin.json`.
- Isolated local smoke test: marketplace add, plugin install, plugin list, and plugin details all passed; Claude Code reported version 1.0.0, one `langchain` skill, and no agents, hooks, MCP servers, or LSP servers.
- `python3 scripts/validate_evidence.py`: PASS with 38 tasks, 27 includes, 11 exclusions, matching generated-file hashes, and matching v1.0.0 release metadata.

### v1.1.0 consultant validation (2026-07-16)

- `validate_harness.py --path .`: PASS, 0 errors / 0 warnings, after the consultant edit and all spec/pointer updates.
- `validate_evidence.py`: PASS at v1.1.0. The `SKILL.md` generated-file hash was re-stamped (`60fdcd6…`) with a documented note; the two delta references' pinned hashes and the historical per-attempt hashes are unchanged, and the residual grading verdicts (which depend only on those references) are untouched.
- Plugin mirror: `diff -rq .claude/skills/langchain plugins/skills-for-langchain/skills/langchain` clean, now including `references/consultant.md`.
- Regression guard: `git diff HEAD` shows `deepagents.md` and `langchain-langgraph.md` byte-unchanged, so the v1.0.0 deltas-only behavior is structurally intact.
- Strict manifest validation on Claude Code 2.1.211: `claude plugin validate` passed for both `plugins/skills-for-langchain/.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`.
- Tier-3 behavioral dry-run (a dynamic workflow of five isolated headless scenarios graded with cited transcript evidence; consult quality is a judgment call, honestly weaker than the v1.0.0 probe suite per DC10). All five passed: V1 support-email agent (English) entered consultant mode, read `references/consultant.md`, asked six scoping questions, and held the agreement gate (no Write/Edit) with current APIs and no stale reflexes; V2 the same goal in Korean did the same entirely in Korean and deferred the proposal until answers; V3 a `create_react_agent(instructions=…)` review applied the deltas-only corrections (`create_agent`, already-compiled, `system_prompt=`, explicit `provider:model`) with no interview launched; V4 "build an agent with CrewAI" correctly did not invoke the skill (`skill_invocations: []`) and wrote genuine CrewAI with no LangChain machinery; V5 "summarize one file once" answered that an agent is the wrong tool and recommended a plain script rather than over-engineering. Caveat honestly recorded: a full multi-turn interview cannot be exercised headless because `AskUserQuestion` is unavailable there, so the dry-run validates entry, posture, reference-reading, and the agreement gate — not interview depth, which remains a manual dogfood.
- Headless permission mechanism: confirmed working in this project on this run — `run_e2e.py` with `--isolate` spawned authenticated `claude -p` sessions that completed with sensible transcripts (`terminal_reason: completed`, `error: null`). The prior documented caveat that this was an unverified best guess is now resolved for this project.

### v1.2.0 docs-DB validation (2026-07-18)

- `scripts/build_docs_db.py` built `docs_official.db` from `langchain-ai/docs` @ `c728061` (snapshot 2026-07-07): 187 docs (langchain 73, langgraph 42, deepagents 53, concepts 4, reference 9, migrate 3, releases 3), 346 snippet substitutions, 10 changelog rows, ~4.4 MB.
- Regression fixed: `SELECT body FROM docs WHERE path LIKE '%dynamic-subagents%'` now contains the inlined `create_deep_agent(` code (the content the old distillation dropped). Zero unresolved snippet tags, zero `:::js`/`:::python` leakage.
- `scripts/validate_docs_db.py`, slimmed `scripts/validate_evidence.py`, and `validate_harness.py --path .` all PASS (0/0). Plugin mirror `diff -rq` clean (3 files, `.db` blob identical in both trees).
- Behavioral dry-run (`claude -p … --plugin-dir … --output-format stream-json`): the skill loaded, issued four `sqlite3 -readonly … MATCH` queries against the DB, and returned snippet-only APIs (`task()`, `CodeInterpreterMiddleware`) with zero stale reflexes (`instructions=`, `create_react_agent`, `.with_fallbacks`, `supervisor`). Caveat: `AskUserQuestion` is unavailable headless, so this validates entry/forcing-function/DB-querying, not interview depth.
- Build gotchas discovered (not anticipated by the plan): snippets nest (recursive inlining required; residual check scoped to imported names so legit JSX survives), and `:::` fences nest by colon count (`::::::js` around inner `:::`), needing a colon-count fence stack rather than exact-line matching.

### Optional paid e2e

- With explicit user consent only, run two to four isolated headless scenarios covering a positive Deep Agents trigger, a positive LangChain or LangGraph trigger, and an unrelated-framework near miss.
- Grade transcripts with cited tool-use or file evidence; surface-level compliance without evidence is a failure.
- The first run must be presented as verification of the headless permission mechanism itself because `--isolate` plus skipped permissions is documented as a reasoned default, not previously confirmed in this project.

## Change history

- 2026-07-12 — user approved the recovered spec and authorized the 38-scenario probe regression; headless e2e was explicitly declined.
- 2026-07-12 — sync/improve planning pass: audited the existing harness, recovered intent from `docs/plans/`, read the complete harness-creator reference and script package, verified the planned API surface against the local official docs, recorded initial source-level corrections, and proposed this spec.
- 2026-07-12 — generated the three-file skill and minimal `CLAUDE.md` pointer; ran both full after suites plus a three-task repair pass; repaired C6/C8 plus independent precision findings; preserved exact prompts and compact before/after evidence; passed normal and strict structural validation with zero findings.
- 2026-07-12 — user replaced the remaining validation method with Codex-only subagent review. The Codex gate found and repaired A2's deprecated override argument, then closed A2/C6/C8 with 2/2 independent `correct` verdicts per task and a passing hash/consensus synthesis. Added B33 and expanded the measured LC/LG reference from nine to ten deltas.
- 2026-07-12 — final independent Codex reviews found four version/branding precision issues and two plan-count/status inconsistencies. Corrected them, reran structural validation and the complete current-hash residual gate, obtained 6/6 independent `correct` verdicts again, and marked B1–B33 `validated`.
- 2026-07-12 — normalized the skill identifier to lowercase for public plugin compatibility and added a dedicated strict-validating Claude plugin plus same-repository marketplace manifest for the v1.0.0 release.
- 2026-07-12 — added public README/wiki and standard open-source governance files, regenerated current-hash residual evidence after identifier normalization, passed strict plugin/harness/evidence validation, and completed an isolated install/details smoke test; marked B34–B35 `validated`.
- 2026-07-16 — extend pass (consultant enhancement, plan in `docs/plans/consultant/`, DC1–DC10). Added the consultant behavior over the existing skill: broadened the `SKILL.md` description (consultant clause first, near-miss boundary kept), prepended a compact consultant gist (consult-vs-deltas branch, persona, thin ten-dimension checklist, reference-usage rule) while preserving the deltas-only content verbatim, and authored the new `references/consultant.md` (interview protocol, expanded checklist, agreement-gate build rules, one worked example). Added behavior rows B36–B41. The two delta references are byte-unchanged, so the v1.0.0 probe-measured knowledge is intact. Re-synced the plugin mirror byte-for-byte (`diff -rq` clean, now including `consultant.md`). Re-stamped the `SKILL.md` generated-file hash in `probe-codex-results.json` with an explicit note that the consultant content is not probe-covered and the per-attempt historical hashes are intentionally unchanged. Bumped the release to v1.1.0 (plugin.json, CHANGELOG, `docs/releases/v1.1.0.md`, README/wiki version references); strict plugin and marketplace validation passed on Claude Code 2.1.211. `validate_harness.py` and `validate_evidence.py` both pass. Commit cbc94e2, initial tag v1.1.0.
- 2026-07-16 — follow-up docs pass (commit 2471165): the v1.1.0 commit had only bumped README/wiki version strings, so the identity/structure/validation framing across README and the wiki (Home, Use-Cases, How-It-Works, Coverage-and-Limits, Validation-and-Evidence, Getting-Started, Customization, Troubleshooting, index) was updated to describe the dual behavior (consultant + current-API guide), the three-reference structure including `consultant.md`, the consult-vs-deltas branch, and the honest dry-run validation of consult behavior. Docs-only (no harness-component, version, or manifest change); reviewed by a four-lens docs workflow (SHIP, no blockers). The v1.1.0 tag was moved to this commit so the release includes the coherent docs.
- 2026-07-18 — **v1.2.0 docs-DB substrate change** (plan in `docs/plans/docs-db/` 00–07; PR #1 merged to `main`, feat commit `f49703c`). Replaced the two hand-distilled delta references with `references/docs_official.db` (SQLite + FTS5, full body of the ~187 core docs, snippets recursively inlined) that Claude queries with SQL before proposing or writing ecosystem code. Rewrote `SKILL.md` (forcing function + gotchas + DB schema/queries + DB-refresh "Staying current"), re-pointed `references/consultant.md` to the DB, deleted `references/deepagents.md` and `references/langchain-langgraph.md`. Added `scripts/build_docs_db.py` and `scripts/validate_docs_db.py`; slimmed `scripts/validate_evidence.py` to SemVer↔CHANGELOG + full-tree mirror byte-identity (dropped the SKILL.md hash pin; `docs/plans/research/` probe records preserved untouched). Bumped to v1.2.0 (plugin.json, CHANGELOG); light DB-search pass over README + wiki (How-It-Works, Coverage-and-Limits, Customization, Maintenance-and-Release), historical probe narrative preserved. Behavior inventory: retired B6–B30 and B33 (the delta-topic rows), reworded B31/B34/B37/B41, added B42–B46. All validators pass; behavioral dry-run confirmed DB-querying. Memory `docs-db-enhancement-plan` updated to IMPLEMENTED.
- 2026-07-18 — spec sync: this harness-spec.md itself was not updated in the v1.2.0 commit (README/wiki/memory were), leaving Context, Goals, the behavior inventory, Component specs, Design rationale, and Validation describing the retired delta-references substrate. Brought all living sections in line with the shipped DB substrate (semantic drift the audit's mechanical check could not catch, since the skill directory still existed). No component change — spec/docs only.
