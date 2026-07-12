# Research artifacts (planning evidence)

Evidence gathered during planning and implementation that grounds the plan in `../`. These inputs make the reasoning auditable and the refresh procedure (D10) repeatable; exact source bytes are verifiable only when the ignored snapshot has been restored.

## Provenance of the source docs

- **Source:** LangChain official docs (`docs.langchain.com/oss/python/...`), covering LangChain, LangGraph, and the Deep Agents SDK.
- **Snapshot:** local working copy at `.tmp/docs_langchain/` — 71,832,402 bytes and 1,139 files, drafted ~April 2026. **Not vendored in git** (see `.gitignore`). `docs-snapshot-manifest.md` records the aggregate digest; fetching live docs later creates a new baseline rather than reconstructing this one.
- **Consumer model cutoff:** the plan targets Claude Opus 4.8 with a January 2026 knowledge cutoff — the gap between that and the April 2026 docs is what the skill captures.

## Files

- `novelty-catalog.md` — axis-1 evidence: a doc-side survey classifying every significant topic as NOVEL / CHANGED / KNOWN, with the specific API deltas and a ranked "top gotchas" list.
- `probe-results.md` — axis-2 evidence: the blind knowledge probe, consolidated include/exclude analysis, and final after-probe closure record with repair iterations and run IDs.
- `probe-round1-tasks.json` / `probe-round2-tasks.json` — exact task prompts plus compact per-task baseline records (verdict, current API, key deltas, what the model did) for all 38 tasks, kept for auditability, reruns, and the "before" baseline.
- `probe-after-results.json` — compact per-task after evidence, historical run IDs and method labels, corrected include/exclude counts, and the final Codex-only residual closure summary.
- `probe-codex-results.json` — exact final Codex attempt, two-grader-per-task, generated-file hash, and synthesis evidence for A2, C6, and C8. This is the final residual authority and records that no Claude process was invoked for the gate.
- `docs-snapshot-manifest.md` — file count, byte count, aggregate SHA-256, verification command, and the explicit boundary of snapshot reproducibility.
