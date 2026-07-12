# LangChain / LangGraph / Deep Agents — Novelty Catalog (April 2026 docs vs. Jan-2026 cutoff)

**Purpose.** Identify the DELTA a Jan-2026-cutoff model (Opus) would get wrong, not know, or write with an outdated idiom — so a skill can carry ONLY what the model doesn't already know. Classifications:

- **NOVEL** — almost certainly post-cutoff or unknown; include.
- **CHANGED** — exists, but the current API/idiom differs from the model's default; include the old→new.
- **KNOWN** — a capable model already handles this; EXCLUDE from a skill.

**Snapshot facts that frame everything.** The docs live at `docs.langchain.com/oss/{python,javascript}/...`. LangChain 1.0 shipped ~Oct 2025; these docs fold in 1.1–1.4 features that are unambiguously post-cutoff. Three-tier mental model the docs push hard (concepts/products.mdx): **Framework = LangChain** (`create_agent`), **Runtime = LangGraph**, **Harness = Deep Agents SDK** (batteries-included). "Studio" is now **LangSmith Studio** (was LangGraph Studio). All model IDs in the docs are future/fictional: `gpt-5.5`, `gpt-5.4`, `gpt-5.4-mini`, `gpt-5-nano`, `claude-opus-4-8`, `claude-opus-4-7`, `claude-sonnet-4-6`, `gemini-3.5-flash`, `gemini-3.1-pro-preview`, open-weight `GLM-5.2`, `Kimi-K2.7`, `MiniMax-M3`, `devstral-2` — a Jan-2026 model will treat these as typos and "correct" them; it must not.

---

## 1. Deep Agents (`deepagents` / `@deepagents`) — HIGHEST NOVELTY

The entire library is post-cutoff. A Jan-2026 model has essentially no correct priors here. Entry points: **`create_deep_agent(...)`** (Python, `from deepagents import create_deep_agent`) / **`createDeepAgent({...})`** (JS, `from "deepagents"`). It pre-assembles a middleware stack on top of LangChain's `create_agent`.

### 1a. Core API surface

| Topic | Novelty | Specific delta / gotcha (exact API) | Source file |
|---|---|---|---|
| `create_deep_agent` / `createDeepAgent` | NOVEL | Main constructor. Params: `model`, `system_prompt`, `tools`, `memory`, `skills`, `backend`, `permissions`, `subagents`, `middleware`, `interrupt_on`, `response_format`, `state_schema`, `context_schema`, `checkpointer`, `store`. | overview, customization |
| Model string format | CHANGED | `provider:model` string resolved via `init_chat_model`, e.g. `"anthropic:claude-sonnet-4-6"`, `"openai:gpt-5.5"`, `"google_genai:gemini-3.5-flash"`, `"baseten:zai-org/GLM-5.2"`. Or a `BaseChatModel` instance. | models, customization |
| "Agent harness" concept | NOVEL | Same tool-calling loop + built-in planning/filesystem/subagents/memory/HITL/summarization. Framework(LangChain) vs Runtime(LangGraph) vs Harness(DeepAgents). | concepts/products, overview |
| Built-in tools | NOVEL | `write_todos` (planning: pending/in_progress/completed), filesystem `ls`/`read_file`/`write_file`/`edit_file`/`delete`/`glob`/`grep`, `execute` (sandbox only), `task` (subagent spawn). `delete` needs `deepagents>=0.7.a1` (recursive `0.7.a2`). | overview |
| Deep Agents Code (`dcode`) | NOVEL | Terminal coding agent (a Claude-Code analog) built on the SDK. Install `curl -LsSf https://langch.in/dcode | bash`. Ships code interpreter → dynamic subagents on by default. | code/overview, subagents |
| ACP / A2A / MCP | NOVEL | Deep agents expose over ACP (Zed etc.); MCP tools via `langchain-mcp-adapters` / `@langchain/mcp-adapters`. | overview, code/mcp-tools |
| Prompt caching auto-on | NOVEL | `AnthropicPromptCachingMiddleware` + `BedrockPromptCachingMiddleware` added automatically for Anthropic/Bedrock models; no config. Override TTL via `AnthropicPromptCachingMiddleware(ttl="1h")` (default `5m`). | overview, customization |

### 1b. Default middleware stack (the load-bearing novel fact)

Order (main agent), first→last: **1** `TodoListMiddleware` → **2** `SkillsMiddleware` (only if `skills`; before filesystem) → **3** `FilesystemMiddleware` (permissions enforcement lives here) → **4** `SubAgentMiddleware` → **5** `SummarizationMiddleware` → **6** `PatchToolCallsMiddleware` (repairs dangling tool calls on resume) → **7** `AsyncSubAgentMiddleware` (if async subagents) → **8** your `middleware=` → **9** harness-profile extras → **10** excluded-tool filtering → **11** prompt-caching (`AnthropicPromptCachingMiddleware`/`BedrockPromptCachingMiddleware`) → **12** `MemoryMiddleware` (if `memory`) → **13** `HumanInTheLoopMiddleware` (if `interrupt_on`).

