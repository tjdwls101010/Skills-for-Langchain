# Decision Log — Langchain Skill (planning session)

This is the running record of decisions agreed during the planning session. The final, detailed plan lives in the sibling files in this directory. This log exists so a later session can see *what was decided and why*, not just the final artifact.

Session date: 2026-07-11 (planning only; implementation is a separate later session).

## Goal (in the user's words, paraphrased)

Build a Claude Code **skill** at `.claude/skills/Langchain` that contains **only what Claude does not already know (or knows wrongly)** about the LangChain ecosystem — LangChain (core), LangGraph, and especially **DeepAgents**, which Claude knows least about. The framework updates constantly, so Claude keeps generating outdated code; the skill closes that gap. Source material: the ~185-file, ~4.6 MB doc snapshot at `.tmp/docs_langchain/` (drafted ~April 2026; Claude's knowledge cutoff is January 2026).

## Confirmed decisions

| # | Decision | Choice | Rationale |
|---|----------|--------|-----------|
| D1 | Language scope | **Python only** | Vast majority of LangChain use; halves surface area; keeps focus. JS can be a later extension. |
| D2 | Framework coverage | **DeepAgents-first**, LangChain/LangGraph only as much as measured need dictates | Claude's gap is largest in DeepAgents; "필요한 만큼"은 추정이 아니라 실측으로 정한다. |
| D3 | Content boundary | **Delta + high-value gotchas** | Post-cutoff/new APIs + renamed/deprecated patterns + traps even a capable model gets wrong. Exclude anything Claude already does right. Best signal-to-token. |
| D4 | Generated skill language | **English** (body, code, terms) | Matches API terminology, avoids translation drift, best for Claude's own parsing/triggering. (Interview conversation stays Korean.) |
| D5 | Scope-setting method | **Empirical measurement, not self-report** | A model cannot reliably self-report what it doesn't know (it confidently believes wrong things). Evidence required. |
| D6 | Evidence: axis 1 | **Doc novelty survey** (background subagent) | Doc-side view: "what is new/changed in the docs." Output → `scratchpad/novelty-catalog.md`. |
| D7 | Evidence: axis 2 | **Blind knowledge probe**, ~24-30 tasks, DeepAgents-weighted | Model-side view: subagents (same Opus 4.8, no doc/web access) attempt tasks from internal knowledge; a doc-armed grader classifies each answer: correct(Claude knows→exclude) / outdated-confident(→highest value) / partial / unknown(→include). |
| D8 | Include logic | **Cross the two axes** | new∧wrong → core of skill; new∧right → exclude (learned elsewhere); not-new∧wrong → sneaky gotcha (include). |
| D9 | Probe reuse | **Doubles as before/after validation** | Same probe re-run with the skill loaded in the implementation session proves the delta closed: "N wrong without skill → 0 wrong with skill" is the success criterion. |
| D10 | Maintenance/refresh | **Snapshot + reproducible, version-stamped refresh procedure** | Skill carries distilled deltas inline with a "verified against &lt;versions&gt; on &lt;date&gt;" stamp; refresh = re-run the survey+probe pipeline, documented as a procedure in the skill. Self-contained (no network at use-time), deterministic, git-versioned. Fits the shared-repo intent. |

## Survey result (axis 1) — recorded

Full catalog: `scratchpad/novelty-catalog.md` (219 lines). Headline: the **entire Deep Agents SDK** is post-cutoff (zero correct priors); **LangChain middleware** + **`create_agent` replacing `create_react_agent`** + the **runtime/context model** (`context=` not `config.configurable`, `ToolRuntime`) are the big CHANGED areas; **LangGraph is CHANGED-dominated** (core StateGraph is KNOWN — exclude). Two surprises folded into scope: **all model IDs in the docs are future/fictional** (must tell the model not to "correct" them), and the literal word **"workflow"** triggers dynamic subagents.

Distilled volume estimate: **~18–30k tokens**, Deep-Agents-dominated (~15–20× compression off raw MDX).

**Structure finding (proposed, confirm after probe):** split per-framework — `deepagents` / `langchain-middleware` / `langgraph` — plus a shared **idioms & import-map** file every branch links. Branching is clean (a task opens exactly one framework; Deep Agents uses the others as a black box). A monolith is wrong here. Deep Agents is the largest branch and may warrant subtopic sub-files. Secondary axis (python vs js) is moot given D1 (Python only).

| D11 | Skill identity | **DeepAgents-centric + thin LC/LG deltas** | Probe evidence: Claude already writes modern LangChain-core + LangGraph-runtime correctly (7/26 "correct"). The real gap is DeepAgents (14 topics) + ~5 LC/LG deltas. One skill, not multiple (single trigger context). |
| D12 | Round-2 probe | **~12 targeted tasks on under-sampled areas** | Round-1 was thin on LangChain built-in middleware (only summarization probed), LangGraph persistence/durability deltas, and DeepAgents micro-features (rubric/dynamic-subagents/interpreters). Measure before finalizing include list. |

## Probe result (axis 2, round 1) — recorded

Full evidence: `research/probe-results.md`. 26 blind tasks → doc-armed grading. **7 exclude** (create_agent, custom middleware, structured output, ToolRuntime, context API, LangGraph runtime context, functional API — Claude already correct), **19 include** (all 14 DeepAgents + A4, A7, B2, B3, B5). **Dominant cross-cutting gotcha:** `create_deep_agent(instructions=)` → `system_prompt=` (wrong in ~every DeepAgents task) — belongs in SKILL.md body. Plus: model IDs in docs are real/future (don't "correct"); pass `model=` explicitly.

## Open decisions (resolve after round-2 probe)

- Round-2 include list (pending round-2 completion).
- Skill file structure: SKILL.md + `references/` layout, and whether DeepAgents is one file or sub-split. Evidence leans: SKILL.md (mental model + cross-cutting gotchas + routing) + `references/deepagents.md` (bulk) + `references/langchain-langgraph.md` (thin deltas). Finalize post-round-2.
- Frontmatter: `description` (trigger wording + near-misses), `user-invocable: false` (background knowledge, not a command), `disable-model-invocation` (likely no).
- Validation scenarios (I5) — the before/after probe is the spine; any additions?

## Method note

This session = planning + evidence-gathering only. No SKILL.md is written. The deliverable is a detailed, self-contained plan in `docs/plans/` that a fresh Claude session can implement from without re-deriving scope.
