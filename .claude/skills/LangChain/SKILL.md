---
name: LangChain
description: >-
  Current April-2026 Python APIs and gotchas for the LangChain ecosystem: LangChain 1.x, LangGraph 1.x, and the Deep Agents SDK (`deepagents`). Load whenever writing, reviewing, or editing Python that imports LangChain, LangGraph, or Deep Agents; calls `create_agent` or `create_deep_agent`; or works with agent middleware, subagents, backends, long-term memory, human-in-the-loop, permissions, streaming, structured output, or agent deployment, even when the user does not name a version. Load especially for Deep Agents, where older model knowledge is incomplete and confidently wrong. This skill carries recent deltas such as `create_deep_agent(system_prompt=...)` instead of `instructions=`, `create_agent` instead of `create_react_agent`, and the current agent-as-tool pattern. Do not use for CrewAI, AutoGen, LlamaIndex, or raw OpenAI or Anthropic SDK work unless it is explicitly bridged through LangChain.
---

# LangChain ecosystem: current APIs and gotchas

This skill contains only the April-2026 deltas that a January-2026 model was measured getting wrong or not knowing. It deliberately does not re-teach basic `create_agent` use, `ToolRuntime`, agent structured output, runtime context, the LangGraph functional API, `PIIMiddleware`, `ContextEditingMiddleware`, `LLMToolSelectorMiddleware`, `durability=`, or Postgres persistence; the model already handled those correctly in blind probes, and second-guessing correct knowledge would dilute the fixes that matter.

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

- Read `references/deepagents.md` for any `deepagents` or `create_deep_agent` task: constructors and built-ins, backends and filesystem security, memory, automatic context compression, synchronous/async/dynamic subagents, skills, HITL, permissions, rubric grading, harness profiles, QuickJS interpreters, remote sandboxes, MCP, and production deployment.
- Read `references/langchain-langgraph.md` for the measured LangChain and LangGraph deltas: dynamic system-prompt rewriting, summarization parameters, multi-agent coordination, model fallback, tool-call limits, provider tool search, event streaming v3, declarative error handling, interrupt refinements, and `DeltaChannel`.
- If one task crosses both branches, read both references. Do not infer one framework's parameter names by analogy with the other; several measured failures came from exactly that shortcut.

## Staying current

This is a version-stamped distillation, not a timeless API encyclopedia. To refresh it, fetch a new official Python-doc snapshot, re-run the novelty survey and both blind-probe task sets under `docs/plans/research/`, cross the doc-side and model-side results, update only deltas the model still gets wrong, re-run the after-probes plus the measured-correct regression guard, and bump the verification stamp in all three skill files. Preserve the exact prompts and compact per-task probe records so future refreshes can distinguish a newly learned API from a removed or renamed one.
