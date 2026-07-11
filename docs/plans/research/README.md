# Research artifacts (planning evidence)

Evidence gathered during the planning session that grounds the plan in `../`. These are inputs to the plan, preserved so the reasoning is auditable and the refresh procedure (D10) is reproducible.

## Provenance of the source docs

- **Source:** LangChain official docs (`docs.langchain.com/oss/python/...`), covering LangChain, LangGraph, and the Deep Agents SDK.
- **Snapshot:** local working copy at `.tmp/docs_langchain/` — ~71 MB, 1139 files, drafted ~April 2026. **Not vendored in git** (see `.gitignore`); re-fetch to reproduce.
- **Consumer model cutoff:** the plan targets Claude Opus 4.8 with a January 2026 knowledge cutoff — the gap between that and the April 2026 docs is what the skill captures.

## Files

- `novelty-catalog.md` — axis-1 evidence: a doc-side survey classifying every significant topic as NOVEL / CHANGED / KNOWN, with the specific API deltas and a ranked "top gotchas" list.
- `probe-results.md` — axis-2 evidence: the blind knowledge probe (added once the probe workflow completes) — what Claude actually got wrong when measured, per task, with verdicts.
