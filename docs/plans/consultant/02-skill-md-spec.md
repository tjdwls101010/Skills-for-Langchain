# 02 — SKILL.md specification (the edit)

This specifies exactly what changes in `.claude/skills/langchain/SKILL.md`. The current file is 33 lines (frontmatter + a short body: three-layer model, cross-cutting corrections, reference routing, maintenance note). The edit **adds** the consultant layer and **broadens** the description; it **preserves** everything the deltas-only path depends on. Do not delete the existing knowledge-facing content — the deltas-only behavior (`00` DC2) rides on it.

## Frontmatter: `description` (broaden, keep the near-miss boundary)

The description is the only trigger signal, and it now has to trigger on **two** situations: (a) working on LangChain-ecosystem Python (existing), and (b) a user describing an agent to build / a task to automate / an outcome to reach with an agent (new). It must keep the existing near-miss boundary so it does not steal triggers from non-LangChain agent frameworks.

The existing description already covers (a) well. The edit **prepends a consultant clause** and keeps the rest. Recommended shape (the implementation session may refine wording, but must preserve: the consultant intent, the "even without naming LangChain / even without code" cue, and the CrewAI/AutoGen/LlamaIndex/raw-SDK near-miss boundary):

> Consultant and current-API guide for building agents with the LangChain ecosystem (LangChain 1.x, LangGraph 1.x, Deep Agents / `deepagents`), Python. Load this whenever a user wants to design or build an agent, automate a task with an agent, or have something answer from their data — even when they describe only an abstract goal and name no framework and show no code — and lead them from that goal to a concrete architecture and, on agreement, an implementation. Also load whenever writing, reviewing, or editing Python that imports LangChain, LangGraph, or Deep Agents; calls `create_agent` or `create_deep_agent`; or works with agent middleware, subagents, backends, long-term memory, human-in-the-loop, permissions, streaming, structured output, or agent deployment — to supply current APIs the model otherwise gets wrong, especially for Deep Agents. Do not use for CrewAI, AutoGen, LlamaIndex, or raw OpenAI or Anthropic SDK work unless it is explicitly bridged through LangChain.

Notes for the implementer:

- **Do not set `disable-model-invocation`.** The skill must stay model-invocable (auto-triggering) so the deltas-only path survives and so a natural-language goal can enter consultant mode (`00` DC3). It stays user-invocable too (`/langchain`).
- **The consultant path is a body decision, not a trigger switch.** The description gets Claude to *load* the skill in both situations; the body decides *which behavior to run*. Do not try to encode consult-vs-deltas in the frontmatter.
- **Watch the near-miss.** Because the positive triggers are now broader ("build an agent" with no framework named), the CrewAI/AutoGen/LlamaIndex/raw-SDK exclusion is doing more work — keep it explicit. A framework-agnostic "build me an agent" legitimately loads this skill (it is the LangChain consultant); the boundary only blocks requests that name a *different* framework. See `03` for how the persona handles the honest "LangChain may not be the best fit here" case.
- Length: `description` + `when_to_use` is truncated at 1,536 characters in the listing; keep the triggering-critical consultant clause first (it is, above).

## Body: what to add, what to keep

The body gains a consultant section at the top and keeps the existing knowledge sections below it. Target order (keeps the auto-inject path's essentials intact while making the consultant behavior the first thing a reader sees, since that is the higher-intent path):

1. **Title + one-line identity.** e.g. "LangChain ecosystem: solutions consultant + current-API guide."

2. **The consult-vs-deltas branch (short, decisive).** The single most important new paragraph. Tell Claude how to decide which behavior it is in:
   - If the user is describing an outcome, a task to automate, or an agent to build — *especially if there is no existing code and no framework named* — **act as the consultant**: read `references/consultant.md` and run that process.
   - If the user is writing, editing, or reviewing existing LangChain-ecosystem code — **do not launch an interview**; silently apply the corrections below and route to the reference files as needed.
   - When genuinely ambiguous, ask one short question rather than assuming (a single clarifying line, not a full interview).

3. **The consultant persona + posture (compact).** 4–8 lines capturing: you are a LangChain solutions consultant; you ask before you assume; you propose concrete, current-API architectures; you are honest about tradeoffs and about when LangChain is not the right tool; you never write files or run side-effecting steps until the user agrees, and you agree the build's scope per case. Full detail lives in `references/consultant.md`; this is the always-loaded gist.

4. **The thin dimension checklist (compact list form).** The list of dimensions to cover in any consult, each with the one architectural decision it drives (see `03` for the authored version). Keep it as a scannable list here; the expanded per-dimension guidance and the worked example are in `references/consultant.md`.

5. **Reference-usage rule (the discipline).** State plainly: before proposing an architecture or writing any code, read the relevant delta reference (`references/deepagents.md` for anything Deep Agents; `references/langchain-langgraph.md` for the LangChain/LangGraph deltas; both if the design crosses them). This is what keeps stale reflexes (`create_react_agent`, `instructions=`, the removed supervisor package, `.with_fallbacks()` for agents) out of the proposal and the code.

6. **Existing "Orient by layer" three-layer model** (LangChain = framework, LangGraph = runtime, Deep Agents = harness) — **kept verbatim**. It serves both paths.

7. **Existing "Cross-cutting corrections"** (`system_prompt=` not `instructions=`; model IDs are real/future and must not be "corrected"; explicit `provider:model`; `create_agent` baseline) — **kept verbatim**. These are the highest-frequency deltas and must remain on the always-loaded path.

8. **Existing "Load the relevant reference" routing** — **kept**, and extended by one line so the routing table now also mentions `references/consultant.md` for the consult path.

9. **Existing "Staying current" maintenance note** — **kept verbatim**. It documents the refresh procedure for the knowledge, which this change does not alter.

## What must NOT change

- The three delta references' content and the maintenance procedure.
- The cross-cutting corrections and the three-layer model wording (they are measured and load-bearing for deltas-only).
- The model-invocable / user-invocable posture (no `disable-model-invocation`).
- The `name: langchain` and the directory (so the command stays `/langchain` and the plugin identity is stable).

## Size budget

The current body is intentionally short. The added consultant gist (items 2–5, plus a routing line) should stay roughly in the 40–70 line range so the always-loaded path does not bloat (`00` DC8). If the consultant material you want to include grows past that, that is the signal to push it into `references/consultant.md`, not to let SKILL.md swell — the deltas-only path pays for every line here.

## Frontmatter fields checklist (leave as-is unless noted)

| Field | Decision |
|---|---|
| `name` | `langchain` (unchanged). |
| `description` | Broadened per above. |
| `disable-model-invocation` | **Absent** (must stay auto-triggering). |
| `user-invocable` | Leave default (usable via `/langchain`). |
| `allowed-tools` | Not set. The consultant may write files during a build, but only after agreement; pre-approving Write/Edit is not warranted and could surprise users during a design-only conversation. Let the normal permission flow apply. |
| `paths` | Not set (the skill applies across the repo / any project). |
| `hooks`, `context: fork`, `agent:` | Not set. The consultant is an interactive main-thread conversation, not a forked task. |
