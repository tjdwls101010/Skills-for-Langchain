# Validation and Evidence

What is actually checked today, and the historical measurements that started the project. These are two different things, and conflating them would overstate the evidence — so this page keeps them apart.

## The honest summary

**What is verified today** is that the shipped artifact is sound and traceable: the database was built correctly from a named upstream commit, nothing was silently dropped, and the published plugin is byte-identical to the source. Plus one behavioral check that the skill actually queries the database rather than answering from memory.

**What was measured historically** is that a specific model, at a specific time, got a specific set of LangChain APIs wrong. That measurement is why this project exists and where the gotchas list comes from. It is **not** a validation of what ships today — the files it graded were deleted in v1.2.0.

Anyone who tells you this plugin is "38/38 validated" is reading a v1.0.0 number and applying it to a v1.2.0 artifact.

---

# Part 1 — What is checked today

## The database artifact

```bash
python3 scripts/validate_docs_db.py
```

Opens the shipped database read-only and asserts:

| Check | What it catches |
|---|---|
| All four tables exist | Schema corruption or an aborted build. |
| `doc_count` between 150 and 250 | A corpus glob that matched nothing, or matched everything. |
| `changelog` non-empty | An upstream format change that broke the parser. |
| No leftover `/snippets` import lines | Snippet inlining did not run. |
| No `:::js` leakage | JavaScript survived into a Python-only artifact. |
| `dynamic-subagents` body contains `create_deep_agent(` | **The regression this database exists to prevent.** |
| `docs_fts MATCH 'agent'` returns rows | The search index is populated, not merely present. |
| Every `meta` key populated | The artifact is traceable to a source commit. |

That sixth check deserves its name. `deepagents/dynamic-subagents.mdx` is the page whose code the old hand-distilled reference silently lost. If a future build stops inlining snippets, this assertion fires rather than shipping a database that reproduces the original defect quietly.

The build script runs an equivalent self-validation before it moves anything into place, so a failed build never overwrites a working database.

## Release metadata and the mirror

```bash
python3 scripts/validate_evidence.py
```

Two invariants:

1. **SemVer ↔ CHANGELOG coupling.** The version in `plugin.json` must have a matching `## [x.y.z]` heading in `CHANGELOG.md`. You cannot ship a version that is not written down.
2. **Mirror byte-identity.** Every file under `.claude/skills/langchain/` is SHA-256 compared against `plugins/skills-for-langchain/skills/langchain/`, in both directions — including the 4.4 MB database. Missing files, extra files, and drifted content all fail.

The second is the load-bearing one. It makes it structurally impossible for the published plugin to differ from what the repository claims it contains.

## Manifests

```bash
claude plugin validate .claude-plugin/marketplace.json --strict
claude plugin validate plugins/skills-for-langchain/.claude-plugin/plugin.json --strict
```

## What CI runs

`.github/workflows/validate.yml`, on every push to `main` and every pull request: `validate_evidence.py`, both strict manifest validations, and a whitespace check.

**CI does not run `validate_docs_db.py`.** Stated plainly because it is a real gap — the database checks are currently a local step a maintainer must remember. If you touch the database or the build script, run it yourself and say so in the pull request.

## Behavioral check (v1.2.0)

Mechanical checks prove the artifact is well-formed. They cannot prove the skill *uses* it — which is the entire load-bearing risk of a query-on-demand design, because a model that skips the lookup and answers from memory looks exactly like one that did not.

A headless dry-run addressed that directly. With the plugin loaded, the skill:

- issued **four** `sqlite3 -readonly ... MATCH` queries against the database before answering;
- returned APIs that exist **only inside inlined snippets** — `task()`, `CodeInterpreterMiddleware` — which is strong evidence it read the database rather than recalling anything, since those strings were absent from the pre-v1.2.0 substrate;
- produced **zero** stale reflexes: no `instructions=`, no `create_react_agent`, no `.with_fallbacks()`, no `supervisor` import.

**Caveat, recorded honestly:** `AskUserQuestion` is unavailable in headless mode, so this validates skill entry, the forcing function, and database querying. It does **not** validate interview depth, which remains a manual review.

