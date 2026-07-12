# 04 — references/langchain-langgraph.md content specification

This is the spec for the thin reference file: 6 LangChain deltas and 4 LangGraph deltas. It is short by design — the probes showed the model already writes most modern LangChain-core and LangGraph-runtime code correctly, so this file carries only the specific misses. Same authoring rules as `03`: lead with the wrong prior, teach only the delta, name the reason, cite and verify the source.

Open the file with a one-line scope note plus a version stamp ("Verified against LangChain 1.x / LangGraph 1.x … April 2026"), then a LangChain section and a LangGraph section. Put a one-line reminder at the top that the excluded topics (`ToolRuntime`, structured output, `PIIMiddleware`, `ContextEditingMiddleware`, `LLMToolSelectorMiddleware`, runtime context, functional API, `durability=`, Postgres persistence) are deliberately absent because the model already handles them.

---

# LangChain deltas

## L1. Dynamic system-prompt rewriting (probe A2)

**Wrong prior.** The model knows the current middleware lifecycle but emits `request.override(system_prompt=...)` as the preferred new-code path. That compatibility argument is deprecated even though `create_agent(system_prompt=...)` remains current.

**Current API.** For a prompt-only rewrite, prefer the focused `@dynamic_prompt` middleware:

```python
from langchain.agents import create_agent
from langchain.agents.middleware import ModelRequest, dynamic_prompt

@dynamic_prompt
def role_prompt(request: ModelRequest) -> str:
    role = request.state.get("role", "generalist")
    return f"You are the {role} specialist."

agent = create_agent(model="anthropic:claude-sonnet-4-6", tools=[], middleware=[role_prompt])
```

When full `wrap_model_call` control is genuinely needed, use the immutable replacement path `request.override(system_message=SystemMessage(...))`, and preserve `request.system_message.content_blocks` when augmenting rather than replacing the existing prompt. Do not emit `ModelRequest.override(system_prompt=...)` in new middleware code. This deprecation applies to `ModelRequest.override`; the top-level `create_agent(system_prompt=...)` constructor argument is still the current API.

**Source.** `langchain/middleware/custom.mdx`, `langchain/context-engineering.mdx`, `langchain/agents.mdx`.

---

## L2. SummarizationMiddleware parameters (probe A4)

**Wrong prior.** The model wires `SummarizationMiddleware` correctly (right import, right `middleware=[...]` attachment) but configures it with the deprecated `max_tokens_before_summary=` and `messages_to_keep=`.

**Current API.**

```python
from langchain.agents.middleware import SummarizationMiddleware
middleware = [SummarizationMiddleware(model="anthropic:claude-sonnet-4-6",
                                      trigger=("tokens", 4000), keep=("messages", 20))]
```

`trigger` takes a `ContextSize` tuple (`"tokens"`/`"messages"`/`"fraction"`, value), a `TriggerClause` dict like `{"tokens": 4000, "messages": 10}` (AND logic), or a list of those (OR logic). `keep` takes one `ContextSize` tuple and defaults to `("messages", 20)`. The deprecated parameters a model will emit are `max_tokens_before_summary` → `trigger`, `messages_to_keep` → `keep`, and `summary_prefix` → `summary_prompt`. Optional: `token_counter`, `summary_prompt`, `trim_tokens_to_summarize` (default 4000).

**Do not re-teach** the middleware mechanism or `create_agent` wiring — only the parameter rename is the delta.

**Source.** `langchain/middleware/built-in.mdx`.

---

## L3. Multi-agent: the supervisor pattern is deprecated (probe A7)

**Wrong prior.** At high confidence the model builds the system with `create_supervisor(agents=[...]).compile()` from `langgraph-supervisor`, over sub-agents made with `create_react_agent`, and calls this "the current recommended multi-agent pattern."

**Current API.** `create_supervisor` / `langgraph-supervisor` is no longer maintained (a migration guide exists). The current pattern is agent-as-tool: build each specialist with `create_agent`, wrap it in a `@tool`, and give a coordinator `create_agent` those tools.

