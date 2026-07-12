# Deep Agents Python deltas

Verified against the official Deep Agents Python documentation snapshot from April 2026. This file corrects measured gaps; it is not a full SDK tutorial. Prefer the installed version's API reference when working far beyond this stamp, especially for features marked beta or preview.

## 1. Constructor and built-in surface

The common wrong prior is a plausible-looking `create_deep_agent(tools=..., instructions=...)` call with an incomplete built-in tool list. The current constructor uses `system_prompt=`, takes an explicit model, and expects `tools=` to contain only the caller's domain tools because the harness injects its own tools.

```python
from deepagents import create_deep_agent

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    system_prompt="You are a research assistant.",
    tools=[search],
)
result = agent.invoke({"messages": [{"role": "user", "content": "Research the topic."}]})
final = result["messages"][-1].content_blocks
```

The current configuration surface includes `model`, `system_prompt`, `tools`, `memory`, `skills`, `backend`, `permissions`, `subagents`, `middleware`, `interrupt_on`, `response_format`, `state_schema`, `context_schema`, `checkpointer`, and `store`. Omitting `model` still reaches a deprecated `claude-sonnet-4-6` fallback; do not rely on it, and do not call `.compile()` on the returned graph.

Every deep agent gets planning through `write_todos`; virtual-filesystem tools `ls`, `read_file`, `write_file`, `edit_file`, `glob`, and `grep`; `execute` when the backend implements the sandbox protocol; and `task` when synchronous subagents are enabled. `delete` requires `deepagents>=0.7.a1`, recursive directory deletion requires `>=0.7.a2`, and backends without deletion support hide the tool. The harness also provides skills, memory, automatic summarization and large-result offloading, Anthropic/Bedrock prompt caching, HITL, and filesystem permissions when configured.

State-backed input files are structured records, not raw strings:

```python
from deepagents.backends.utils import create_file_data

result = agent.invoke({
    "messages": [{"role": "user", "content": "Read notes.txt."}],
    "files": {"notes.txt": create_file_data("source material")},
})
```

Sources: `deepagents/overview.mdx`, `deepagents/quickstart.mdx`, and `deepagents/customization.mdx`.

## 2. Backends and filesystem security

`FilesystemBackend(root_dir=...)` does not become a sandbox merely because a root is present. Its default is `virtual_mode=False`, which provides no path protection; `virtual_mode=True` is what blocks `..`, `~`, and absolute paths outside the root. The root must be absolute.

```python
from deepagents.backends import CompositeBackend, FilesystemBackend, StateBackend

backend = CompositeBackend(
    default=StateBackend(),
    routes={
        "/workspace/": FilesystemBackend(
            root_dir="/absolute/path/to/project",
            virtual_mode=True,
        ),
    },
)
agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    system_prompt="Work only inside /workspace/.",
    backend=backend,
)
```

The `CompositeBackend` boundary matters because Deep Agents writes `/large_tool_results/` and `/conversation_history/` to the default backend. Keeping `StateBackend()` as the default prevents internal artifacts from mixing with project files on real disk. Longer route prefixes win.

`virtual_mode=True` is only path normalization, not process isolation. It provides no security once a shell-capable backend can execute commands. `LocalShellBackend` runs `subprocess.run(..., shell=True)` on the host and is a trusted-development tool, not a production sandbox.

Pass constructed backend instances. The old `backend=lambda rt: StateBackend(rt)` factory form is deprecated since Deep Agents 0.5.0 because backends now resolve runtime state internally.

Source: `deepagents/backends.mdx`.

## 3. Long-term memory and namespace isolation

`StateBackend` persists through turns in one checkpointed thread but is not cross-thread memory. Route a durable path to `StoreBackend` for cross-thread state, and always choose a namespace that matches the data boundary.

```python
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()
backend = CompositeBackend(
    default=StateBackend(),
    routes={
        "/memories/": StoreBackend(
            namespace=lambda rt: (rt.server_info.user.identity,),
        ),
    },
)
agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    system_prompt="Keep durable user preferences under /memories/.",
    backend=backend,
    store=store,
)
```

A missing namespace is a silent multi-user isolation bug: the legacy default scopes by assistant, so users of the same assistant share storage. Namespace factories receive `Runtime` and can key on `rt.server_info.user.identity`, `rt.server_info.assistant_id`, `rt.context`, or `rt.execution_info.thread_id`. Wildcards are rejected in namespace components.