## The build that shipped

`scripts/build_docs_db.py` against `langchain-ai/docs` at `c728061`, snapshot date 2026-07-07: 187 documents (langchain 73, langgraph 42, deepagents 53, concepts 4, reference 9, migrate 3, releases 3), **346 snippet substitutions**, 10 changelog rows, ~4.4 MB. Zero unresolved snippet tags, zero language-conditional leakage.

Two build behaviors were discovered during that work and are worth knowing, because both were silent-corruption risks: snippets import further snippets, so inlining has to recurse; and Mintlify nests language fences by *increasing colon count*, so a closing fence must be matched to its opener by count rather than by position.

---

# Part 2 — The historical measurement

Everything below describes how v1.0.0's scope was determined in July 2026. It is preserved because it explains why the project exists and where the gotchas list came from. It does not validate the current artifact.

## Why measurement rather than asking

The failure this project targets is **confident outdatedness**. That rules out asking the model what it does not know — it will report an obsolete pattern as current, with no hedge, because from its side nothing is uncertain.

So scope was set by crossing two independent axes:

**Axis 1 — documentation novelty.** The official documentation was surveyed and each topic classified `NOVEL`, `CHANGED`, or `KNOWN`. Catalog: [novelty-catalog.md](../plans/research/novelty-catalog.md).

**Axis 2 — blind probes.** Implementation tasks given to Claude Opus 4.8 (January-2026 cutoff) with **no documentation and no web access**, each answer graded by a separate documentation-armed grader.

Crossing them mattered: the survey said far more was "new" than the model actually got wrong, and the probes corrected that down to what was genuinely missing. Include logic was `new ∧ wrong → include`, `new ∧ right → exclude (learned elsewhere)`, `not-new ∧ wrong → include (a sneaky gotcha)`.

## The grading rubric

| Verdict | Meaning | Decision |
|---|---|---|
| `correct` | The model already knows it | **Exclude** — and keep as a regression guard |
| `outdated_confident` | Plausible, confident, materially obsolete | **Highest-value inclusion** |
| `partial` | Right scaffolding, wrong specifics | Include the missing piece |
| `unknown` | No usable answer | Include focused guidance |

## Results

**38 tasks across two rounds.**

*Round 1* — 26 tasks, deliberately weighted toward Deep Agents (A1–A7 LangChain, B1–B5 LangGraph, C1–C14 Deep Agents):

| Verdict | Count |
|---|---|
| `correct` (excluded) | 6 |
| `partial` (included) | 15 |
| `outdated_confident` (included) | 5 |

**All 14 Deep Agents tasks were flagged as gaps** — a complete miss for that library. The single most common failure was `create_deep_agent(instructions=...)`, which appeared in nine of them. That is why it became the first line of the gotchas list: if the model loads the skill and reads nothing else, that one line prevents the most common failure.

*Round 2* — 12 targeted tasks on areas Round 1 had under-sampled: 5 excluded, 7 included. The finding worth keeping is that the LangChain built-in middleware catalog was **mostly already known** — `PIIMiddleware`, `ContextEditingMiddleware`, and `LLMToolSelectorMiddleware` all graded `correct` — so no catalog was needed, only the specific misses.

**Totals: 27 included, 11 measured-correct exclusions.**

Exact prompts and baseline records: [Round 1](../plans/research/probe-round1-tasks.json), [Round 2](../plans/research/probe-round2-tasks.json).

## The after-run, tiered honestly

The record was deliberately kept as layers rather than collapsed into one number:

1. **Strict full suite** using the generated files and the original grader: **35/38** — 24 of 27 include-list flips, and 11 of 11 exclusions preserved. Residuals: A2, C6, C8.
2. **Repair-context retry** on those three: 3/3 correct, labeled separately because it used shorter correction context, not the strict mechanism.
3. **Final residual gate**, by explicit maintainer decision using Codex subagents only, with no Claude process involved: isolated attempts embedding the exact current file hashes, then **two independent documentation-armed graders per task** — 6/6 `correct` — plus a separate synthesis reviewer confirming every hash.

**Final recorded state: 27/27 included tasks correct, 11/11 exclusions preserved.**

