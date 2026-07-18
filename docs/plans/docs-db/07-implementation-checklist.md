# 07 — Implementation checklist

Ordered, verifiable steps for the implementation session. Each step names its verification. Do not mark a step done until its check passes.

## Phase A — Source & build script
1. Fresh clone: `rm -rf .tmp/docs_langchain && git clone --depth 1 https://github.com/langchain-ai/docs .tmp/docs_langchain`.
   → verify: `ls .tmp/docs_langchain/src/oss` and `ls .tmp/docs_langchain/src/snippets/code-samples | head`.
2. Confirm the snippet that broke before resolves: `test -f .tmp/docs_langchain/src/snippets/code-samples/dynamic-subagents-quickstart-py.mdx`.
3. Write `scripts/build_docs_db.py` per `04-build-script.md` (stdlib-only, FTS5 preflight, snippet inlining, `:::js` strip, changelog + meta).
   → verify: `python scripts/build_docs_db.py --help` runs; code has no third-party imports.

## Phase B — Build & validate the DB
4. Build: `python scripts/build_docs_db.py --src .tmp/docs_langchain --out .claude/skills/langchain/references/docs_official.db`.
   → verify: exits 0; report shows ≈187 rows, per-package counts, snippet substitutions > 0, changelog rows > 0.
5. Regression check (the whole point):
   ```bash
   sqlite3 -readonly .claude/skills/langchain/references/docs_official.db \
     "SELECT substr(body,1,4000) FROM docs WHERE path LIKE '%dynamic-subagents%';"
   ```
   → verify: output contains real Python (`create_deep_agent(`), i.e. the inlined `<CodeGroup>`, not a bare `<... />` tag.
6. FTS smoke: `... "SELECT d.path FROM docs_fts JOIN docs d ON d.id=docs_fts.rowid WHERE docs_fts MATCH 'model fallback' ORDER BY rank LIMIT 5;"` returns rows.
7. Add/adjust the lightweight DB validation (`--check` or `scripts/validate_docs_db.py`) per `06`; run it → passes.

## Phase C — Skill rewrite
8. Rewrite `SKILL.md` per `05`: forcing function, gotchas (~10 lines), schema + 5 example queries + FTS notes + `sqlite3 -readonly` invocation, "Staying current" → DB-refresh workflow. Remove all pointers to the two delta files.
9. Edit `references/consultant.md`: re-point "Reference-usage discipline" to the DB; scan the worked example for stale references.
10. Delete `references/deepagents.md` and `references/langchain-langgraph.md`.
    → verify: `python "/Users/seongjin/.claude/skills/harness-creator/scripts/validate_harness.py" --path .` exits 0 (no dangling pointers).

## Phase D — Evidence & release
11. Lighten the evidence framework per `06`: drop/relax the SKILL hash pin; keep CHANGELOG+SemVer and mirror checks; preserve `docs/plans/research/` records untouched.
12. Bump `plugin.json` (+ marketplace.json if versioned) → `1.2.0`; add `## [1.2.0]` to `CHANGELOG.md`.
13. Confirm `.gitignore`: `.tmp/` ignored, `references/docs_official.db` **not** ignored (carve out any `*.db` rule).
14. Mirror everything into `plugins/skills-for-langchain/skills/langchain/` (skill files + `.db`).
    → verify: `diff -rq .claude/skills/langchain plugins/skills-for-langchain/skills/langchain` shows no differences.
15. Run `validate_evidence.py` (slimmed) + `validate_harness.py` → both pass.
16. Update README / wiki wording (delta-refs → DB-search), light touch.

## Phase E — Behavioral check & commit
17. (Recommended) Headless dry-run per `06` "Regression guard", incl. the snippet-dependent Deep Agents scenario → confirm DB-querying behavior.
18. Commit on a branch; message ends with the required `Co-Authored-By` trailer. Push; open PR to `main`. Do **not** commit `.tmp/`.
19. Update memory: mark the docs-DB enhancement implemented + released, with any gotchas discovered (mirror the `consultant-enhancement-plan` memory's style).

## Guardrails carried from the plan
- Corpus = core only; JS and integrations excluded — enforced by build globs, not by the clone.
- Every changed skill file is mirrored; the `.db` is committed in both copies.
- The forcing function + gotchas list are the DB-only safety net — do not drop them for brevity.
- Keep MDX cleaning conservative; the only mandatory transforms are snippet inlining and `:::js` removal.
