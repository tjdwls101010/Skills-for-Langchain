# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.2.0] - 2026-07-18

### Changed

- The `langchain` skill's knowledge substrate is now a searchable database of the current official docs (`references/docs_official.db`) that Claude queries with SQL before proposing or writing any ecosystem code — replacing the two hand-distilled delta references. The DB holds the full body of the ~187 core docs (LangChain, LangGraph, Deep Agents, concepts, reference, migrate, releases) with every `/snippets/...` code sample inlined, so nothing is pre-dropped by distillation. This fixes the measured failure where distillation silently lost content (e.g. `deepagents/dynamic-subagents.mdx`'s orchestration code samples).
- `SKILL.md` rewritten: a forcing function ("you do not reliably know the current API — query the DB first"), a compact gotchas list for removed/renamed APIs the DB structurally cannot surface, the DB schema with worked FTS5 queries, and a one-command DB-refresh workflow.
- `references/consultant.md` re-pointed from the delta files to the DB; the interview protocol, ten dimensions, build rules, and worked example are otherwise unchanged.

### Added

- `scripts/build_docs_db.py` (stdlib-only): clones/reads `langchain-ai/docs`, selects the core corpus, recursively inlines snippet imports, strips JS-only `:::js` conditionals, parses the changelog, and writes `docs_official.db` with an FTS5 index and a provenance `meta` stamp.
- `scripts/validate_docs_db.py`: lightweight artifact validation (schema, row-count band, zero unresolved snippets, snippet-inlining regression, FTS hits, meta populated).

### Removed

- `references/deepagents.md` and `references/langchain-langgraph.md` — the two delta references, superseded by the DB.
- The deltas-only justification in `scripts/validate_evidence.py` (SKILL.md hash pin); it now checks only SemVer/CHANGELOG coupling and plugin-mirror byte-identity. The historical probe records under `docs/plans/research/` are preserved untouched.

## [1.1.0] - 2026-07-16

### Added

- Consultant behavior on the `langchain` skill: on an abstract agent-building goal ("build an agent that…", "automate this…", "answer from these docs"), the skill now leads an interview, proposes a concrete current-API architecture, and — only after explicit agreement and an agreed build scope — implements it.
- New `references/consultant.md`: the interview protocol (divergent-open, convergent AskUserQuestion), the ten-dimension checklist expanded as principles, the agreement-gate build rules, and one worked example.
- Broadened skill `description` so a natural-language goal (no framework named, no code shown) triggers the skill, while preserving the CrewAI/AutoGen/LlamaIndex/raw-SDK near-miss boundary.

### Preserved

- The deltas-only behavior is unchanged: editing or reviewing existing LangChain-ecosystem code still gets silent current-API corrections with no interview.
- The two delta references (`deepagents.md`, `langchain-langgraph.md`) are byte-unchanged; the v1.0.0 probe-measured knowledge is intact.

## [1.0.0] - 2026-07-12

### Added

- Evidence-built Claude Code skill for current LangChain 1.x, LangGraph 1.x, and Deep Agents Python APIs.
- Progressive-disclosure references covering 6 LangChain deltas, 4 LangGraph deltas, and 16 Deep Agents topics.
- Claude Code plugin manifest and same-repository marketplace catalog.
- Public README, wiki-source documentation, contribution guidelines, security policy, support policy, issue forms, and pull-request template.
- Vendored project artwork with a separate reuse notice.
- Reproducible research artifacts for 38 baseline probes, after-run results, current-file residual grading, and documentation snapshot provenance.
- Automated repository validation for plugin manifests and evidence integrity.

### Validated

- Final recorded state of 27/27 included probe tasks correct and 11/11 measured-correct exclusions preserved.
- Normal and strict harness validation with zero errors and zero warnings.
- Claude Code plugin and marketplace validation in strict mode.

### Known limitations

- Python only.
- Version-sensitive knowledge is verified against an April-2026 official-documentation snapshot.
- Headless E2E was skipped and is not claimed as v1.0.0 evidence.

[Unreleased]: https://github.com/tjdwls101010/Skills-for-Langchain/compare/v1.1.0...HEAD
[1.2.0]: https://github.com/tjdwls101010/Skills-for-Langchain/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/tjdwls101010/Skills-for-Langchain/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/tjdwls101010/Skills-for-Langchain/releases/tag/v1.0.0