| Topic | Novelty | Delta / gotcha | Source file |
|---|---|---|---|
| Import paths | NOVEL | `from deepagents.middleware import FilesystemMiddleware, SubAgentMiddleware, SummarizationMiddleware`; `from deepagents.middleware.subagents import CompiledSubAgent`; `from deepagents.backends import StateBackend, StoreBackend, CompositeBackend, FilesystemBackend`; `from deepagents.backends.utils import create_file_data`. | customization, backends |
| Override-by-name merge | NOVEL | A `middleware=` instance whose `.name` matches a default **replaces it in place**; anything else lands after `PatchToolCallsMiddleware`. Requires `deepagents>=0.7.0a3`. Override does NOT merge — you must re-pass `backend`/`permissions`/`subagents`. | customization |
| `FilesystemMiddleware`/`SubAgentMiddleware` are required scaffolding | NOVEL (trap) | Listing them in `excluded_middleware` raises `ValueError`. To hide tools use `excluded_tools`; to remove `task`, disable the general-purpose subagent + pass no sync subagents. | overview, profiles, subagents |
| `FilesystemMiddleware(tools=[...])` allowlist | NOVEL | Restrict visible FS tools (`read_file` mandatory). Requires `deepagents>=0.7.0a4`. | overview |
| `create_summarization_tool_middleware` | NOVEL | Adds a `compact_conversation` tool for on-demand compaction (between tasks) alongside automatic summarization. | customization, context-engineering |

### 1c. Backends (pluggable virtual filesystem)

| Backend | Novelty | Delta / gotcha | Source file |
|---|---|---|---|
| `StateBackend` (default) | NOVEL | Thread-scoped, stored in LangGraph state, persists across turns via checkpointer, NOT across threads. | backends |
| `FilesystemBackend(root_dir=..., virtual_mode=True)` | NOVEL | Local disk. **Security trap:** default `virtual_mode=False` gives NO protection even with `root_dir`; must set `virtual_mode=True` to block `..`/`~`/absolute escapes. Wrap in `CompositeBackend` so internal `/large_tool_results/` and `/conversation_history/` stay ephemeral. | backends |
| `LocalShellBackend` | NOVEL | FS + unrestricted host shell `execute`. `subprocess.run(shell=True)`, no sandbox. `timeout` (120s), `max_output_bytes` (100k), `env`, `inherit_env`. | backends |
| `StoreBackend(namespace=...)` | NOVEL | Cross-thread durable via LangGraph `BaseStore`. `namespace` factory receives a `Runtime`: `rt.context`, `rt.server_info.user.identity`, `rt.execution_info.thread_id`. `namespace` becomes REQUIRED in v0.5.0/1.9.0. | backends |
| `ContextHubBackend("owner/name")` | NOVEL | Durable FS in a LangSmith Context Hub repo; agent repo + linked skill repos under `/skills/`. Needs `LANGSMITH_API_KEY`. | backends |
| `CompositeBackend(default=..., routes={...})` | NOVEL | Prefix routing; longer prefix wins. Canonical long-term-memory pattern: route `/memories/` → `StoreBackend`, default `StateBackend`. | backends, context-engineering |
| Sandbox backends | NOVEL | `SandboxBackendProtocolV2` adds `execute`. Providers: LangSmith, AgentCore, Daytona, Deno/Deno, E2B, Modal, Runloop, Vercel, Runloop, OpenShell, local VFS. Packages: `langchain-daytona`, `langchain-e2b`, `langchain-runloop`, `langchain-vercel-sandbox`, `langchain-agentcore-codeinterpreter`, `langchain-nvidia-openshell`. | sandboxes, backends |
| Backend protocol V1→V2 | CHANGED | `BackendProtocol`→`BackendProtocolV2`; methods return structured `LsResult`/`ReadResult`/`WriteResult`/`EditResult`/`GlobResult`/`GrepResult` with `error` field — **never raise**. V2 adds `readRaw`, binary `Uint8Array`+`mimeType` reads. Multimodal needs `deepagents>=1.9.0`. | backends |
| Backend factory pattern deprecated | CHANGED | Old: `backend=lambda rt: StateBackend(rt)`. New: `backend=StateBackend()` (resolves context internally via `get_config`/`get_store`/`get_runtime`). `BackendContext` → `Runtime` in namespace factories (`deepagents>=0.5.2`/`1.9.1`). | backends |

### 1d. Subagents, skills, memory, context, HITL, rubrics