```python
from langchain.agents import create_agent
from langchain.tools import tool

research = create_agent(model="anthropic:claude-sonnet-4-6", tools=[...], system_prompt="You research.")

@tool("research", description="Delegate a research question to the research specialist.")
def call_research(query: str) -> str:
    return research.invoke({"messages": [{"role": "user", "content": query}]})["messages"][-1].content

coordinator = create_agent(model="anthropic:claude-sonnet-4-6", tools=[call_research, call_writer],
                           system_prompt="You coordinate specialists.")
```

Alternatively, a single-dispatch pattern: one `@tool def task(agent_name: str, description: str)` that looks the agent up in a registry and invokes it. `create_agent` returns an already-compiled graph, so there is no `.compile()` and no uncompiled `StateGraph` step; the "supervisor" is just a coordinator `create_agent` whose tools are the sub-agents. Routing is done by the wrapping tool's name/description (or the `task` dispatch tool), not a `name=` handoff parameter.

**Why it matters.** The model is `outdated_confident` here — it will confidently pull in an unmaintained package. Naming the deprecation plus the replacement pattern is the whole point.

**Source.** `langchain/multi-agent/subagents.mdx`, `handoffs.mdx`, `index.mdx`.

---

## L4. ModelFallbackMiddleware (probe R3)

**Wrong prior.** The model wraps the model runnable in `primary.with_fallbacks([secondary])` and passes it to `create_react_agent`, presenting `.with_fallbacks()` as the current built-in mechanism.

**Current API.** Agent model fallback is a built-in middleware, not a runnable wrapper:

```python
from langchain.agents import create_agent
from langchain.agents.middleware import ModelFallbackMiddleware

agent = create_agent(model="anthropic:claude-sonnet-4-6", tools=[],
                     middleware=[ModelFallbackMiddleware("openai:gpt-5.5", "openai:gpt-5.4-mini")])
```

`ModelFallbackMiddleware(first_model, *additional_models)` takes each fallback as a `provider:model` string or a `BaseChatModel`, tried in order when the primary call fails. There is no `exceptions_to_handle` parameter (that belonged to the old `.with_fallbacks()`). The agent constructor is `create_agent`, not `create_react_agent`.

**Source.** `langchain/middleware/built-in.mdx`, `agents.mdx`.

---

## L5. ToolCallLimitMiddleware semantics (probe R4)

**Wrong prior.** The model uses `ModelCallLimitMiddleware` correctly but assumes `ToolCallLimitMiddleware.exit_behavior` mirrors it (`"end"`/`"error"`), applying `"end"` to a global limiter.

**Current API.**

```python
from langchain.agents.middleware import ModelCallLimitMiddleware, ToolCallLimitMiddleware
middleware = [
    ModelCallLimitMiddleware(thread_limit=10, run_limit=5, exit_behavior="end"),   # default "end"
    ToolCallLimitMiddleware(tool_name="search", run_limit=3, exit_behavior="continue"),
]
```

`ToolCallLimitMiddleware(tool_name=None, thread_limit=..., run_limit=..., exit_behavior=...)` requires at least one of `thread_limit`/`run_limit`. Its `exit_behavior` has three values and defaults to `"continue"` (block exceeded tool calls with error messages and let the model keep going) — not `"end"`. `"error"` raises `ToolCallLimitExceededError`. `"end"` only works when limiting a single tool (`tool_name` set); on a global/multi-tool limiter it raises `NotImplementedError` if other tools have pending calls. `thread_limit` on either middleware requires a checkpointer to persist across runs. `ModelCallLimitMiddleware.exit_behavior` does default to `"end"` — that part the model gets right.

**Source.** `langchain/middleware/built-in.mdx`.

---

## L6. ProviderToolSearchMiddleware — deferred tool loading (probe R6)

**Wrong prior.** The model hand-rolls Anthropic's provider-side tool search at the raw-API level — `ChatAnthropic(betas=[...])` plus a guessed server-tool dict in `tools=` and a `tool.metadata["defer_loading"]` flag.

