# 01 — Overview and implementation orientation

Read this first. It tells the implementation session what is being built, why the scope is what it is, and how the rest of the plan is organized. The companion docs (`02`–`06`) hold the exact component specs; the evidence that justifies every scope decision lives in `research/`.

## What we are building

A single Claude Code skill at `.claude/skills/LangChain/` that carries **only what Claude (Opus 4.8, January-2026 knowledge cutoff) does not already know — or confidently gets wrong — about the current LangChain ecosystem** (LangChain 1.x, LangGraph 1.x, and the Deep Agents SDK), as documented in the April-2026 doc snapshot. It is a background knowledge skill: it auto-triggers when Claude works on LangChain-ecosystem code and supplies the specific deltas that keep Claude from generating deprecated or hallucinated APIs. It is not an action skill and defines no commands.

The skill's center of gravity is **Deep Agents**, which the model has essentially no correct priors for. LangChain-core and LangGraph appear only as a thin set of measured deltas, because the model already writes most modern LangChain-core and LangGraph-runtime code correctly.

## Why the scope is this and not more

This was decided by measurement, not by guessing, because a model cannot reliably self-report what it does not know — the failure mode we are fixing is precisely a model that confidently believes a deprecated API is current. Two independent axes were run:

- **Axis 1 — doc-novelty survey** (`research/novelty-catalog.md`): a read of the docs classifying every topic as NOVEL / CHANGED / KNOWN, with the exact API deltas.
- **Axis 2 — blind knowledge probes** (`research/probe-results.md`): 38 total tasks (26 + a 12-task round-2) in which subagents with no doc access wrote the Python they would actually produce, then a doc-armed grader classified each answer as `correct` (exclude), `outdated_confident` (highest value), `partial`, or `unknown`.

Crossing the two axes is what produced the final include list: the survey said much more was "new" than the model actually gets wrong, and the probes corrected that down to what is genuinely missing. The single most important empirical result is that **7 of the first 26 topics graded `correct` and were removed from scope** — the model already knows `create_agent`, custom middleware, structured output, `ToolRuntime`, the runtime-context API, LangGraph runtime context, and the functional API. Do not re-teach these; a skill that restates what the model already does correctly wastes context and signals distrust, which measurably degrades the model.

## The final content (measured)

The exact per-topic deltas, with the wrong prior each corrects and the current correct API, are specified in `03` (Deep Agents) and `04` (LangChain + LangGraph). At a glance:

- **Cross-cutting, belongs in the SKILL.md body** (applies on essentially every Deep Agents task): `create_deep_agent(system_prompt=...)` — **not** `instructions=`, which raises `TypeError` and which the model used in almost every Deep Agents probe; model IDs in this ecosystem are real/future (`claude-sonnet-4-6`, `gpt-5.5`) and must never be "corrected"; `model=` is passed explicitly as a `provider:model` string; `create_agent` (not `create_react_agent`/`AgentExecutor`) is the agent baseline.
- **LangChain — 5 deltas:** `SummarizationMiddleware` params, supervisor→agent-as-tool, `ModelFallbackMiddleware`, `ToolCallLimitMiddleware`, `ProviderToolSearchMiddleware`.
- **LangGraph — 4 deltas:** event streaming (v3), declarative error handling, interrupts (thin), `DeltaChannel`.
- **Deep Agents — 16 topics:** core + built-ins, backend security, long-term memory, subagents, async subagents, context engineering, skills, HITL, permissions, harness profiles, sandboxes, production, MCP, rubric middleware, dynamic subagents, interpreters/PTC.

**Explicitly excluded because the model was measured getting them right:** `create_agent` basics, custom middleware (`wrap_model_call`), agent structured output, `ToolRuntime`, per-invocation context, LangGraph runtime context, functional API, `PIIMiddleware`, `ContextEditingMiddleware`, `LLMToolSelectorMiddleware`, LangGraph `durability=`, Postgres persistence with `EncryptedSerializer`. These are recorded as "verified current as of the April-2026 snapshot" rather than silently dropped, so a future refresh knows they were checked and can re-check them.

