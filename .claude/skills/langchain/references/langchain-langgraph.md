# LangChain and LangGraph Python deltas

Verified against the official LangChain 1.x and LangGraph 1.x Python documentation snapshot from April 2026. This reference contains only ten measured misses. `ToolRuntime`, agent structured output, `PIIMiddleware`, `ContextEditingMiddleware`, `LLMToolSelectorMiddleware`, runtime context, the functional API, `durability=`, and Postgres persistence are intentionally absent because the model already handled them correctly in blind probes.

# LangChain

## 1. Dynamic prompt rewrites use `dynamic_prompt` or `system_message`

For a state-dependent system prompt and no other interception logic, use the dedicated `@dynamic_prompt` convenience middleware:

```python
from langchain.agents import create_agent
from langchain.agents.middleware import ModelRequest, dynamic_prompt

@dynamic_prompt
def state_aware_prompt(request: ModelRequest) -> str:
    message_count = len(request.state.get("messages", []))
    return f"You are a concise assistant. This conversation has {message_count} messages."

agent = create_agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[search],
    middleware=[state_aware_prompt],
)
```

When a full `wrap_model_call` hook is required, `ModelRequest.system_message` is the current message object and the immutable override field is `system_message`, not the deprecated compatibility field `system_prompt`:

```python
from collections.abc import Callable

from langchain.agents.middleware import ModelRequest, ModelResponse, wrap_model_call
from langchain.messages import SystemMessage

@wrap_model_call
def rewrite_prompt(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse],
) -> ModelResponse:
    prompt = f"You are a concise assistant. State keys: {sorted(request.state)}"
    return handler(request.override(system_message=SystemMessage(content=prompt)))
```

To augment rather than replace the prompt, preserve `request.system_message.content_blocks` when constructing the new `SystemMessage`. `create_agent(system_prompt=...)` remains the current constructor parameter; the deprecation applies specifically to `ModelRequest.override(system_prompt=...)` inside middleware.

Sources: `langchain/middleware/custom.mdx`, `langchain/context-engineering.mdx`, and `langchain/agents.mdx`.

## 2. SummarizationMiddleware uses trigger and keep

The middleware and its attachment mechanism are not the gap; its renamed parameters are. Replace deprecated `max_tokens_before_summary`, `messages_to_keep`, and `summary_prefix` with `trigger`, `keep`, and `summary_prompt`.

```python
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware

agent = create_agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[search],
    middleware=[
        SummarizationMiddleware(
            model="openai:gpt-5.4-mini",
            trigger=("tokens", 4000),
            keep=("messages", 20),
        ),
    ],
)
```

`trigger` accepts one `("tokens" | "messages" | "fraction", value)` tuple, a dictionary such as `{"tokens": 4000, "messages": 10}` whose conditions are ANDed, or a list of tuples/dictionaries whose entries are ORed. `keep` accepts one context-size tuple and defaults to `("messages", 20)`. Optional controls include `token_counter`, `summary_prompt`, and `trim_tokens_to_summarize`, whose default is 4,000 tokens.

Source: `langchain/middleware/built-in.mdx`.

## 3. Multi-agent coordination is agent-as-tool

`langgraph-supervisor` and `create_supervisor(...).compile()` are no longer actively maintained. The current subagent pattern wraps already-compiled `create_agent` instances in ordinary tools and gives those tools to a coordinator.

```python
from langchain.agents import create_agent
from langchain.tools import tool

researcher = create_agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[search],
    system_prompt="Research the question and return evidence.",
)

@tool("research", description="Delegate a research question to the research specialist.")
def call_research(query: str) -> str:
    result = researcher.invoke({
        "messages": [{"role": "user", "content": query}],
    })
    return result["messages"][-1].content

coordinator = create_agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[call_research, call_writer],
    system_prompt="Coordinate specialists and synthesize their results.",
)
```

For a large registry, expose one `task(agent_name, description)` tool that validates the name, invokes the selected agent, and returns its final result. Routing comes from the wrapper tool's name and description, not a `name=` handoff parameter. Do not call `.compile()` on `create_agent` output.

Sources: `langchain/multi-agent/subagents.mdx`, `langchain/multi-agent/handoffs.mdx`, and `langchain/multi-agent/index.mdx`.

## 4. Model fallback is middleware, not a runnable wrapper

For an agent, use `ModelFallbackMiddleware` rather than `primary.with_fallbacks(...)` and do not regress to `create_react_agent`.

