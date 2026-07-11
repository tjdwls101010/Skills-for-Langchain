# Probe results (axis 2) — what Claude actually gets wrong

Empirical measurement, not self-report. 26 blind tasks (Opus 4.8, Jan-2026 cutoff, no docs/web) → doc-armed grading against the April-2026 docs. Full per-task detail: `../../../scratchpad/probe-compact.json` (and the raw workflow output). Verdict key: `correct` = Claude already knows it (EXCLUDE) · `outdated_confident` = confidently wrong (HIGHEST value) · `partial` = right scaffolding, wrong specifics · `unknown` = didn't know.

## Headline

| verdict | count | tasks |
|---|---|---|
| correct (exclude) | 7 | A1, A2, A3, A5, A6, B1, B4 |
| partial (include) | 15 | A4, B2, B3, C1–C8, C10, C11, C13, C14 |
| outdated_confident (include) | 4 | A7, B5, C9, C12 |

**19 of 26 include; 7 exclude.** The doc-survey (axis 1) flagged far more as NOVEL/CHANGED than Claude actually gets wrong — exactly why empirical measurement was necessary. **Claude already writes modern LangChain-core and LangGraph-runtime code correctly.** The real gap is **DeepAgents (all 14 tasks flagged) plus ~5 specific LangChain/LangGraph deltas.**

## The dominant cross-cutting gotcha

**`create_deep_agent(instructions=...)` → `create_deep_agent(system_prompt=...)`.** Claude used the deprecated `instructions=` in essentially *every* DeepAgents task (C1, C2, C5, C6, C7, C8, C11, C12, C14). `instructions=` is not in the current signature and raises `TypeError`. This single correction fixes a huge fraction of DeepAgents errors — it belongs in the SKILL.md body (applies on every DeepAgents task), not buried per-topic. Two more recurring cross-cutting items: **model IDs in the docs are real/future** (`claude-sonnet-4-6`, `gpt-5.5` — never "correct" them) and **`model=` must be passed explicitly** as a `provider:model` string (Claude often omits it).

## EXCLUDE — Claude already knows (verified correct, April-2026)

| id | topic | why excluded |
|---|---|---|
| A1 | `create_agent` basic tool-calling agent | used `create_agent` from `langchain.agents` correctly; NOT the deprecated `create_react_agent`/`AgentExecutor` |
| A2 | custom middleware (`wrap_model_call`) | subclassed `AgentMiddleware`, `wrap_model_call(request, handler)`, `request.override(...)` — all current; even named `@dynamic_prompt` |
| A3 | agent structured output | `response_format=` → `result["structured_response"]`, `ToolStrategy`/`ProviderStrategy` — correct |
| A5 | tool runtime access | unified `ToolRuntime` param (`runtime.context/.store/.state`) — correct |
| A6 | per-invocation runtime context | `context_schema=` + `context=` at invoke, read `runtime.context` — correct |
| B1 | LangGraph node runtime context | `Runtime[Context]` node param, `context=` at invoke — correct |
| B4 | LangGraph functional API | `@entrypoint`/`@task`, injected `previous=`, `entrypoint.final()` — correct verbatim |

(Plan rationale note: these are recorded as "verified current as of April-2026 snapshot," not silently dropped, so a future refresh knows they were checked.)

## INCLUDE — the delta the skill must carry

### LangChain (2)
- **A4 — `SummarizationMiddleware` params (high).** Deprecated `max_tokens_before_summary`/`messages_to_keep`/`summary_prefix` → `trigger=("tokens",N)` / `keep=("messages",N)` ContextSize tuples (also `("fraction",…)`, multi-threshold dicts). Mechanism/import known; only the params are wrong.
- **A7 — multi-agent (high, outdated_confident).** Claude reached for `create_supervisor`/`langgraph-supervisor` and called it "current." → **deprecated/unmaintained.** Current: agent-as-tool (wrap each `create_agent` sub-agent in a `@tool`) or single-dispatch `task(agent_name, description)` over a registry. No `.compile()` (create_agent returns a compiled graph).

### LangGraph (3)
- **B5 — event streaming (high, outdated_confident).** Claude used old `stream(stream_mode=[...])` v1 `(mode, chunk)` tuples and asserted `stream_events` is the *older* API — **backwards.** Current: `stream_events(..., version="v3")` with typed projections (`stream.messages/.values/.tool_calls/.interrupts`), `ToolCallTransformer`, `stream.interleave(...)`.
- **B3 — declarative error handling (high).** Caching (`CachePolicy`/`InMemoryCache`) and retry (`RetryPolicy`) Claude knows. **Missed:** `add_node(..., error_handler=fn)` where `fn(state, error: NodeError) -> Command` (from `langgraph.errors`, `langgraph>=1.2`); fires after retries exhausted; `set_node_defaults(...)` for graph-wide.
- **B2 — interrupts (low).** Core `interrupt()`/`Command(resume=...)` known. Thin delta only: `InMemorySaver` (vs `MemorySaver` alias), `stream_events(v3)` as recommended driver, parallel-interrupt id-keyed resume `Command(resume={id: val})`. Marginal — fold in briefly.