| Topic | Novelty | Delta / gotcha | Source file |
|---|---|---|---|
| `subagents=` list | NOVEL | Dicts (`SubAgent` spec) or `CompiledSubAgent(name, description, runnable=graph)`. SubAgent fields: `name`, `description`, `system_prompt` (all required), `tools`, `model`, `middleware`, `interrupt_on`, `skills`, `response_format`, `permissions`. Delegated via the `task` tool. | subagents |
| `general-purpose` subagent | NOVEL | Auto-added unless you supply one named `general-purpose`. Inherits main tools/model/skills. Disable via harness profile `general_purpose_subagent=GeneralPurposeSubagentProfile(enabled=False)`. | subagents |
| Async subagents | NOVEL | `AsyncSubAgentMiddleware`, `AsyncSubAgent`; long-running/parallel with mid-flight steering + cancellation. ASGI (co-deployed) vs HTTP (remote) transport; single/split/hybrid topology. | async-subagents |
| Dynamic subagents (Beta) | NOVEL | With `CodeInterpreterMiddleware` (QuickJS, `deepagents[quickjs]`, `langchain-quickjs>=0.2.0`, Py≥3.11), the agent dispatches subagents FROM CODE via a `task()` global. The word "workflow" in the prompt triggers it. `CodeInterpreterMiddleware(subagents=False)` to force normal `task`. | dynamic-subagents, subagents, interpreters |
| `lc_agent_name` metadata | NOVEL | Every subagent/coordinator run tags metadata `{'lc_agent_name': ...}` for LangSmith filtering and per-agent tool branching. `stream.subagents` handles expose `.name/.messages/.tool_calls/.output`. | subagents |
| Skills | NOVEL | `skills=[paths]`. Agent Skills spec (agentskills.io/specification), `SKILL.md` + YAML frontmatter (`name`, `description`, optional `license`/`compatibility`/`metadata`/`allowed-tools`). Progressive disclosure: metadata@startup → body@invoke → `scripts/`/`references/`/`assets/` on demand. `SkillsMiddleware`. Body <5k tokens / <500 lines; files >10MB skipped; last source wins. With `StateBackend`, pass files via `invoke(files={...})` using `create_file_data()`. `deepagents>=1.7.0` (JS). | skills, customization |
| Memory (`AGENTS.md`) | NOVEL | `memory=[paths]` → `MemoryMiddleware`, always loaded (no progressive disclosure). Distinct from skills. Stored in the configured backend. | customization, context-engineering, memory |
| Context compression | NOVEL | Offloading: tool inputs/results >20,000 tokens moved to FS + reference (truncation kicks in ~85% window). Summarization: `SummarizationMiddleware` triggers at 85% of `max_input_tokens` (fallback 170k trigger / 6 msgs), keeps ~10%; falls back on `ContextOverflowError`. Filter summarizer tokens via `metadata["lc_source"]=="summarization"`. | context-engineering |
| `state_schema` | NOVEL | Must subclass `DeepAgentState` (preserves `DeltaChannel` reducer on `messages` → linear checkpoint growth). `deepagents>=0.6.6`. | context-engineering |
| `context_schema` / runtime context | NOVEL/CHANGED | dataclass/TypedDict (Py) or Zod (JS); pass values with `context=` at `invoke`/`ainvoke` (NOT `config.configurable`). Propagates to all subagents; per-subagent via namespaced keys. Tools read `ToolRuntime`. | context-engineering, subagents |
| HITL `interrupt_on` | NOVEL | `{tool: True|False|InterruptOnConfig}`. Decisions: approve/edit/reject/respond. `when` predicate (`ToolCallRequest`→bool) for conditional interrupts (`langchain>=1.3.3`). Resume: `Command(resume={"decisions":[...]})` with same `thread_id`; `version="v2"`. Result `.interrupts` (Py) / `.__interrupt__` (JS). Requires checkpointer. | human-in-the-loop |
| FS permissions | NOVEL | `permissions=[FilesystemPermission(operations=["read"|"write"], paths=["/ws/**"], mode="allow"|"deny"|"interrupt")]`. First-match-wins; default allow. `mode="interrupt"` (`deepagents>=0.6.8`) pauses like HITL. Subagents inherit; `permissions=[]` = unrestricted. Not applied to sandboxes. `deepagents>=0.5.2`. | permissions |
| Harness profiles (Beta) | NOVEL | `HarnessProfile(...)` + `register_harness_profile("anthropic:claude-sonnet-4-6", ...)`. Fields: `base_system_prompt`, `system_prompt_suffix`, `tool_description_overrides`, `excluded_tools`, `excluded_middleware`, `extra_middleware`, `general_purpose_subagent`. Keyed by provider or `provider:model`; merged. Built-in profiles for OpenAI + Anthropic. YAML via `HarnessProfileConfig`; plugins via entry points. JS: `HarnessProfileOptions` / `registerHarnessProfile`. | profiles, customization |
| Provider profiles | NOVEL | `ProviderProfile` (Python-only) packages `init_chat_model` kwargs: `init_kwargs`, `pre_init`, `init_kwargs_factory`. | profiles, models |
| Prompt assembly | NOVEL | 4 slots: `USER`(system_prompt=) → (`BASE` default or `CUSTOM` profile.base_system_prompt) → `SUFFIX`(profile.system_prompt_suffix). USER always front, SUFFIX always last. | customization |
| `RubricMiddleware` (Beta) | NOVEL | `deepagents>=0.6.5`. LLM-as-judge self-grading loop. Args `model`, `system_prompt`, `tools`, `max_iterations`(3), `on_evaluation`. Pass `rubric` string at invoke. Per-pass results: satisfied/needs_revision/failed/grader_error; cap exhaustion is terminal `_rubric_status=max_iterations_reached`. Emits `rubric_evaluation_start/end` on `stream.custom`; code-generation examples use the same middleware class. | rubric, code/goals-and-rubrics |
| Structured output | NOVEL | `response_format=` → captured in state `structured_response` (Py) / `structuredResponse` (JS). Accepts Pydantic/`ToolStrategy(...)`/`ProviderStrategy(...)`/raw schema (Zod/JSON schema in JS). Subagent structured output `deepagents>=0.5.3`/`1.8.4`. | customization, subagents |
| Interpreters | NOVEL | QuickJS `eval` tool for programmatic tool-calling/batching, scoped, no shell/network/installs. | interpreters, customization |
| Production | NOVEL | Managed Deep Agents (LangSmith, private preview) or self-host `langgraph build` → Docker. `langgraph.json` config, `langgraph dev`. `durability=` param, `SandboxSyncMiddleware` (sync skills/memories in `before_agent`, out in `after_agent`). Multi-tenancy: per-user sandboxes, scoped threads, RBAC, auth proxy. Used in prod by OpenSWE + LangSmith Fleet. | going-to-production, comparison |

