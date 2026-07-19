## Summary

<!-- What changed and why? -->

## Evidence

<!-- If this fixes bad guidance: the prompt, what Claude produced, and the official source showing what is current. -->

## Validation

- [ ] `python3 scripts/validate_docs_db.py` *(not covered by CI — run it locally)*
- [ ] `python3 scripts/validate_evidence.py`
- [ ] `claude plugin validate .claude-plugin/marketplace.json --strict`
- [ ] `claude plugin validate plugins/skills-for-langchain/.claude-plugin/plugin.json --strict`
- [ ] `git diff --check`
- [ ] Skill edits are mirrored — `diff -rq .claude/skills/langchain plugins/skills-for-langchain/skills/langchain` is clean.
- [ ] `CHANGELOG.md` and user documentation are updated when behavior, coverage, or limits changed.
- [ ] Historical evidence under `docs/plans/research/` was preserved rather than rewritten.
- [ ] No credentials, personal data, or proprietary source code are included.

## Scope

- [ ] The change belongs where it was put: the always-loaded `SKILL.md`, the consultant process, the build script and corpus, or documentation.
- [ ] No hand-written API prose was added to the skill. If the answer is in the official docs it belongs in the database; if it is missing from the database, the fix is corpus selection or a refresh.
- [ ] Any new gotcha covers a genuinely **removed or renamed** API — something a search over current documentation structurally cannot surface.