Use `InMemoryStore` only for local development. Production can use `PostgresStore` with its setup step. On a LangSmith Deployment, omit `store=` because the platform provisions the store and checkpointer.

Sources: `deepagents/memory.mdx`, `deepagents/backends.mdx`, and `deepagents/context-engineering.mdx`.

## 4. Context compression is already automatic

Do not hand-add `SummarizationMiddleware` plus `ContextEditingMiddleware` merely to obtain the standard Deep Agents behavior. Every `create_deep_agent` call already includes summarization and filesystem offloading.

- File write/edit tool-call inputs above 20,000 tokens are truncated once they are old and active context crosses roughly 85% of the model window; the persisted file remains available by path.
- Tool results above 20,000 tokens are stored in the backend and replaced with a path plus a preview of the first ten lines.
- Summarization normally triggers at 85% of the model profile's `max_input_tokens`, keeps roughly 10% as recent context, and preserves a text rendering of the original conversation in the filesystem.
- Without a model profile, the fallback is a 170,000-token trigger with six recent messages kept.
- A standard `ContextOverflowError` triggers immediate summarize-and-retry behavior.

For deliberate compaction between tasks, add the separate on-demand tool instead of duplicating the default middleware:

```python
from deepagents.backends import StateBackend
from deepagents.middleware.summarization import create_summarization_tool_middleware

model = "anthropic:claude-sonnet-4-6"
backend = StateBackend()
agent = create_deep_agent(
    model=model,
    backend=backend,
    middleware=[create_summarization_tool_middleware(model, backend)],
)
```

This adds `compact_conversation`; it does not disable automatic threshold-based summarization.

Source: `deepagents/context-engineering.mdx`.

## 5. Synchronous subagents

Declarative subagents use dictionaries with required `name`, `description`, and `system_prompt`. The nested key is not `prompt`. Tools and model inherit from the main agent unless overridden; `system_prompt` does not inherit. Middleware and specialist skills do not inherit, while permissions inherit unless the subagent supplies a replacement list.

```python
agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    system_prompt="Coordinate specialists.",
    subagents=[
        {
            "name": "researcher",
            "description": "Finds and checks source material.",
            "system_prompt": "Return concise findings with evidence.",
        },
        {
            "name": "writer",
            "description": "Turns verified findings into a clear draft.",
            "system_prompt": "Write from the supplied evidence only.",
        },
    ],
)
```

The harness exposes these through `task` and adds `general-purpose` unless a synchronous subagent already uses that name. A custom compiled graph uses `CompiledSubAgent(name=..., description=..., runnable=graph)` from `deepagents.middleware.subagents`; the field is `runnable`, not `graph`.

Source: `deepagents/subagents.mdx`.

## 6. Async subagents are first-class remote tasks

Do not reconstruct long-running, steerable work from regular `task` calls, `asyncio` cancellation, `aupdate_state`, or HITL resume commands. Async subagents are a preview facility available in Python `deepagents>=0.5.0`, backed by independent threads on an Agent Protocol server.

Each `AsyncSubAgent` spec requires `name`, `description`, and `graph_id`; `graph_id` matches the graph or assistant registered by the server. Omit `url` for recommended in-process ASGI transport when graphs are co-deployed in one `langgraph.json`; set `url` and optional `headers` for HTTP transport to a remote server.

Pass these specs through `subagents=`; `create_deep_agent` detects their type and attaches `AsyncSubAgentMiddleware` automatically. Do not construct that middleware manually.

```python
from deepagents import AsyncSubAgent, create_deep_agent

agent = create_deep_agent(
    model="google_genai:gemini-3.5-flash",
    subagents=[
        AsyncSubAgent(
            name="researcher",
            description="Researches and synthesizes source material.",
            graph_id="researcher",
        ),
        AsyncSubAgent(
            name="coder",
            description="Implements and reviews code.",
            graph_id="coder",
            url="https://coder.example.com",
            headers={"Authorization": "Bearer ..."},
        ),
    ],
)
```

When async subagents are configured, `AsyncSubAgentMiddleware` adds five model-facing tools:

- `start_async_task` launches work and returns a task ID immediately.
- `check_async_task` returns live status and the result when ready.
- `update_async_task` sends new instructions to the running task using the same ID.
- `cancel_async_task` performs server-side cancellation.
- `list_async_tasks` reports all tracked tasks.