**Deep Agents structure note:** cleanly splits **Python vs JS** (heavy `:::python`/`:::js` duplication; JS lags on version numbers: e.g. `deepagents 1.9.x` vs Python `0.5.x`, and JS lacks provider profiles + plugin registration). Also splits by **subtopic** (backends / subagents / skills / memory / HITL / profiles), each self-contained enough that a task opens one.

---

## 2. LangChain v1.0 — Middleware (`langchain.agents.middleware`)

Baseline the model defaults to: `create_react_agent` (langgraph.prebuilt) or legacy `AgentExecutor`/`initialize_agent`; runtime via `config={"configurable":{...}}`; tool state via `InjectedState`/`RunnableConfig`. The docs never mention `create_react_agent`.

| Topic | Novelty | Delta / gotcha (old→new) | Source |
|---|---|---|---|
| `create_agent` | CHANGED | `from langchain.agents import create_agent` (Py) / `createAgent` from `"langchain"` (JS). Replaces `create_react_agent`/`AgentExecutor`. `middleware=[...]` kwarg is new. "Agent = Model + Harness." | agents, overview |
| `middleware=[...]` abstraction | NOVEL | Entire concept. All built-ins + hooks + `AgentMiddleware`/`AgentState` from `langchain.agents.middleware`. | overview |
| Node hooks `before_agent`/`after_agent` | NOVEL | Once per invocation (outermost). | custom |
| Node hooks `before_model`/`after_model` | NOVEL | Return dict merged via reducers; args `state`, `runtime`. Async `abefore_model`/etc. | custom |
| `wrap_model_call` | NOVEL | `(request: ModelRequest, handler) -> ModelResponse`. **Replaces early-v1.0 `modify_model_request`** (gone). | custom |
| `wrap_tool_call` | NOVEL | `(request, handler)`; can return a `Command`. | custom |
| `@dynamic_prompt` | NOVEL | `(request: ModelRequest) -> str`. Replaces `prompt=`/`state_modifier=`. | custom, runtime |
| `@hook_config(can_jump_to=[...])` + `jump_to` | NOVEL | Return `{"jump_to": "end"|"tools"|"model"}`. JS `jumpTo`/`canJumpTo`. | custom |
| `ModelRequest` | NOVEL | `.system_message` (always a `SystemMessage`, even from a string prompt), `.state`, `.runtime`, `.tools`; `.override(tools=..., system_prompt=..., model=..., messages=..., response_format=...)`. | custom, context-engineering |
| `ModelResponse`/`ExtendedModelResponse` | NOVEL | Py state-inject: `ExtendedModelResponse(model_response=resp, command=Command(update={...}))`. **JS returns a `Command` directly** — languages differ. | custom |
| `AgentMiddleware` / `AgentState` | NOVEL | Subclass base; custom state = subclass `AgentState` + `NotRequired[...]`, pass `state_schema=`. JS `createMiddleware({...})` / `new StateSchema({...})`. | custom |
| `SummarizationMiddleware` | NOVEL/CHANGED | `trigger=("tokens",4000)`, `keep=("messages",20)` (ContextSize tuples / TriggerClause dicts; also `("fraction",…)`). **Deprecated params a model will emit:** `max_tokens_before_summary`, `messages_to_keep`, `summary_prefix`. | built-in |
| `HumanInTheLoopMiddleware` | NOVEL | `interrupt_on={tool:{"allowed_decisions":["approve","edit","reject"]}}`. Needs checkpointer. | built-in |
| `ModelCallLimitMiddleware`/`ToolCallLimitMiddleware` | NOVEL | `thread_limit`/`run_limit`/`exit_behavior`. `ToolCallLimitExceededError`. | built-in |
| `ModelFallbackMiddleware` | NOVEL | Variadic model list. | built-in |
| `ModelRetryMiddleware`/`ToolRetryMiddleware` | NOVEL | `max_retries`,`backoff_factor`,`initial_delay`,`retry_on`,`on_failure`. JS `onFailure` uses `"continue"`/`"error"` (Py still `"return_message"`/`"raise"`). | built-in, agents |
| `PIIMiddleware` | NOVEL | `PIIMiddleware("email", strategy="redact", apply_to_input=True)`. Strategies block/redact/mask/hash; types email/credit_card/ip/mac_address/url. `apply_to_output` needs `langchain>=1.3.2`. | built-in, agents |
| `TodoListMiddleware` | NOVEL | Adds `write_todos`. | built-in |
| `LLMToolSelectorMiddleware` | NOVEL | `model`,`max_tools`,`always_include`. Pre-filters tools. | built-in |
| `LLMToolEmulator` | NOVEL | No `Middleware` suffix (Py); JS `toolEmulatorMiddleware`. `tools=None` emulates all. | built-in |
| `ContextEditingMiddleware` + `ClearToolUsesEdit` | NOVEL | `edits=[ClearToolUsesEdit(trigger=100000, keep=3, clear_tool_inputs=..., exclude_tools=..., placeholder=...)]`. JS `triggerTokens`/`clearToolInputs`/`excludeTools`, `new ClearToolUsesEdit({...})`. | built-in |
| `ProviderToolSearchMiddleware` + `@tool(extras={"defer_loading":True})` | NOVEL | Defers tools behind provider server-side tool search; provider-gated (Claude Sonnet/Opus 4+/Haiku 4.5+, OpenAI gpt-5.5+) else `ValueError`. | built-in |
| `ShellToolMiddleware` + policies | NOVEL | `HostExecutionPolicy`/`DockerExecutionPolicy`/`CodexSandboxExecutionPolicy`, `RedactionRule`. Python-only. | built-in |
| `FilesystemFileSearchMiddleware` | NOVEL | `glob_search`/`grep_search`, `use_ripgrep`. Python-only. | built-in |
| Stream transformers | NOVEL | class attr `transformers=(Factory,)` / JS `streamTransformers`. `langchain>=1.3.2`(Py)/`1.4.3`(JS). | custom |
| Execution order | NOVEL | before_* first→last; after_* last→first; wrap_* nested (first = outermost). | custom |