The combined observed figure across all suites is 38/38, and the record explicitly declines to present that as a single identical-protocol run. A faithful full retry was attempted and returned HTTP 429 on an exhausted session limit; it produced no countable result and is not counted as evidence.

Records: [probe-codex-results.json](../plans/research/probe-codex-results.json), [probe-after-results.json](../plans/research/probe-after-results.json), [probe-results.md](../plans/research/probe-results.md).

## What the after-run actually caught

Two genuine defects, which is the argument for having run it at all:

- **C6** — the reference described async subagents but never said to import `AsyncSubAgent` from `deepagents`, pass the specs directly through `subagents=[...]`, and rely on automatic middleware attachment.
- **C8** — the planning record had treated an individual skill directory as a `skills=` entry. Official docs define each entry as a *top-level source directory* whose children are the skills.

Both were plan-level errors that read as correct until a probe tried to use them.

## Snapshot provenance (historical)

The v1.0.0 evidence baseline was a fetched copy of the official Python documentation described as **April 2026**: 1,139 files, 71,832,402 bytes, aggregate SHA-256 `28f5d63f361de2d56b62118524401fa5aca3d08a8c993e7605aedb45f457fbed`. Recorded in [docs-snapshot-manifest.md](../plans/research/docs-snapshot-manifest.md).

It had **no git metadata** — it was a fetch, not a clone — and it was missing `src/snippets/`, which is precisely the defect that led v1.2.0 to clone the whole repository and inline snippets at build time. The manifest can verify a restored copy is byte-identical; it cannot reconstruct the snapshot from this repository.

The current database is a different snapshot entirely: a real `git clone` at commit `c728061`, dated 2026-07-07. Do not conflate the two dates.

## The consultant (v1.1.0)

The consultant is validated on a deliberately lighter bar, and the reason is stated rather than hidden: "is this API current" is a mechanically gradable fact; "did it consult well" is a judgment. Pretending otherwise would have meant inventing a false metric.

So there is no probe flip-rate for it. Instead, a five-scenario headless dry-run, each graded with cited transcript evidence:

| Scenario | Requirement | Result |
|---|---|---|
| Support-email agent, English | Enter consultant mode, read `consultant.md`, ask scoping questions, write nothing | Passed — six questions, gate held |
| Same goal, Korean | Same, conducted entirely in Korean | Passed |
| Review of `create_react_agent(instructions=…)` | Correct the APIs with **no** interview | Passed |
| "Build an agent with CrewAI" | Do not invoke the skill at all | Passed — `skill_invocations: []` |
| "Summarize one file once" | Say an agent is the wrong tool | Passed — recommended a plain script |

Same caveat as above: no `AskUserQuestion` headless, so interview *depth* is unvalidated.

## What is not claimed

- The historical evidence is not one identical-protocol 38/38 run.
- **The probe evidence does not validate the current artifact.** It graded the delta reference files, which v1.2.0 deleted. What survives from it is the gotchas list and the reason the project exists.
- Consult quality is a judgment call, not a measured number.
- Results do not generalize to every model, prompt, package version, or domain.
- Passing a code-generation probe proves nothing about runtime correctness, security, or production fitness.
- No headless end-to-end test of a full multi-turn interview exists, on any version.

## Evaluating a future refresh

The refresh model changed with the substrate. There is nothing to re-probe — rebuild, and check:

1. **The build report.** Per-package counts near the previous build, and a snippet-substitution count that has not collapsed. A sudden drop means the corpus or the inliner broke.
2. **`validate_docs_db.py` passes**, especially the snippet-inlining regression.
3. **`meta.snapshot_date` moved.** If it did not, you rebuilt from a stale clone.
4. **The gotchas list is still true.** This is the one item requiring judgment: a removed API may have returned, or a new rename may have appeared. Nothing automated will tell you.
5. **The mirror is clean** and the version was bumped.

Never rewrite the historical records under `docs/plans/research/` to make a new result look tidier. Append.

---

**Next:** [Maintenance and Release](Maintenance-and-Release.md) for the procedure these checks belong to.

Back to the [documentation index](README.md).
