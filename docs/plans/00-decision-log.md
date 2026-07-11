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

## Open decisions (to resolve this session)

- Probe task blueprint (categories + weighting) — pending user approval.
- Skill structure: single skill vs. split into `references/` — decide after evidence (survey + probe) reveals whether the model branches per-framework on a given task.
- Content organization within the skill.
- Maintenance/refresh strategy (framework changes constantly; how does the skill stay current?).
- Validation scenarios (I5) — the before/after probe is the spine; any additions?

## Method note

This session = planning + evidence-gathering only. No SKILL.md is written. The deliverable is a detailed, self-contained plan in `docs/plans/` that a fresh Claude session can implement from without re-deriving scope.