---

## 3. LangChain v1.0 — Multi-agent, structured output, runtime, memory

| Topic | Novelty | Delta / gotcha (old→new) | Source |
|---|---|---|---|
| Runtime context / `context_schema` | CHANGED | `create_agent(context_schema=Context)` + `agent.invoke(..., context=Context(...))`, read `runtime.context.x`. Replaces `config_schema` + `config={"configurable":{...}}`. **`thread_id` still goes in `configurable`** (split trap). | runtime, context-engineering |
| `Runtime` object | NOVEL | `from langgraph.runtime import Runtime`; `runtime.context`, `runtime.store`, `runtime.execution_info.thread_id/run_id`, `runtime.server_info.assistant_id/user.identity`. Version-gated (`langgraph>=1.1.5` / `@langchain/langgraph>=1.2.8`); `server_info` None off LangGraph Server. | runtime |
| `ToolRuntime` injected param | CHANGED | `def tool(runtime: ToolRuntime[Context]) -> str: runtime.context.user_id / runtime.store / runtime.state / runtime.tool_call_id`. **Replaces `InjectedState`/`InjectedStore`/`InjectedToolCallId`/`config: RunnableConfig`.** | runtime, tools |
| `response_format=` on agents | NOVEL/CHANGED | Result in `result["structured_response"]` (JS `structuredResponse`). NOT `.with_structured_output()` (that's for bare models only). | structured-output, agents |
| `ToolStrategy`/`ProviderStrategy` | NOVEL | `from langchain.agents.structured_output import ToolStrategy, ProviderStrategy`. Bare `response_format=Schema` auto-picks via model profile. `ProviderStrategy(schema, strict=...)` (strict needs `langchain>=1.2`); `ToolStrategy(schema, tool_message_content=..., handle_errors=...)`. Errors: `StructuredOutputValidationError`, `MultipleStructuredOutputsError`. JS accepts any Standard Schema (Zod/Valibot). | structured-output |
| Subagents = agent-as-tool | CHANGED | Wrap `create_agent(...)` in a `@tool`, call `.invoke({"messages":[...]})`, return last message. **`langgraph-supervisor`/`create_supervisor` no longer maintained** — model will wrongly recommend it. Single-dispatch `task(agent_name, description)` over a registry pattern. | multi-agent/subagents, index |
| Subagent checkpointer modes | NOVEL | "inherited checkpointer" (default, fresh state, parallel-safe) vs `checkpointer=True` continuations; `get_state(subgraphs=True)` can't see tool-invoked subagents. | multi-agent/subagents |
| Handoffs via `Command` | CHANGED | Tool returns `Command(goto="agent", graph=Command.PARENT, update={"messages":[AIMessage, ToolMessage(...)]})`. Must pair the triggering AIMessage + matching-`tool_call_id` ToolMessage or history is malformed. "Handoffs" naming credited to OpenAI. | multi-agent/handoffs |
| LangChain "skills" pattern | NOVEL | `load_skill(skill_name)` progressive-disclosure tool; backed by `github.com/langchain-ai/langchain-skills` + agentskills.io. Distinct from Deep Agents' built-in skills. | multi-agent/skills |
| Router pattern | KNOWN/CHANGED | `Send`/`Command(goto=)` from `langgraph.types`; only the "router vs supervisor" framing is delta. | multi-agent/router |
| Message `content_blocks` | NOVEL/CHANGED | `result["messages"][-1].content_blocks` (v1 typed content-blocks API) alongside `.content`. | messages, structured-output |
| `stream_events(version="v3")` | CHANGED | v3 stream (old model emits v1/v2). | short-term-memory, event-streaming |
| Short-term memory | KNOWN | `checkpointer=InMemorySaver()`+`thread_id`; `PostgresSaver.from_conn_string`. Delta only in `create_agent` surface. | short-term-memory |
| Long-term memory / store | CHANGED | `InMemoryStore` get/put by namespace+key is KNOWN; new plumbing is `store=` on `create_agent` + `runtime.store`. | long-term-memory, context-engineering |
| Model profiles | NOVEL | `init_chat_model("gpt-5.5", profile={...})`; feature gating (native structured output needs `langchain>=1.1`). | structured-output, built-in |

**LangChain structure note:** middleware core is fairly self-contained, but multi-agent + context-engineering are essentially middleware+LangGraph tutorials — heavily interwoven with `Command`/`Send`/`checkpointer`/`store`/subgraphs and with the shared Runtime/context model. Splits well by **Python vs JS** (PascalCase classes vs camelCase factories: `SummarizationMiddleware` vs `summarizationMiddleware`).

---

## 4. LangGraph v1.0–v1.2 — CHANGED-heavy (core StateGraph is KNOWN, EXCLUDE)

A capable model already knows `StateGraph`/`add_node`/`add_edge`/conditional edges/`Command`/`Send`/reducers/checkpointer concept/time-travel — EXCLUDE those. Only the deltas below matter.

| Topic | Novelty | Delta / gotcha (old→new) | Source |
|---|---|---|---|
| Runtime object + context | NOVEL | Nodes take `(state, runtime: Runtime[Context])`; read `runtime.context.x` (was `config["configurable"]`). `Runtime` also has `.store`, `.stream_writer`, `.execution_info.thread_id`, `.server_info`, `.heartbeat`, `.control`. `from langgraph.runtime import Runtime`. | graph-api |
| `context_schema` on StateGraph | CHANGED | `StateGraph(State, context_schema=Context)` replaces `config_schema=` (0 hits in docs). Invoke `graph.invoke(inputs, context={...})` — new top-level `context=`, not `config={"configurable":{...}}`. | graph-api, stores, add-memory |
| Durability `durability=` | NOVEL | `invoke/stream(..., durability="exit"|"async"|"sync")` (`"async"` default). Replaces `checkpoint_during` boolean (0 hits). | checkpointers, thinking-in-langgraph |
| `stream_events(version="v3")` | NOVEL | New recommended in-process streaming (v1.2): typed projections `stream.messages/.values/.output/.subgraphs/.interrupts/.interrupted/.extensions`, `.interleave(...)`. Async `astream_events`. | event-streaming, interrupts |
| Stream transformers | NOVEL | `StreamTransformer` (`init/process/finalize/fail`, `required_stream_modes`), `StreamChannel`, `ProtocolEvent`, built-in `ToolCallTransformer` (`langgraph.prebuilt`) → `stream.tool_calls`. `transformers=[...]` at compile/call. | event-streaming |
| Streaming v2 `StreamPart` | CHANGED | `stream(..., version="v2")` (≥1.1) yields uniform `StreamPart` dicts `{type, ns, data}` (`ValuesStreamPart` etc. from `langgraph.types`) instead of raw dicts/tuples. | streaming |
| `GraphOutput` from invoke (v2) | CHANGED | `invoke(..., version="v2")` returns `GraphOutput` with `.value`/`.interrupts` (tuple), not a plain dict with `__interrupt__`. | streaming |
| Node caching `CachePolicy` | NOVEL | `add_node(..., cache_policy=CachePolicy(ttl=120))` + `compile(cache=InMemoryCache())`. `from langgraph.cache.memory import InMemoryCache/SqliteCache`, `from langgraph.types import CachePolicy`. | graph-api, use-graph-api |
| Deferred nodes `defer=True` | NOVEL | `add_node(d, defer=True)` waits for all superstep tasks (fan-in / map-reduce without barrier edges). | use-graph-api |
| Declarative error handling | NOVEL | `langgraph>=1.2`. `add_node(..., error_handler=fn)` where `fn(state, error: NodeError) -> Command` runs compensation/saga after retries. `from langgraph.errors import NodeError` (injected by annotation like Runtime). | thinking-in-langgraph, fault-tolerance |
| Graph-wide node defaults | NOVEL | `set_node_defaults()` / `setNodeDefaults()` for graph-wide `retry_policy`/`error_handler`/`timeout`/`cache_policy`. | fault-tolerance |
| `DeltaChannel` | NOVEL | `langgraph>=1.2`, beta. `Annotated[list, DeltaChannel(bulk_reducer, snapshot_frequency=K)]` — stores per-step deltas → O(1) checkpoint blobs. Bulk reducer `(state, Sequence[writes])` must be **associative + pure** (runs on reconstruction). `from langgraph.channels import DeltaChannel`. | pregel, checkpointers |
| Checkpointer package split | CHANGED | Separate libs: `langgraph-checkpoint` (`InMemorySaver`), `-sqlite`, `-postgres`, `langchain-azure-cosmosdb` (`CosmosDBSaver`). `InMemorySaver` (Py) vs `MemorySaver` (JS). `adelete_thread` now required; `EncryptedSerializer.from_pycryptodome_aes()` (`LANGGRAPH_AES_KEY`); `langgraph-checkpoint-conformance` suite. | checkpointers |
| `interrupt()` only HITL pattern | CHANGED | `raise NodeInterrupt` GONE (0 hits). Static `interrupt_before/after` demoted to debugging only. `from langgraph.types import interrupt`. **No `while True`+interrupt loops** (exponential replay) — use a conditional-edge re-prompt loop. | interrupts |
| Multiple-interrupt resume map | CHANGED | Parallel interrupts resume via `Command(resume={interrupt_id: value, ...})` keyed by id; `isInterrupted()`, `INTERRUPT`/`__interrupt__`; interrupts carry `id`. | interrupts |
| `create_agent` location moved | CHANGED | `from langchain.agents import create_agent` (was `langgraph.prebuilt.create_react_agent`, 0 hits). Returns a compiled graph; does NOT support Pydantic state schemas. | graph-api, use-subgraphs |
| `tools` stream mode + `useStream.toolProgress` | NOVEL (JS) | `streamMode: "tools"` → `on_tool_start/event/end/error`; async-generator tools yield progress; `useStream` (`@langchain/langgraph-sdk/react`) exposes `toolProgress[]`. | streaming |
| langchain v1 import reshuffle | CHANGED | `from langchain.tools import tool`, `from langchain.messages import ...`, `from langchain.chat_models import init_chat_model` (were `langchain_core.*`). | thinking-in-langgraph, interrupts |
| Backward-compat model | NOVEL (conceptual) | Latest deployed graph always runs against old checkpoints; only node rename/removal breaks interrupted threads (edge topology not persisted). Patterns: `NotRequired` fields, add-then-remove renames, `flow_version` stamping. | backward-compatibility |
| Functional API | CHANGED | `@entrypoint`/`@task` from `langgraph.func`; short-term memory via `previous=` (Py) / `getPreviousState()` (JS); `entrypoint.final(value=, save=)` decouples return from checkpointed value. | functional-api |
| JS `StateSchema`/`MessagesValue` | CHANGED (JS) | `Annotation.Root` → `new StateSchema({...})` + Zod, `MessagesValue`, `new ReducedValue(...)`. | overview, checkpointers |
| Core StateGraph / edges / Command / Send / reducers / time-travel | KNOWN | EXCLUDE. Only note: `Command(resume=...)` is the only Command form valid as invoke input. | interrupts |

**LangGraph structure note:** orchestration primitives are mostly self-contained, but agent/model/tool construction is interwoven with LangChain v1 (`create_agent`, `tool`, `init_chat_model`, message classes all now import from top-level `langchain.*`). This is CHANGED-dominated, not NOVEL — the smallest branch by distilled volume.

---

## Top gotchas (sharpest, ranked) — a model will confidently get these wrong

1. **`create_agent`, not `create_react_agent`.** `from langchain.agents import create_agent`. The `middleware=` kwarg doesn't exist on the old function. `initialize_agent`/`AgentExecutor`/LCEL agent constructors are fully absent from the docs.
2. **Deep Agents exists and is a whole library.** `create_deep_agent`/`createDeepAgent` from `deepagents`; the harness concept, the default 13-layer middleware stack, backends, subagents, skills, profiles — none of it is in a Jan-2026 model's priors.
3. **`create_supervisor` / `langgraph-supervisor` is deprecated / unmaintained.** Use the agent-as-tool subagents pattern. Model will still reach for `create_supervisor`.
4. **Runtime data is `context=`, not `config={"configurable":{...}}`.** `context_schema=` on the constructor, read via `runtime.context.x`. BUT `thread_id` still lives in `configurable` — the split is the trap.
5. **Tools read runtime via one `ToolRuntime` param** (`runtime.context/.store/.state/.tool_call_id`), replacing `InjectedState`/`InjectedStore`/`InjectedToolCallId`/`RunnableConfig`.
6. **`wrap_model_call` replaced `modify_model_request`.** Idiom: `handler(request.override(...))`. Same for `wrap_tool_call`.
7. **`SummarizationMiddleware` params changed:** `trigger=("tokens",N)`/`keep=("messages",N)`, not `max_tokens_before_summary`/`messages_to_keep`/`summary_prefix`.
8. **Structured output on agents uses `response_format=` → `result["structured_response"]`**, with `ToolStrategy`/`ProviderStrategy` from `langchain.agents.structured_output`. `.with_structured_output()` is bare-model only.
9. **Deep Agents runtime data goes to `context=` at invoke**, and it auto-propagates to all subagents; per-subagent uses namespaced context keys.
10. **Deep Agents backend security:** `FilesystemBackend` default `virtual_mode=False` = no protection; `StateBackend` is thread-scoped only; long-term memory needs a `CompositeBackend` routing `/memories/` to a `StoreBackend`.
11. **`FilesystemMiddleware`/`SubAgentMiddleware` can't be excluded** (ValueError) — use `excluded_tools` / disable the general-purpose subagent instead.
12. **Deep Agents HITL resume:** `Command(resume={"decisions":[...]})`, same `thread_id`, `version="v2"`, decisions ordered to `action_requests`; result `.interrupts` (Py) / `.__interrupt__` (JS). Requires checkpointer.
13. **Import surface moved:** middleware/hooks/`AgentMiddleware`/`AgentState` from `langchain.agents.middleware`; messages from `langchain.messages` (not `langchain_core.messages`); `tool`/`ToolRuntime` from `langchain.tools`; `Runtime` from `langgraph.runtime`; deepagents split (`deepagents.middleware`, `deepagents.backends`, `deepagents.middleware.subagents`).
14. **`ProviderToolSearchMiddleware` + `@tool(extras={"defer_loading":True})`** — new, provider-gated.
15. **Handoffs need `Command(goto=..., graph=Command.PARENT)` with paired AIMessage+ToolMessage** or the receiving agent sees malformed history.
16. **Naming inconsistencies:** `LLMToolEmulator` (no suffix, Py) vs JS `toolEmulatorMiddleware`; Python `PascalCaseMiddleware` classes vs JS `camelCaseMiddleware` factories; JS `ToolRetryMiddleware.onFailure` `"continue"`/`"error"` vs Py `"return_message"`/`"raise"`.
17. **Skills = Agent Skills spec** (`SKILL.md`, agentskills.io); progressive disclosure; both Deep Agents (built-in `SkillsMiddleware`) and LangChain (`load_skill` pattern) versions exist.
18. **`RubricMiddleware`** (LLM-as-judge iterate-until-satisfied) and **harness profiles** (`provider:model`-keyed config bundles) are novel Deep Agents beta features.
19. **All model IDs are future/fictional** (`gpt-5.5`, `claude-opus-4-8`, `gemini-3.5-flash`, `GLM-5.2`) — don't "correct" them.
20. **Dynamic subagents:** the literal word "workflow" in a prompt makes a code-interpreter deep agent fan out subagents from code.

---

## Structure & compressed-volume assessment

**Does the material branch cleanly?** Yes, along **two strong axes**:

- **Per-framework:** `deepagents` vs `langchain` (create_agent + middleware) vs `langgraph`. On a given task a model opens exactly one: "build a batteries-included agent" → deepagents; "customize the agent loop / add a middleware" → langchain; "hand-roll a graph / persistence / interrupts" → langgraph. Deep Agents depends on the other two but is used as a black box.
- **Per-language:** python vs js. Every page duplicates `:::python`/`:::js`, JS uses camelCase factories + different version numbers + a few missing features (provider profiles, plugin registration). A skill can pick one language per branch or gate by language.

**Recommendation:** a **split skill with `references/` per framework** (deepagents.md, langchain-middleware.md, langgraph.md), plus a short shared **"idioms & import map"** file (create_agent, context vs configurable, ToolRuntime, model-ID warning, package layout) that every branch links. Deep Agents is the largest and highest-value branch; give it the most room and its own subtopic files if needed (backends, subagents, skills/memory, profiles, HITL/permissions). Do NOT write one monolithic file — the per-framework branching is clean and a monolith would force the model to read three frameworks for a one-framework task.

**Rough compressed volume (NOVEL+CHANGED + gotchas only, one language, no repeated examples):**

| Area | Raw | Distilled |
|---|---|---|
| Deep Agents | ~900KB / 50 files | **~10–16 pages ≈ 7–11k tokens** (largest; most novel) |
| LangChain middleware | ~230KB (3 files) | ~6–10 pages ≈ 3.5–5.5k tokens |
| LangChain multi-agent + structured output + runtime + memory | ~2.4MB total area | ~5–8 pages ≈ 4–6.5k tokens |
| LangGraph (CHANGED-only) | ~1.1MB | ~6–8 pages ≈ 4–6k tokens (must-know deltas only ≈ 2.5k) |
| Shared idioms/import map | — | ~1–2 pages ≈ 1k tokens |

**Total estimate: ~18–30k tokens** of distilled skill material (dominated by Deep Agents), a ~15–20× compression off the raw MDX, because almost all prose is duplicated per-language and per-example.