Task metadata lives in the dedicated `async_tasks` state channel, so task IDs survive message-history compaction. This is non-blocking task management, not merely several synchronous calls emitted in one model turn.

Source: `deepagents/async-subagents.mdx`.

## 7. Dynamic subagents run from interpreter code

When the number of work units is discovered at runtime, use the beta dynamic-subagents feature rather than asking the model to emit an arbitrary number of parallel `task` tool calls or dropping to LangGraph `Send`.

Install `deepagents[quickjs]` with `langchain-quickjs>=0.2.0` on Python 3.11+, then add `CodeInterpreterMiddleware`. If the agent has subagents, the QuickJS interpreter exposes a `task()` global by default. Interpreter JavaScript can hold the working set in variables, loop or batch over it, and call `task({description, subagentType, responseSchema?})`; the optional schema returns a typed JavaScript object.

The literal word **workflow** is a documented opt-in signal in the interpreter prompt. Ask for a "workflow" when code-driven fan-out is intended; use plain delegation wording for one direct subagent call. Set `CodeInterpreterMiddleware(subagents=False)` to disable the interpreter bridge and require normal `task` tool calls.

Interpreter-dispatched subagents bypass per-dispatch `interrupt_on`; gate the parent `eval` tool if approval is required before orchestration.

Sources: `deepagents/dynamic-subagents.mdx`, `deepagents/interpreters.mdx`, and `deepagents/subagents.mdx`.

## 8. Skills attach through `skills=`, not backend discovery

A filesystem backend stores files but does not make the SDK scan them for skills. Pass each top-level skill source directory explicitly; the middleware scans its child directories for `SKILL.md` files:

```text
/absolute/project/
└── skills/
    └── pdf-fill/
        └── SKILL.md
```

```python
from deepagents.backends import FilesystemBackend

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    system_prompt="Use the available skills when relevant.",
    skills=["skills"],
    backend=FilesystemBackend(root_dir="/absolute/project", virtual_mode=True),
)
```

Paths use forward slashes and are relative to the backend root. Passing an individual skill directory such as `skills=["skills/pdf-fill"]` loads nothing because `skills=` identifies sources, not skills. The frontmatter `name` must match the directory immediately containing `SKILL.md`. Passing `skills=` adds `SkillsMiddleware`, which loads metadata at startup and the full body only on invocation. With the default `StateBackend`, provide skill files through `invoke(files={...})` using `create_file_data()`; raw strings are rejected. Do not reimplement the Agent Skills directory format—the important delta is the explicit source attachment mechanism.

Sources: `deepagents/skills.mdx` and `deepagents/customization.mdx`.

## 9. Human-in-the-loop uses `interrupt_on`

The current surface is `interrupt_on`, not `interrupt_config`, and the decision vocabulary is `approve`, `edit`, `reject`, and `respond`. `respond` is for a human acting as the tool, not for denying a side-effecting action.

```python
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

checkpointer = InMemorySaver()
agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    system_prompt="Send mail only after review.",
    tools=[send_email],
    interrupt_on={
        "send_email": {
            "allowed_decisions": ["approve", "edit", "reject", "respond"],
        },
    },
    checkpointer=checkpointer,
)

config = {"configurable": {"thread_id": "review-1"}}
result = agent.invoke(
    {"messages": [{"role": "user", "content": "Send the update."}]},
    config=config,
    version="v2",
)
if result.interrupts:
    result = agent.invoke(
        Command(resume={"decisions": [{"type": "approve"}]}),
        config=config,
        version="v2",
    )
final = result.value["messages"][-1].content
```

Edit decisions use `{"type": "edit", "edited_action": {"name": ..., "args": {...}}}`; rejection uses `{"type": "reject", "message": ...}`. Resume with the same thread configuration. A checkpointer is mandatory because the paused state must survive between calls.

Source: `deepagents/human-in-the-loop.mdx`.

## 10. Filesystem permissions are ordered rules

Permissions are `FilesystemPermission` objects passed to `create_deep_agent`, not a path-to-level dictionary on the backend.

```python
from deepagents import FilesystemPermission

permissions = [
    FilesystemPermission(
        operations=["read", "write"],
        paths=["/workspace/secrets/**"],
        mode="deny",
    ),
    FilesystemPermission(
        operations=["write"],
        paths=["/workspace/config/**"],
        mode="deny",
    ),
    FilesystemPermission(
        operations=["read", "write"],
        paths=["/workspace/**"],
        mode="allow",
    ),
]
```

