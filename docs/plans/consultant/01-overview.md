# 01 — Overview and implementation orientation

Read this first. It tells the implementation session what is being added, why the scope is what it is, and how the rest of this plan is organized. The companion docs hold the exact specs: `02` (SKILL.md changes), `03` (the consultant content and the new `references/consultant.md`), `04` (validation), `05` (ordered checklist). The rationale for every decision is in `00-decision-log.md`.

## What we are adding

A **consultant behavior** on top of the existing `langchain` skill. Today the skill is a passive knowledge layer: it auto-triggers when Claude works on LangChain-ecosystem Python and injects the measured post-cutoff API deltas. After this change, the *same skill* also acts as a **LangChain solutions consultant**: when a user describes an abstract goal ("build an agent that triages my support inbox", "automate this weekly report", "let it answer questions from these PDFs"), the skill leads Claude to interview the user, propose a concrete architecture grounded in the *current* LangChain/LangGraph/Deep Agents API, discuss it, and — only after the user agrees — build it.

Crucially, this is **one skill with two behaviors**, not a rewrite:

- **Deltas-only path (unchanged, must not regress):** Claude is editing or reviewing existing LangChain code. The skill silently supplies the current-API corrections, exactly as in v1.0.0. No interview.
- **Consultant path (new):** the user is describing an outcome they want, not editing code. The skill has Claude adopt the consultant role, run the interview, propose, and build-on-agreement.

The body of `SKILL.md` branches between these two on the situation it detects.

## Why the scope is *process*, not more knowledge

This is the load-bearing scope decision (`00` DC4), and the implementation session must hold the line on it. The instinct is to make a good consultant by teaching it more about LangChain. That is wrong here, for a measured reason: the earlier plan already proved that Claude (Opus 4.8) writes most *conceptually correct* LangChain architecture on its own — it knows what middleware, HITL, subagents, RAG, and persistence are and when to reach for them. What it gets wrong is the **current API surface at implementation time**, and that gap is already closed by the two existing delta references.

So the consultant needs exactly three things, and nothing that smells like an encyclopedia:

1. **A persona and a posture** — a confident solutions consultant who asks before assuming, proposes concrete architectures, is honest about tradeoffs (including when LangChain is the wrong tool), and never side-effects without agreement.
2. **An interview protocol with a thin dimension checklist** — a list of *dimensions to ask about*, so the interview never silently assumes one. Not a decision tree that maps goals to answers; Claude's own judgment does the mapping.
3. **The discipline to read the delta references before proposing or implementing** — so Claude's *stale* architecture reflexes (`create_react_agent`, `instructions=`, the removed supervisor package, `.with_fallbacks()` for agents) never leak into the proposal or the code.

If the implementation session finds itself writing a catalog of "here is everything LangChain can do", it has drifted off-scope. Stop and re-read `00` DC4. The user explicitly named the "walking encyclopedia" as the anti-goal.

## Why the knowledge stays exactly where it is

The existing `references/deepagents.md` (16 topics) and `references/langchain-langgraph.md` (10 deltas) are the consultant's evidence base. They are **not** edited by this plan. The consultant SKILL.md points at them ("before you propose or write code, read the relevant reference"), so there is one copy of the knowledge, shared by both behaviors — which is precisely the "consultant on top, absorb the knowledge" structure the user asked for (`00` DC1). Re-verifying or expanding that knowledge is out of scope; if a future refresh is needed it follows the maintenance procedure already documented in the current SKILL.md, independent of this consultant work.

## Structure of the change

```
.claude/skills/langchain/
├── SKILL.md                          # EDITED: + consultant persona/goals, consult-vs-deltas branch,
│                                     #         thin dimension checklist, reference-usage rules,
│                                     #         broadened description (see 02). Existing 3-layer model,
│                                     #         cross-cutting gotchas, routing, and maintenance note kept.
└── references/
    ├── deepagents.md                 # UNCHANGED
    ├── langchain-langgraph.md        # UNCHANGED
    └── consultant.md                 # NEW: the full interview walkthrough, the checklist expanded with
                                      #      the architecture decision each dimension drives, a worked
                                      #      example dialogue, and the build/agreement/scope rules (see 03).
```

Plus the two non-skill obligations every skill edit carries in this repo:

- `plugins/skills-for-langchain/skills/langchain/` — re-synced byte-identical (`00` DC9).
- `.claude/harness-spec.md` — new behavior-inventory rows and component specs for the consultant (`05`).
- `CLAUDE.md` — its one pointer line reviewed and lightly updated if the skill's broadened identity warrants it (`05`); it must stay a pointer, never a component inventory.

## Why the split between SKILL.md and `references/consultant.md`

SKILL.md auto-loads on **every** LangChain code edit (the deltas-only path). Anything placed there is paid on that path even though the interview never runs there. So the split follows the branch the model actually takes (`00` DC8): the parts needed to *recognize the consult situation and hold the posture* stay in SKILL.md (persona, the consult-vs-deltas decision, the thin checklist as a compact list, the reference-usage rule, the design-always/implement-after-agreement rule). The parts needed only *once inside* an interview (the full walkthrough, the per-dimension architecture mapping, the worked example) move to `references/consultant.md`, which the consultant path reads on entry. This keeps the deltas-only path lean while giving the consultant path its depth.

## Authoring principles (apply to every line you write into the skill)

Same doctrine as the earlier plan (`docs/plans/01-overview.md`), because it is what keeps this from rotting:

- **Conviction over compliance.** Every checklist item and every rule carries the *reason* it matters, so Claude can generalize past the cases this plan enumerated. A checklist dimension is written as "ask whether any action needs human approval before it executes, because that is the difference between an agent you can let run and one that needs `interrupt_on` + a checkpointer" — not as a bare "ask about HITL."
- **Do not write what the model already knows.** The consultant content is process and posture, not LangChain facts. If a line would teach Claude something a competent engineer already knows about agent design, cut it.
- **Respect Claude's intelligence (the user's explicit instruction).** The checklist lists *dimensions to ask about*; it does not prescribe the answer. The mapping from a user's goal to an architecture is Claude's judgment, informed by the delta references.
- **No mid-sentence line wrapping** in any generated file. Break only at sentence, list-item, or paragraph boundaries. Hard wraps break future exact-string edits and pollute diffs.

## Success criteria (what "done" means)

Defined concretely in `04`. In one line: the skill enters consultant mode on an agent-building goal and runs a real interview before proposing; it proposes a *current-API* architecture (having read the references) and does not implement until the user agrees; plain code edits still get deltas-only with no interview (no regression); `validate_harness.py` exits 0; and the plugin mirror is byte-identical. The honest caveat (`00` DC10): consult quality is judgment, not a probe-measurable fact, so validation here is lighter than v1.0.0's before/after probe suite and should be presented that way.

## Document map

- `00-decision-log.md` — every decision DC1–DC10 with rationale and the session Q&A record.
- `01-overview.md` — this file.
- `02-skill-md-spec.md` — the exact SKILL.md edits: new description, new body sections, what is preserved.
- `03-consultant-content.md` — the consultant persona, the interview protocol, the thin dimension checklist expanded, the build rules, and the `references/consultant.md` spec with a worked example.
- `04-validation.md` — trigger tests, the consultant dry-run scenarios, the delta-injection regression guard, and the mechanical gates.
- `05-implementation-checklist.md` — the ordered step list for the next session, including plugin sync, harness-spec rows, CLAUDE.md review, release/version handling, and commit/push.