## Structure of the skill

One skill, three files (rationale in `00-decision-log.md` D13):

```
.claude/skills/LangChain/
├── SKILL.md                          # trigger; 3-tier mental model; cross-cutting gotchas; routing to the two references
└── references/
    ├── deepagents.md                 # the bulk: 16 Deep Agents topics
    └── langchain-langgraph.md        # the thin deltas: 5 LangChain + 4 LangGraph
```

`02` specifies SKILL.md exactly (frontmatter and body). `03` and `04` specify the two reference files. Keep Deep Agents as one file: its topics interrelate (a single "build me a deep agent that does X" task routinely spans model + backend + subagents + memory), so co-locating them preserves the connective tissue and gives the model exactly one file to open. Sub-split only if `deepagents.md` becomes genuinely unwieldy while authoring — and if so, split along the core-vs-advanced seam noted in `03`, not by raw length.

## Authoring principles (apply to every line you write into the skill)

These come from the harness-creator skill doctrine and are the difference between a skill that ages well and one that becomes a liability.

- **Conviction over compliance.** Every delta is a correction plus the reason it is true, not a bare "use X not Y." The test: given only the reason, could the model re-derive the rule and handle a case this plan did not enumerate? Example: do not just write "pass `virtual_mode=True`"; write that `FilesystemBackend` defaults to `virtual_mode=False`, which performs no sandboxing at all even when `root_dir` is set, so the escape-blocking the user assumes is happening is not — that reasoning also covers cases the plan never lists.
- **Do not write what the model already knows.** The excluded list above is load-bearing. If a topic has a part the model gets right (e.g. the Deep Agents skill *format* `SKILL.md`+frontmatter, or `langgraph.json` shape), teach only the part it gets wrong (the `skills=` attach mechanism, the Managed Deep Agents branding) and say nothing about the part it already handles.
- **Lead with the wrong prior.** Because these are *corrections*, each topic lands hardest when it names the plausible-but-wrong thing the model will otherwise do, then the current API. The probe evidence gives you the exact wrong prior for every topic (the grader's "what the model did").
- **Numbers carry their reason and exception.** Any threshold or version gate (`deepagents>=0.6.5`, the ~85% summarization trigger, `max_ptc_calls=256`) is written with why it is that value and when it differs, not as a bare digit.
- **No mid-sentence line wrapping** in any generated file. Break only at sentence, list-item, or paragraph boundaries. Hard wraps break future exact-string edits and pollute diffs.

## Maintenance and refresh (D10)

The skill is a point-in-time distillation and must say so. Each reference file carries a "verified against \<versions\> on \<date\>" stamp. The refresh procedure — re-fetch the docs, re-run the survey and both probes, re-cross the axes, update only what changed — is documented for the maintainer inside the skill (see `02` for where). The skill is versioned in the GitHub repo, so a refresh is a normal commit with a visible diff of exactly which deltas changed.

## Success criteria (what "done" means)

Defined concretely in `05`. The spine is the **before/after probe**: the 38 probe tasks are a regression suite. "Done" means re-running the include-list tasks with the skill loaded flips their verdicts from `outdated_confident`/`partial`/`unknown` to `correct` — the deltas actually close — while the excluded tasks stay `correct` (the skill did not break anything the model already did well). Plus: `validate_harness.py` exits 0, and the skill's `description` triggers on real LangChain-ecosystem prompts without stealing triggers from unrelated work.

## Document map

- `00-decision-log.md` — every decision D1–D14 with rationale.
- `01-overview.md` — this file.
- `02-skill-md-spec.md` — the exact SKILL.md (frontmatter + body).
- `03-deepagents-content.md` — the `deepagents.md` reference: 16 topics, each with wrong prior, current API, code, source citation.
- `04-langchain-langgraph-content.md` — the `langchain-langgraph.md` reference: 9 deltas.
- `05-validation.md` — the before/after probe protocol, trigger tests, and `validate_harness.py` gate.
- `06-implementation-checklist.md` — the ordered step list for the next session.
- `research/` — the raw evidence (survey catalog, probe results, provenance).