Rules are first-match-wins with a permissive default, so specific restrictions must precede broad allows. `read` covers `ls`, `read_file`, `glob`, and `grep`; `write` covers `write_file`, `edit_file`, and `delete`. Read-only means denying `write`; fully blocked means denying both. `mode="interrupt"` requires Deep Agents 0.6.8+ and pauses for HITL review; the overall permission feature requires 0.5.2+.

These rules cover only built-in filesystem tools. They do not constrain custom tools, MCP tools, or sandbox shell execution. Synchronous subagents inherit the parent list unless their spec replaces it.

Source: `deepagents/permissions.mdx`.

## 11. RubricMiddleware owns the judge loop

Do not hand-roll a critique subagent, parse a free-form `PASS`, or put iteration policy in the main prompt. Deep Agents 0.6.5+ provides beta `RubricMiddleware`.

```python
from deepagents.middleware import RubricMiddleware

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    system_prompt="Produce the requested artifact.",
    middleware=[
        RubricMiddleware(
            model="anthropic:claude-sonnet-4-6",
            max_iterations=3,
            tools=[run_test_suite],
        ),
    ],
)
result = agent.invoke({
    "messages": [{"role": "user", "content": "Implement the function."}],
    "rubric": "1. All tests pass\n2. Public behavior remains compatible",
})
```

No `rubric` means the middleware is inert. Each grader pass reports `satisfied`, `needs_revision`, `failed`, or `grader_error`; `needs_revision` automatically injects feedback and loops. If the final pass still needs revision at the cap, its `RubricEvaluation.result` remains `needs_revision` while terminal private state `_rubric_status` becomes `max_iterations_reached`. Observe passes with `on_evaluation` or `rubric_evaluation_start` and `rubric_evaluation_end` on `stream.custom`; code-generation examples use the same `RubricMiddleware`, not a separate middleware class.

Source: `deepagents/rubric.mdx`.

## 12. Harness profiles follow model selection

When tuning the harness per provider or model, use the beta harness-profiles feature rather than hand-rolling a configuration dictionary at every call site. Register a profile once and let `create_deep_agent` resolve it from the model.

```python
from deepagents import HarnessProfile, register_harness_profile

register_harness_profile(
    "anthropic",
    HarnessProfile(system_prompt_suffix="Use precise tool calls and preserve evidence."),
)
register_harness_profile(
    "openai:gpt-5.5",
    HarnessProfile(base_system_prompt="Be concise and explicit about uncertainty."),
)
```

`HarnessProfile` can set `base_system_prompt`, `system_prompt_suffix`, `tool_description_overrides`, `excluded_tools`, `excluded_middleware`, `extra_middleware`, and `general_purpose_subagent`. Provider- and model-level entries merge, and built-in Anthropic and OpenAI profiles already exist. Caller `system_prompt=` stays first, a custom base replaces the SDK base, and the profile suffix stays last.

Python-only `ProviderProfile` plus `register_provider_profile` handles model-construction concerns such as `init_kwargs`, `pre_init`, and `init_kwargs_factory`; it is distinct from harness behavior. `HarnessProfileConfig` is the serializable YAML/JSON form.

Source: `deepagents/profiles.mdx`.

## 13. Interpreters and programmatic tool calling

The current API is beta `CodeInterpreterMiddleware`, not an invented `CodeExecutionMiddleware`, and the runtime is JavaScript/QuickJS rather than Python.

```python
from langchain_quickjs import CodeInterpreterMiddleware

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    system_prompt="Use code to compose large batches of tool calls.",
    tools=[search, fetch, score],
    middleware=[
        CodeInterpreterMiddleware(ptc=[search, fetch, score]),
    ],
)
```

The middleware adds `eval`. QuickJS has no host filesystem, network, shell, package manager, or clock by default. Programmatic tool calling is off until `ptc=` allowlists tool names or `BaseTool` instances; those tools appear under `tools.*`, use camelCase names, and must be awaited. Only the final interpreter result returns to the model, keeping intermediate data out of context.

Important defaults are `max_ptc_calls=256`, `mode="thread"`, `timeout=5.0`, `tool_name="eval"`, `capture_console=True`, `max_result_chars=4000`, and `subagents=True`. PTC calls bypass per-tool `interrupt_on`, so treat the allowlist as a permission boundary.

