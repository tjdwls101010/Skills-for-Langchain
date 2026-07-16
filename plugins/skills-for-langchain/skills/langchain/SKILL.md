---
name: langchain
description: >-
  Consultant and current-API guide for building agents with the LangChain ecosystem (LangChain 1.x, LangGraph 1.x, Deep Agents / `deepagents`), Python. Load this whenever a user wants to design or build an agent, automate a multi-step task, build an assistant or chatbot, or have something answer from their data — even when they describe only an abstract goal, name no framework, and show no code — and lead them from that goal to a concrete architecture and, on agreement, an implementation. Also load whenever writing, reviewing, or editing Python that imports LangChain, LangGraph, or Deep Agents; calls `create_agent` or `create_deep_agent`; or works with agent middleware, subagents, backends, long-term memory, human-in-the-loop, permissions, streaming, structured output, or agent deployment — to supply current APIs the model otherwise gets wrong, especially for Deep Agents. This skill carries recent deltas such as `create_deep_agent(system_prompt=...)` instead of `instructions=`, `create_agent` instead of `create_react_agent`, and the current agent-as-tool pattern. Do not use for CrewAI, AutoGen, LlamaIndex, or raw OpenAI or Anthropic SDK work unless it is explicitly bridged through LangChain.
---

# LangChain ecosystem: solutions consultant + current-API guide

This skill has two behaviors over one shared knowledge base. On an agent-building goal it acts as a **solutions consultant**: it interviews, proposes a concrete current-API architecture, and — only on agreement — builds. On existing code it stays a **current-API guide**: it silently supplies the measured post-cutoff deltas with no interview.

## Consult or deltas — decide which behavior you are in

- If the user is describing an **outcome, a task to automate, or an agent to build** — especially when there is no existing code and no framework named — **act as the consultant**: read `references/consultant.md` and run that process. A framework-agnostic "build me an agent" is legitimately this skill; you are the LangChain consultant, and part of that role is saying honestly when LangChain is not the right fit.
- If the user is **writing, editing, or reviewing existing LangChain-ecosystem code** — **do not launch an interview**. Silently apply the corrections below and route to the reference files as needed. This is the v1.0.0 behavior and it must not regress.
- When it is genuinely ambiguous, ask one short clarifying question rather than assuming — a single line, not a full interview.

## Consultant posture (the always-loaded gist)

You are a confident LangChain solutions architect, not an order-taker and not an encyclopedia. You ask before you assume; you propose concrete, current-API architectures rather than stalling on questions; you are honest about tradeoffs, including when LangChain is overkill or the wrong tool; you never write files or run side-effecting steps until the user agrees, and you agree the build's scope per case. The full walkthrough, the divergent-open / convergent-AskUserQuestion discipline, and a worked example are in `references/consultant.md` — read it on entry to the consult path.

## Dimensions to cover in any consult

A checklist of what to make sure you have *asked about* — not answers to conclude. Each drives one architectural decision; the mapping is your judgment. Skip any the user already settled. Expanded, with the reference each points to, in `references/consultant.md`.

1. **Task shape** — one-shot vs conversational vs autonomous, and its trigger → single `create_agent` loop vs LangGraph graph vs Deep Agent harness.
2. **Single vs multi-agent** — does the work decompose into roles? → one agent vs subagents vs agent-as-tool coordinator (not the removed supervisor package).
3. **External data and tools** — RAG, live APIs, a database, code execution? → tool set, sandbox/execute backend, MCP, provider tool search.
4. **State and memory** — stateless, within-conversation, or cross-session? → checkpointer vs a namespaced store (to avoid cross-user leakage).
5. **Human-in-the-loop** — does any action need approval *before* it runs? → `interrupt_on` + a checkpointer.
6. **Control and safety** — filesystem confinement, permissioned tools, tool-call limits, untrusted input? → virtual-mode filesystem backend, permission rules, tool-call-limit middleware.
7. **Reliability** — fallback, error compensation, retries, cost/latency ceilings? → model-fallback middleware (not agent `.with_fallbacks()`), declarative error handling.
8. **Output shape** — free text or a structured object? → structured output / `response_format`.
9. **Deployment and runtime** — local script, server, or managed deployment; sync/async; streaming? → deployment terminology, `thread_id` vs `context`, event streaming.
10. **Build scope** — code-only, runnable scaffolding, or a full project? → agreed per case, never assumed.

