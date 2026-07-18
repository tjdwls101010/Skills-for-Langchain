# 06 — Evidence framework, validation & release

## Evidence framework: retire & lighten (D9)

Current state (from the v1.1.0 release, see memory `consultant-enhancement-plan`):
- `scripts/validate_evidence.py` pins `SKILL.md`'s SHA256 in `docs/plans/research/probe-codex-results.json` (`generated_file_sha256`) and enforces deltas-only justification + SemVer/CHANGELOG coupling.
- Per-attempt `skill_sha256` fields there are **historical** v1.0.0 grading records.

Changes:
1. **Remove the SKILL.md hash pin** as a hard gate — SKILL.md is being rewritten and will keep evolving with each DB refresh; pinning its hash to a probe record no longer models anything. Either delete the `generated_file_sha256` check or repoint it to hash the **DB build inputs** instead (optional).
2. **Preserve** `docs/plans/research/` probe records as-is (historical measurement; do not rewrite them).
3. **Keep** the parts of `validate_evidence.py` that are still meaningful: `plugin.json` version must have a matching `## [x.y.z]` CHANGELOG heading; plugin mirror must be byte-identical. If disentangling is awkward, it's acceptable to slim `validate_evidence.py` down to just those two checks and drop the delta-justification logic.
4. **Add** a lightweight **DB-build validation** — either a `--check` mode in `build_docs_db.py` or a small `scripts/validate_docs_db.py`:
   - schema has `docs`, `docs_fts`, `changelog`, `meta`;
   - `doc_count` in band (≈150–250);
   - **zero unresolved snippet tags** (no imported `NAME` still present as `<NAME/>`);
   - `docs_fts MATCH 'agent'` returns > 0 rows;
   - the dynamic-subagents regression: `SELECT body FROM docs WHERE path LIKE '%dynamic-subagents%'` contains actual Python (e.g. matches `create_deep_agent(`), proving snippets inlined;
   - `meta` fully populated.

## Whole-harness validation

- `python "/Users/seongjin/.claude/skills/harness-creator/scripts/validate_harness.py" --path .` must exit 0. This catches dangling pointers to the deleted delta files and YAML/structure issues. It does **not** grade the SKILL.md description — re-read the description against skills-authoring guidance manually (it should already be fine; don't narrow it).

## Release mechanics (D10)

1. **SemVer:** bump `plugin.json` (and `.claude-plugin/marketplace.json` if it carries a version) to **1.2.0** — a user-facing capability change (new knowledge substrate).
2. **CHANGELOG.md:** add a `## [1.2.0] - 2026-…` entry describing the DB-backed knowledge substrate, snippet-complete docs, and the removal of the two delta files.
3. **Plugin mirror:** copy every changed skill file **and `docs_official.db`** into `plugins/skills-for-langchain/skills/langchain/`; verify:
   ```bash
   diff -rq .claude/skills/langchain plugins/skills-for-langchain/skills/langchain
   ```
   Expect no differences. The `.db` is committed in both places (accepted binary duplication, D11.5).
4. **.gitignore:** confirm `.tmp/` stays ignored and the `.db` under `references/` is **not** ignored (it must be committed). Check for any blanket `*.db` ignore and carve out the docs DB if present.
5. **README / wiki:** update any description of "how the skill knows current APIs" from delta-references to DB-search. Keep it light; the prior release touched README + wiki.

## Regression guard (behavioral, optional but recommended)

Reuse the v1.1.0 headless dry-run shape (consult En/Ko, deltas path, CrewAI near-miss, overkill-honesty) plus one new scenario: a Deep Agents coding task where the correct answer depends on a snippet-only detail (e.g. dynamic subagents / interpreter wiring) — confirm the model queries the DB and pulls inlined code rather than hallucinating. Note the standing caveat: AskUserQuestion is unavailable headless, so the full interview can't be exercised that way; this validates entry/posture/DB-querying, not interview depth.