Source: `deepagents/interpreters.mdx`.

## 14. Sandboxes are backends, not tools

Use a sandbox backend when code needs packages, tests, shell commands, or an OS filesystem. Do not add a nonexistent `PyodideSandboxTool` to `tools=`. A backend implementing the sandbox protocol makes the harness inject `execute` alongside filesystem tools.

```python
from deepagents.backends.langsmith import LangSmithSandbox
from langsmith.sandbox import SandboxClient

client = SandboxClient()
ls_sandbox = client.create_sandbox()
backend = LangSmithSandbox(sandbox=ls_sandbox)

try:
    agent = create_deep_agent(
        model="anthropic:claude-sonnet-4-6",
        system_prompt="Analyze the data inside the sandbox.",
        backend=backend,
    )
    result = agent.invoke({"messages": [{"role": "user", "content": "Analyze /data.csv."}]})
finally:
    client.delete_sandbox(ls_sandbox.name)
```

Other integrations wrap provider objects as `AgentCoreSandbox`, `DaytonaSandbox`, `E2BSandbox`, `ModalSandbox`, `RunloopSandbox`, `VercelSandbox`, or `OpenShellSandbox`; `LocalShellBackend` is non-isolated development execution. Move application files across the boundary with `backend.upload_files([(absolute_path, bytes)])` and retrieve artifacts with `backend.download_files([provider_appropriate_sandbox_paths])`. The agent itself uses filesystem tools inside the sandbox.

Sources: `deepagents/sandboxes.mdx` and `deepagents/code/remote-sandboxes.mdx`.

## 15. MCP tools use the LangChain adapters

The current client integration is stateless by default: `get_tools()` returns LangChain tools, and each call gets a fresh session unless explicit session management is used.

```python
from deepagents import create_deep_agent
from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient({
    "math": {
        "transport": "stdio",
        "command": "python",
        "args": ["math_server.py"],
    },
    "weather": {
        "transport": "http",
        "url": "https://example.com/mcp",
    },
})
tools = await client.get_tools()
agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    system_prompt="Use MCP tools when they are relevant.",
    tools=tools,
)
result = await agent.ainvoke({"messages": [{"role": "user", "content": "Check the weather."}]})
```

Use `transport: "http"` for streamable HTTP. `streamable_http` and `streamable-http` remain accepted aliases, but they are not the documented current spelling. `get_tools()` is stateless by default. When a server genuinely needs one persistent MCP session across tool calls, use the current explicit form `async with client.session("server_name") as session:` and load tools from that session; do not use the obsolete `async with client as session` shape.

Sources: `langchain/mcp.mdx` and `deepagents/code/mcp-tools.mdx`.

## 16. Production naming and invocation boundaries

The recommended hosted path is **Managed Deep Agents**, a LangSmith CLI-first runtime currently in private preview. Use a direct **LangSmith Deployment** when custom application code, routes, or advanced authentication are required. "LangGraph Platform" and "LangGraph Cloud" are former hosted-product names. **LangGraph Server** remains a current technical term for the agent runtime/server, but it is not the hosted product brand.

The Deep Agents CLI exposes `deepagents deploy` for shipping an agent to LangSmith Deployments. Direct graph-factory deployment examples use `langgraph deploy`, while standalone self-hosted images use `langgraph build`. Do not collapse these paths into one command. A deployment provisions threads, runs, a store, and a checkpointer, so application code should not inject its own store or checkpointer there.

Every production run has two independent identifiers:

- `thread_id` selects conversation and checkpoint history.
- `context` carries per-run data described by `context_schema` and read through `runtime.context`.

```python
from langgraph_sdk import get_client

client = get_client(url=DEPLOYMENT_URL, api_key=LANGSMITH_API_KEY)
thread = await client.threads.create()
async for chunk in client.runs.stream(
    thread["thread_id"],
    "agent",
    input={"messages": [{"role": "user", "content": "Plan the trip."}]},
    context={"user_id": "user-123"},
    stream_mode="updates",
):
    print(chunk.data)
```

Keep `thread_id` in the configurable run identity when invoking graphs directly; do not move it into `context`. Conversely, do not hide user IDs, API keys, feature flags, or session metadata under `config.configurable` when they belong to the typed per-run context.

Sources: `deepagents/going-to-production.mdx` and `contributing/code.mdx`.