```python
from langchain.agents import create_agent
from langchain.agents.middleware import ModelFallbackMiddleware

agent = create_agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[],
    middleware=[
        ModelFallbackMiddleware(
            "openai:gpt-5.5",
            "openai:gpt-5.4-mini",
        ),
    ],
)
```

The signature is `ModelFallbackMiddleware(first_model, *additional_models)`. Each fallback is a `provider:model` string or `BaseChatModel`, tried in order after the primary model call fails. There is no `exceptions_to_handle` argument; that belonged to the older runnable fallback mechanism.

Sources: `langchain/middleware/built-in.mdx` and `langchain/agents.mdx`.

## 5. Tool-call limits do not mirror model-call limits

`ModelCallLimitMiddleware` defaults to `exit_behavior="end"`, but `ToolCallLimitMiddleware` defaults to `"continue"`. Inferring one from the other produces broken global-limit behavior.

```python
from langchain.agents import create_agent
from langchain.agents.middleware import ModelCallLimitMiddleware, ToolCallLimitMiddleware
from langgraph.checkpoint.memory import InMemorySaver

agent = create_agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[search],
    checkpointer=InMemorySaver(),
    middleware=[
        ModelCallLimitMiddleware(
            thread_limit=10,
            run_limit=5,
            exit_behavior="end",
        ),
        ToolCallLimitMiddleware(
            tool_name="search",
            run_limit=3,
            exit_behavior="continue",
        ),
    ],
)
```

`ToolCallLimitMiddleware` requires at least one of `thread_limit` or `run_limit`. Its behaviors are `continue` (block exceeded calls with tool errors and let the model proceed), `error` (raise `ToolCallLimitExceededError`), and `end` (finish with a tool and AI message). `end` is valid only for a single-tool limiter; a global limiter with other pending calls raises `NotImplementedError`. Any `thread_limit` needs a checkpointer to persist counts across runs.

Source: `langchain/middleware/built-in.mdx`.

## 6. Provider-side tool search has a middleware

Do not hand-construct provider beta headers, guessed server-tool dictionaries, or `tool.metadata` flags. Use the provider-abstracting middleware and construction-time extras.

```python
from langchain.agents import create_agent
from langchain.agents.middleware import ProviderToolSearchMiddleware
from langchain.tools import tool

@tool(extras={"defer_loading": True})
def lookup_order(order_id: str) -> str:
    """Look up a customer order by ID."""
    ...

agent = create_agent(
    model="anthropic:claude-opus-4-8",
    tools=[get_weather, lookup_order],
    middleware=[
        ProviderToolSearchMiddleware(searchable_tools=["lookup_order"]),
    ],
)
```

`searchable_tools` accepts tool names or instances. Tools marked with `extras={"defer_loading": True}` are deferred even when not listed; if only pre-marked tools should defer, omit `searchable_tools`. The feature requires server-side tool search: Anthropic Claude Sonnet 4+, Opus 4+, or Haiku 4.5+, or OpenAI gpt-5.5+; unsupported providers raise `ValueError`.

Source: `langchain/middleware/built-in.mdx`.

# LangGraph

## 7. Event streaming v3 is the recommended typed surface

The measured wrong prior used `graph.stream(..., stream_mode=[...])`, consumed legacy `(mode, chunk)` tuples, and claimed event streaming was older. For in-process application streaming on LangGraph 1.2+, prefer `stream_events(..., version="v3")` or `astream_events` and consume typed projections.

```python
from langgraph.prebuilt import ToolCallTransformer

stream = graph.stream_events(
    inputs,
    version="v3",
    transformers=[ToolCallTransformer],
)

for name, item in stream.interleave("messages", "tool_calls", "values"):
    if name == "messages":
        for token in item.text:
            print(token, end="", flush=True)
    elif name == "tool_calls":
        print(item.tool_name, item.input)

final = stream.output
```

Core projections include `stream.messages`, `stream.values`, `stream.output`, `stream.subgraphs`, `stream.interrupts`, `stream.interrupted`, and `stream.extensions`. Each `stream.messages` item exposes token text through `message.text`, tool-call argument chunks through `message.tool_calls`, reasoning through `message.reasoning`, final usage metadata through `message.output.usage_metadata`, and provenance through `message.node`. Register `ToolCallTransformer` on a plain `StateGraph` to expose `stream.tool_calls`; LangChain agents expose the product projection directly. In async code, consume projections concurrently with `asyncio.gather`.