**Current API.**

```python
from langchain.agents import create_agent
from langchain.agents.middleware import ProviderToolSearchMiddleware
from langchain.tools import tool

@tool(extras={"defer_loading": True})
def lookup_order(order_id: str) -> str:
    ...

agent = create_agent(model="anthropic:claude-opus-4-8", tools=[get_weather, lookup_order],
                     middleware=[ProviderToolSearchMiddleware(searchable_tools=["lookup_order"])])
```

Deferral is done via `ProviderToolSearchMiddleware` (which internally wires the provider's server-side tool search — no manual beta header or server-tool dict), passed to `create_agent(middleware=[...])`. Which tools defer is controlled by `ProviderToolSearchMiddleware(searchable_tools=[...])` (tool names or instances), or per-tool at construction with `@tool(extras={"defer_loading": True})`; with pre-marked tools, `searchable_tools` can be omitted. Provider-gated: Anthropic Claude Sonnet 4+/Opus 4+/Haiku 4.5+ or OpenAI gpt-5.5+, else it raises `ValueError`.

**Source.** `langchain/middleware/built-in.mdx`.

---

# LangGraph deltas

## G1. Event streaming — the recommendation flipped (probe B5)

**Wrong prior.** The model streams via `graph.stream(inputs, stream_mode=["updates", "messages"])` consuming v1-format `(mode, chunk)` tuples, and explicitly asserts that `stream_mode="messages"` is now preferred while `astream_events(version="v2")` is the "older" API — which is backwards.

**Current API.** Event streaming is the recommended in-process streaming API (LangGraph v1.2+): `graph.stream_events(input, version="v3")` (sync) / `graph.astream_events(input, version="v3")` (async); `create_agent(...)` returns a compiled graph that exposes it. Consume typed projections as attributes on the returned run-stream object: `stream.messages` (iterate `message.text` for token deltas; `message.tool_calls` for tool-call arg chunks; `message.reasoning`; `message.output.usage_metadata`; `message.node`), `stream.values`, `stream.output`, `stream.subgraphs`, `stream.interrupts`/`stream.interrupted`, `stream.extensions`. For a typed tool-call projection, register `ToolCallTransformer` (`from langgraph.prebuilt import ToolCallTransformer`, via `transformers=[...]`) to expose `stream.tool_calls` (`tool_call.tool_name`, `tool_call.input`). Multiplex with `stream.interleave("values", "messages", "subgraphs")` (sync) or `asyncio.gather` over projection iterators (async); resume after an interrupt by calling `stream_events(Command(resume=...), version="v3")` again. If you drop to the lower-level stream-mode API, its current output format is `graph.stream(..., stream_mode=[...], version="v2")` yielding uniform `StreamPart` dicts (`{type, ns, data}`), not v1 `(mode, chunk)` tuples.

**Why it matters.** The model has the recommendation inverted, so it writes the non-recommended path and mislabels the current one as legacy. The correction is the version (`v3`), the projection-attribute model, and that token streaming iterates `message.text`.

**Source.** `langgraph/event-streaming.mdx`, `streaming.mdx`, `langchain/event-streaming.mdx`.

---

## G2. Declarative error handling (probe B3)

**Wrong prior.** The model uses `CachePolicy`/`InMemoryCache` (correct) and `RetryPolicy` (correct) but treats `RetryPolicy` as the whole "error handling" answer, omitting the declarative `error_handler=` API the task asked for.

**Current API (teach only the error handler; caching and retry the model already knows).**

```python
from langgraph.errors import NodeError
from langgraph.types import Command

def handle(state: State, error: NodeError) -> Command:
    return Command(update={"failed_node": error.node}, goto="compensate")

builder.add_node("charge", charge_fn, retry_policy=RetryPolicy(max_attempts=3), error_handler=handle)
builder.set_node_defaults(error_handler=handle)   # graph-wide default
```

`add_node(..., error_handler=fn)` where `fn(state, error: NodeError) -> Command` runs compensation/saga routing and requires `langgraph>=1.2`; `NodeError` and `set_node_defaults` belong to the same version-gated surface. It fires only after the retry policy is exhausted (or immediately if there is no retry policy) — retry and error handling are decoupled and configured independently. `NodeError` is a frozen dataclass with fields `node: str` and `error: BaseException`; the `error: NodeError` parameter is injected by type annotation (the same mechanism as `runtime: Runtime`) and is opt-in — a handler can also be `(state)` or `(state, runtime)`. `interrupt()` is not routed to the handler. `set_node_defaults(retry_policy=, error_handler=, timeout=, cache_policy=)` applies these graph-wide; error-handler nodes are excluded from the `error_handler` and `cache_policy` defaults. (JS: `errorHandler` on `StateGraph.addNode` requires `@langchain/langgraph>=1.4.0`.)

**Source.** `langgraph/thinking-in-langgraph.mdx`, `fault-tolerance.mdx`.

---

## G3. Interrupts — thin deltas (probe B2)

**Wrong prior.** The core pattern is correct — `interrupt(payload)` in a node, `Command(resume=...)` on the same `thread_id`, checkpointer + `{"configurable": {"thread_id": ...}}`. Only the surrounding details drift.

**Current API (deltas only — do not re-teach the core pattern the model gets right).** The Python checkpointer class is now `InMemorySaver` (`from langgraph.checkpoint.memory import InMemorySaver`); `MemorySaver` works only as a legacy alias. The recommended driver is `graph.stream_events(..., version="v3")`, checking `stream.interrupted` and reading payloads from `stream.interrupts`; `graph.invoke(...)` with `result["__interrupt__"]` still works but is the non-recommended fallback. Multiple simultaneous (parallel-branch) interrupts resume via an id-keyed map `Command(resume={interrupt_id: value})`, not a bare value. Worth reinforcing because it is correct and stabilizing: `raise NodeInterrupt` is removed and static `interrupt_before/after` is debugging-only — `interrupt()` + `Command(resume=...)` is the sole dynamic HITL pattern.

**Source.** `langgraph/interrupts.mdx`.

---

## G4. DeltaChannel — bounded checkpoint growth (probe R8)

**Wrong prior.** The model correctly diagnoses that snapshotting a large growing list every step blows up checkpoints, but "fixes" it by offloading the list out of checkpointed state into the long-term Store with a cursor — abandoning the reducer channel, which violates the task's "preserve reducer semantics" requirement.

**Current API.** The purpose-built feature is `DeltaChannel` (langgraph ≥1.2, beta):

```python
from langgraph.channels import DeltaChannel

class State(TypedDict):
    events: Annotated[list, DeltaChannel(bulk_reducer, snapshot_frequency=50)]
```

It keeps the growing list as a reducer channel in checkpointed state but serializes only per-step deltas, so each checkpoint blob is O(1) instead of O(N). The reducer is a **bulk** reducer with signature `(state, writes: Sequence[...]) -> ...` — it receives all writes for the step at once, not pairwise like `operator.add`/`add_messages` — and it must be associative and pure because it runs at reconstruction time, not at write time (no `uuid`/`datetime`/side effects; assign stable IDs upstream). `snapshot_frequency=K` writes a full snapshot every K steps to bound read-replay latency (default `None`). Downgrading LangGraph after a thread uses `DeltaChannel` leaves those checkpoints unreadable (new on-disk delta format).

**Why it matters.** The store-offload approach the model reaches for does not satisfy the reducer-preservation constraint at all — it removes the reducer channel and forces manual key-per-item writes plus reconstruction. `DeltaChannel` is the one API that keeps the reducer and shrinks the blob. (Separately, if the model reaches for `get_store()` from `langgraph.config` to access a store in a node, that is outdated — the current idiom is `runtime.store` via a `runtime: Runtime[Context]` node parameter.)

**Source.** `langgraph/pregel.mdx`, `checkpointers.mdx`.