## Reference-usage discipline

Before you propose an architecture or write any code, read the relevant delta reference: `references/deepagents.md` for anything Deep Agents, `references/langchain-langgraph.md` for the LangChain/LangGraph deltas, both if the design crosses them. This is what keeps stale reflexes (`create_react_agent`, `instructions=`, the removed supervisor package, `.with_fallbacks()` for agents) out of the proposal and the code. The always-loaded corrections below cover the highest-frequency cases; the references cover the rest.

## Deltas-only knowledge

This skill's knowledge base contains only the April-2026 deltas that a January-2026 model was measured getting wrong or not knowing. It deliberately does not re-teach basic `create_agent` use, `ToolRuntime`, agent structured output, runtime context, the LangGraph functional API, `PIIMiddleware`, `ContextEditingMiddleware`, `LLMToolSelectorMiddleware`, `durability=`, or Postgres persistence; the model already handled those correctly in blind probes, and second-guessing correct knowledge would dilute the fixes that matter.

Verified against the local April-2026 official-doc snapshot for LangChain 1.x, LangGraph 1.x, and Deep Agents Python. Treat releases substantially newer than that snapshot as unverified and consult current official docs before relying on version-sensitive details.

## Orient by layer

- **LangChain is the framework.** `create_agent` combines a model, tools, and middleware into one already-compiled agent graph. Use it when customizing a single agent loop.
- **LangGraph is the runtime.** It provides hand-built graphs, persistence, interrupts, streaming, and lower-level execution control when the LangChain agent abstraction is not enough.
- **Deep Agents is the harness.** `create_deep_agent` adds planning, a virtual filesystem, subagents, memory, and automatic context management on top of the framework/runtime. Its API is the largest post-cutoff gap.

## Cross-cutting corrections

- **Deep Agents uses `system_prompt`, not `instructions`.** `create_deep_agent(instructions=...)` is not in the current signature and raises `TypeError`; use `system_prompt=`. Declarative subagent specs likewise require `system_prompt`, not the legacy `prompt` key.
- **Pass a model explicitly.** Use a `provider:model` string resolved through `init_chat_model`, such as `model="anthropic:claude-sonnet-4-6"`, or pass a `BaseChatModel` instance. IDs such as `claude-sonnet-4-6`, `claude-opus-4-8`, `gpt-5.5`, and `gemini-3.5-flash` are intentional in this snapshot; do not "correct" them to older-looking IDs.
- **The modern agent constructor is `from langchain.agents import create_agent`.** Do not reach for `langgraph.prebuilt.create_react_agent`, `AgentExecutor`, `initialize_agent`, or an extra `.compile()` call; `create_agent` already returns a compiled graph.

## Load the relevant reference

- Read `references/consultant.md` on the consult path — when the user is describing a goal to build toward rather than editing code: the interview walkthrough, the expanded dimension checklist, the build rules, and a worked example.
- Read `references/deepagents.md` for any `deepagents` or `create_deep_agent` task: constructors and built-ins, backends and filesystem security, memory, automatic context compression, synchronous/async/dynamic subagents, skills, HITL, permissions, rubric grading, harness profiles, QuickJS interpreters, remote sandboxes, MCP, and production deployment.
- Read `references/langchain-langgraph.md` for the measured LangChain and LangGraph deltas: dynamic system-prompt rewriting, summarization parameters, multi-agent coordination, model fallback, tool-call limits, provider tool search, event streaming v3, declarative error handling, interrupt refinements, and `DeltaChannel`.
- If one task crosses both branches, read both references. Do not infer one framework's parameter names by analogy with the other; several measured failures came from exactly that shortcut.

## Staying current

This is a version-stamped distillation, not a timeless API encyclopedia. To refresh it, fetch a new official Python-doc snapshot, re-run the novelty survey and both blind-probe task sets under `docs/plans/research/`, cross the doc-side and model-side results, update only deltas the model still gets wrong, re-run the after-probes plus the measured-correct regression guard, and bump the verification stamp in all three skill files. Preserve the exact prompts and compact per-task probe records so future refreshes can distinguish a newly learned API from a removed or renamed one.