The lower-level stream-mode API still exists, but its current uniform form is `graph.stream(..., stream_mode=[...], version="v2")` yielding `StreamPart` dictionaries with `type`, `ns`, and `data`, not v1 `(mode, chunk)` tuples.

Sources: `langgraph/event-streaming.mdx`, `langgraph/streaming.mdx`, and `langchain/event-streaming.mdx`.

## 8. Declarative error handling is separate from retry

`RetryPolicy` decides whether to retry an attempt. `error_handler` decides how the graph compensates or reroutes only after retries are exhausted. Treating retry as the whole error-handling answer loses saga/compensation semantics.

This declarative `error_handler`, `NodeError`, and `set_node_defaults` surface requires `langgraph>=1.2`; it is not available across all LangGraph 1.x minors.

```python
from langgraph.errors import NodeError
from langgraph.graph import StateGraph
from langgraph.types import Command, RetryPolicy

def handle_charge_failure(state: State, error: NodeError) -> Command:
    return Command(
        update={"failed_node": error.node, "failure": str(error.error)},
        goto="compensate",
    )

builder = StateGraph(State)
builder.add_node(
    "charge",
    charge,
    retry_policy=RetryPolicy(max_attempts=3),
    error_handler=handle_charge_failure,
)
```

`NodeError` is a frozen dataclass with `node: str` and `error: BaseException`, injected by its annotation. The parameter is optional when a handler only needs state or runtime. `interrupt()` bypasses both retry and error handlers because it is control flow, not a failure.

Use `builder.set_node_defaults(retry_policy=..., error_handler=..., timeout=..., cache_policy=...)` for graph-wide policy. Per-node values win. Error-handler nodes inherit retry and timeout defaults but never inherit the error-handler or cache defaults, preventing recursion and unsafe result reuse.

Sources: `langgraph/thinking-in-langgraph.mdx` and `langgraph/fault-tolerance.mdx`.

## 9. Interrupt refinements: event driver, saver name, parallel resume

The core `interrupt(payload)` and `Command(resume=...)` pattern remains valid. The current Python in-memory checkpointer is `InMemorySaver`; `MemorySaver` is the JavaScript name and only a legacy Python alias.

```python
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command, interrupt

checkpointer = InMemorySaver()
graph = builder.compile(checkpointer=checkpointer)
config = {"configurable": {"thread_id": "approval-1"}}

stream = graph.stream_events(inputs, config=config, version="v3")
if stream.interrupted:
    for pending in stream.interrupts:
        print(pending.id, pending.value)
    stream = graph.stream_events(
        Command(resume={pending.id: human_value for pending in stream.interrupts}),
        config=config,
        version="v3",
    )
final = stream.output
```

The ID-keyed resume map is required when parallel branches pause simultaneously; a single bare resume value cannot reliably pair answers with interrupts. `graph.invoke(...)["__interrupt__"]` still works when typed streaming is unnecessary. `raise NodeInterrupt` is removed, and static `interrupt_before` or `interrupt_after` remains a debugging breakpoint rather than application HITL.

Source: `langgraph/interrupts.mdx`.

## 10. DeltaChannel preserves reducers without checkpoint bloat

Moving a growing reducer value into the long-term store changes semantics and forces manual reconstruction. LangGraph 1.2+ beta `DeltaChannel` keeps the value in checkpointed state while storing only per-step writes, making each checkpoint blob O(1) for that channel rather than reserializing the full O(N) accumulation.

```python
from typing import Annotated, Sequence
from typing_extensions import TypedDict
from langgraph.channels import DeltaChannel

def append_batches(state: list[str], writes: Sequence[list[str]]) -> list[str]:
    result = list(state)
    for write in writes:
        result.extend(write)
    return result

class State(TypedDict):
    events: Annotated[
        list[str],
        DeltaChannel(append_batches, snapshot_frequency=50),
    ]
```

The reducer is bulk: it receives the current state and every write from one step as a sequence, not pairwise like `operator.add`. It must be associative and pure because it runs during reconstruction rather than write time. Never generate IDs, read the clock, perform side effects, or rely on mutating incoming writes inside it; attach stable identity upstream.

Without snapshots, reconstruction replays the full write history. `snapshot_frequency=K` bounds replay depth to K steps: lower values improve read latency at the cost of larger checkpoints, while the default `None` stores no full snapshots. Once a thread uses `DeltaChannel`, older LangGraph versions cannot read its new checkpoint format; migrate or discard affected threads before downgrading.

Sources: `langgraph/pregel.mdx` and `langgraph/checkpointers.mdx`.