### DeepAgents (14) — the core; all include=true
Per topic, the **specific delta** (Claude's scaffolding was often right — carry only the correction):
- **C1/C2 — core + built-ins.** `system_prompt=` not `instructions=`; explicit `provider:model`; full built-in tool list (`write_todos`, `ls/read_file/write_file/edit_file/delete/glob/grep`, `execute`, `task`); seed files via `create_file_data()`; broader built-in capabilities (skills/memory/summarization/prompt-caching/HITL/permissions).
- **C3 — backend security.** `FilesystemBackend(root_dir=..., virtual_mode=True)` — **default `False` = no sandbox**; wrap in `CompositeBackend`.
- **C4 — long-term memory.** `CompositeBackend(default=StateBackend(), routes={"/memories/": StoreBackend(namespace=lambda rt: ...)})`; `StoreBackend` needs a namespace factory (multi-user isolation); pass `store=`.
- **C5 — subagents.** Subagent dict key `system_prompt` not `prompt`; `CompiledSubAgent(..., runnable=graph)` not `graph=`.
- **C6 — async subagents (Claude didn't know).** First-class `AsyncSubAgent` specs → `AsyncSubAgentMiddleware` exposes 5 tools (`start/check/update/cancel/list_async_task`); steer via `update_async_task`, not hand-rolled asyncio.
- **C7 — context engineering.** Summarization + >20k-token offloading are **built-in/automatic** (don't hand-add middleware); thresholds (85% window); optional `create_summarization_tool_middleware`.
- **C8 — skills (Claude didn't know attach).** `skills=[paths]` param → `SkillsMiddleware` auto-added; a `FilesystemBackend` root alone loads nothing. (SKILL.md format itself Claude knows — exclude that part.)
- **C9 — HITL (outdated_confident).** `interrupt_on={tool: {"allowed_decisions":[...]}}` not `interrupt_config`; decisions `approve/edit/reject/respond`; resume `Command(resume={"decisions":[...]})`, `version="v2"`; detect via `result.interrupts`.
- **C10 — permissions (Claude didn't know).** `create_deep_agent(permissions=[FilesystemPermission(operations=[...], paths=[globs], mode="allow"|"deny"|"interrupt")])` — a list, not a backend dict; first-match-wins; `from deepagents import FilesystemPermission`.
- **C11 — harness profiles (Claude didn't know).** `HarnessProfile(...)` + `register_harness_profile("anthropic"|"provider:model", ...)`; ships built-in Anthropic/OpenAI profiles; tunes without touching the call site.
- **C12 — sandboxes/interpreters (outdated_confident).** Sandboxes are **backends, not tools**; `execute` auto-added by `SandboxBackendProtocol`; `LangSmithSandbox`/Daytona/E2B/Modal/etc.; interpreters (QuickJS `CodeInterpreterMiddleware`) are a distinct in-loop feature. Claude reached for the non-existent `PyodideSandboxTool`.
- **C13 — production.** Branding is **LangSmith Deployments** (not "LangGraph Platform"); **Managed Deep Agents** is the recommended path; pass `context=` at invoke. (`langgraph.json`/`langgraph build`/`langgraph_sdk` Claude knows — exclude.)
- **C14 — MCP.** `system_prompt=` not `instructions=`; transport `"http"` (not `"streamable_http"` alias). Integration shape (`MultiServerMCPClient().get_tools()`) known.

## Coverage gaps (under-sampled by the 26 tasks)

The probe is solid for DeepAgents (14 tasks) but **thin where it matters for LangChain/LangGraph breadth**:
- **LangChain built-in middleware catalog:** only `SummarizationMiddleware` (A4) was probed; ~18 other built-ins (`PIIMiddleware`, `ContextEditingMiddleware`, `ModelFallbackMiddleware`, `ProviderToolSearchMiddleware`, `ToolCallLimitMiddleware`, `LLMToolSelectorMiddleware`, `ShellToolMiddleware`, …) untested. A4 (partial) suggests Claude knows the *mechanism* but not each built-in's *specifics* — but that's one data point.
- **LangGraph deltas:** `durability=` (replaces `checkpoint_during`), checkpointer package split, `DeltaChannel`, `defer=True` — not directly probed (B3 covered caching/error-handling).
- **DeepAgents micro-features:** `RubricMiddleware` (LLM-as-judge), dynamic subagents (the "workflow" trigger word), the QuickJS interpreter path — touched but not isolated.

→ A targeted **round-2 mini-probe** on these would convert guesses into measurements before finalizing the include list.

## Round 2 — coverage-gap closure (12 tasks)

Verdicts: **5 correct (exclude), 7 include** (2 outdated_confident, 4 partial, 1 unknown). Key lesson: the LangChain built-in-middleware catalog is **mostly already known** — no full catalog needed, only the specific misses.

**EXCLUDE (Claude already knows):**
- R1 `PIIMiddleware` — correct (class, params, strategies, `apply_to_*` all right).
- R2 `ContextEditingMiddleware`/`ClearToolUsesEdit` — correct verbatim.
- R5 `LLMToolSelectorMiddleware` — correct (`model`, `max_tools`, `always_include`).
- R7 LangGraph `durability=` (`"exit"/"async"/"sync"`, default async) — correct, even named the old `checkpoint_during`.
- R9 Postgres persistence + `EncryptedSerializer.from_pycryptodome_aes()` — correct verbatim.

**INCLUDE (the genuine misses):**
- **R3 — `ModelFallbackMiddleware` (high, outdated_confident).** Claude used `model.with_fallbacks()` + `create_react_agent`. Current: built-in `ModelFallbackMiddleware(first, *rest)` via `middleware=[...]`.
- **R4 — `ToolCallLimitMiddleware` (medium).** `ModelCallLimitMiddleware` Claude knows. Tool limiter's `exit_behavior` defaults to `"continue"` (3 values: continue/error/end); `"end"` only works single-tool.
- **R6 — `ProviderToolSearchMiddleware` (high, unknown).** Claude hand-rolled raw `ChatAnthropic(betas=[...])`. Current: `ProviderToolSearchMiddleware(searchable_tools=[...])` + `@tool(extras={"defer_loading": True})`; provider-gated.
- **R8 — `DeltaChannel` (high).** Claude offloaded the list to the Store (abandoning the reducer). Current: `Annotated[list, DeltaChannel(bulk_reducer, snapshot_frequency=K)]` from `langgraph.channels` (`>=1.2`, beta); bulk reducer must be associative+pure.
- **R10 — `RubricMiddleware` (high, outdated_confident).** Claude claimed "deepagents has no judge-loop primitive" (false) and hand-rolled one. Current: `RubricMiddleware(model=, max_iterations=3, ...)` via `middleware=[...]`; trigger by passing `rubric` on invoke state; fixed verdict enum.
- **R11 — dynamic subagents (high).** Claude emitted N parallel `task` calls. Current: interpreter-based — `CodeInterpreterMiddleware` exposes a `task()` global called from JS `eval` code; the literal word **"workflow"** triggers it.
- **R12 — interpreters / PTC (high).** Claude invented `CodeExecutionMiddleware(sandbox=False)` running Python. Current: `CodeInterpreterMiddleware(ptc=[tools])` — QuickJS (JavaScript, not Python), `eval` tool, `deepagents[quickjs]`; distinct from sandbox backends.

## Consolidated final include list

**Cross-cutting → SKILL.md body:** `system_prompt=` not `instructions=` (deepagents); model IDs are real/future (don't "correct"); pass `model=` explicitly as `provider:model`; `create_agent` is the agent baseline (not `create_react_agent`/`AgentExecutor`).

**LangChain deltas (5):** A4 SummarizationMiddleware params · A7 supervisor→agent-as-tool · R3 ModelFallbackMiddleware · R4 ToolCallLimitMiddleware · R6 ProviderToolSearchMiddleware.

**LangGraph deltas (4):** B5 event streaming (stream_events v3) · B3 declarative error handling · B2 interrupts (thin) · R8 DeltaChannel.

**DeepAgents (16) — the bulk:** C1/C2 core+built-ins · C3 backend security · C4 long-term memory · C5 subagents · C6 async subagents · C7 context engineering · C8 skills · C9 HITL · C10 permissions · C11 harness profiles · C12 sandboxes · C13 production · C14 MCP · R10 rubric · R11 dynamic subagents · R12 interpreters/PTC.

**Excluded (verified current, April-2026):** create_agent basics, custom middleware, structured output, ToolRuntime, context API, PII/ContextEditing/ToolSelector middleware, LangGraph runtime-context, functional API, durability=, Postgres persistence.
