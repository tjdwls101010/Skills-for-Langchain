# 03 — references/deepagents.md content specification

This is the spec for the largest reference file. It covers the 16 Deep Agents topics the probes measured the model getting wrong. For each topic you get: the **wrong prior** (what the model actually produced in the blind probe, so you can lead with the correction), the **current API** (concrete, with the minimal code that makes it unambiguous), **why it matters** (the reasoning the model needs to generalize, per the conviction principle), the **source** doc file to verify against, and **version gates** where they exist.

Author the reference file in that spirit: each topic is a correction, framed reason-first, teaching only the delta and nothing the model already does right. Where a topic has a part the model handled correctly in the probe, that part is called out as "do not re-teach" — leave it out of the reference.

All facts below are drawn from `research/probe-results.md` (the graders' `current_correct_api` and `key_deltas`) and `research/novelty-catalog.md`. **Verify each against the cited doc file before shipping** — the docs are the ground truth, this plan is a distillation of them.

Recommended section order for the file (build-flow order): core → backends & filesystem security → long-term memory → context engineering → subagents → async subagents → dynamic subagents → skills → human-in-the-loop → permissions → rubric middleware → harness profiles → interpreters/PTC → sandboxes → MCP → production. If `deepagents.md` grows unwieldy, the natural split seam is after "permissions" (everything above is the common build path; everything below is advanced/specialized) — but prefer one file.

Open the file with a one-line scope note and the version stamp ("Verified against deepagents (Python) … April 2026"), then the topics.

---

## 1. Creating a deep agent — core surface (probe C1, C2)

**Wrong prior.** The model calls `create_deep_agent(tools=..., instructions=..., model=ChatAnthropic(...))`, lists the built-in tools as only `write_todos`/`ls`/`read_file`/`write_file`/`edit_file`/`task`, and sometimes relies on a hidden default model.

**Current API.**

```python
from deepagents import create_deep_agent

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",   # provider:model string (init_chat_model) or a BaseChatModel; pass it explicitly
    system_prompt="You are a research assistant.",   # NOT instructions=
    tools=[my_tool],                        # only YOUR tools; the built-ins are injected automatically
)

result = agent.invoke({"messages": [{"role": "user", "content": "..."}]})
final = result["messages"][-1].content      # docs prefer result["messages"][-1].content_blocks
```

Full constructor parameters (name them so the model stops guessing): `model`, `system_prompt`, `tools`, `memory`, `skills`, `backend`, `permissions`, `subagents`, `middleware`, `interrupt_on`, `response_format`, `state_schema`, `context_schema`, `checkpointer`, `store`.

Built-in tools injected on every deep agent (this is broader than the model thinks): `write_todos` (planning; statuses pending/in_progress/completed); the virtual filesystem `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`; `execute` (only with a sandbox backend); and `task` (spawns subagents). Built-in *capabilities* beyond tools: skills, memory, automatic summarization and large-result offloading, automatic prompt caching for Anthropic/Bedrock models, human-in-the-loop, and filesystem permissions.

Seeding the virtual filesystem on input needs `create_file_data()` — raw `{name: string}` dicts are rejected:

```python
from deepagents.backends.utils import create_file_data
agent.invoke({"messages": [...], "files": {"notes.txt": create_file_data("...")}})
```

**Why it matters.** `instructions=` is the single highest-frequency error in the whole probe — the model used it in almost every Deep Agents task, and it raises `TypeError` under the current signature. The prompt parameter was renamed to `system_prompt=` to align with LangChain's `create_agent`. This one correction belongs both here and in the SKILL.md body.

**Source.** `deepagents/overview.mdx`, `customization.mdx`, `quickstart.mdx`, `models.mdx`.

---

## 2. Backends and filesystem security (probe C3)

**Wrong prior.** The model writes `FilesystemBackend(root_dir=...)` and then claims in a comment that `..` and absolute-path escapes are blocked — but omits `virtual_mode=True`, so nothing is blocked.

**Current API.**

```python
from deepagents.backends import FilesystemBackend, StateBackend, CompositeBackend

backend = CompositeBackend(
    default=StateBackend(),                                  # internal ephemeral files stay in state
    routes={"/workspace/": FilesystemBackend(root_dir="/abs/workspace", virtual_mode=True)},
)
agent = create_deep_agent(model="anthropic:claude-sonnet-4-6", system_prompt="...", backend=backend)
```

Key facts: `virtual_mode=True` is **required** to sandbox — the default `virtual_mode=False` performs no path protection at all, even with `root_dir` set. `root_dir` must be an absolute path. `StateBackend` (the default when you pass no backend) is thread-scoped: it persists across turns via a checkpointer but not across threads. Wrapping the real-disk backend in a `CompositeBackend` keeps the agent's internal `/large_tool_results/` and `/conversation_history/` off real disk. Backends are passed as constructed instances; the old `backend=lambda rt: StateBackend(rt)` factory form is deprecated (deepagents 0.5.0) — `backend=StateBackend()` now resolves runtime internally.

**Why it matters.** The default-insecure behavior is a genuine security trap: the model's code *looks* sandboxed and its comment asserts it is, but a malicious path traverses right out of `root_dir`. Stating the default (`False` = no protection) lets the model get this right in cases this plan does not enumerate.

**Source.** `deepagents/backends.mdx`.

---

## 3. Long-term (cross-thread) memory (probe C4)

**Wrong prior.** The model gets the overall shape right — `CompositeBackend` routing `/memories/` to a `StoreBackend`, plus a `store=` — but writes `StoreBackend()` with no namespace and omits `model=`.

**Current API.**

```python
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend

backend = CompositeBackend(
    default=StateBackend(),
    routes={"/memories/": StoreBackend(namespace=lambda rt: (rt.server_info.user.identity,))},
)
agent = create_deep_agent(model="anthropic:claude-sonnet-4-6", system_prompt="...", backend=backend, store=store)
```

`StoreBackend` needs a `namespace` factory (it becomes required in deepagents 0.5.0). Without it, every user of the same assistant shares one storage bucket — a real multi-user data-isolation bug. The factory receives a `Runtime`, so it can key on `rt.server_info.user.identity`, `rt.context`, or `rt.execution_info.thread_id`. Provide the store yourself in dev (`InMemoryStore()` from `langgraph.store.memory`) or prod (`PostgresStore.from_conn_string(DB_URI)` + `store.setup()`), but **omit `store=` on a LangSmith Deployment**, which auto-provisions one. `StateBackend` is thread-scoped; `StoreBackend` is the cross-thread durable layer.

**Why it matters.** The missing namespace is silent — the code runs fine in a single-user test and leaks across users in production. That is exactly the kind of gotcha worth the skill's tokens.

**Source.** `deepagents/backends.mdx`, `memory.mdx`, `context-engineering.mdx`.

---

## 4. Context engineering — it is automatic (probe C7)

**Wrong prior.** The model hand-assembles `middleware=[SummarizationMiddleware(...), ContextEditingMiddleware(edits=[ClearToolUsesEdit(...)])]` to get summarization and large-result offloading.

**Current API.** Both behaviors are **built in and automatic** in every `create_deep_agent` — you do not add middleware to enable them. Offloading moves tool inputs/results larger than ~20,000 tokens to the backend filesystem, replacing them with a file-path reference plus a first-10-lines preview, and truncates older tool calls as context crosses ~85% of the model window. Summarization triggers at ~85% of the model's `max_input_tokens` (fallback trigger 170,000 tokens / 6 messages), keeps ~10% as recent context, writes the original conversation to the filesystem, and falls back automatically on `ContextOverflowError`. For explicit, on-demand compaction between tasks, pass `create_summarization_tool_middleware` via `middleware=` — it adds a `compact_conversation` tool.

**Why it matters.** The correction is subtractive: the idiomatic answer is *do nothing*, plus optional tuning. Hand-adding the middleware duplicates the default stack and can misconfigure the thresholds. (If the model does tune the underlying `SummarizationMiddleware`, note the parameter names are `trigger=("tokens", N)` / `keep=("messages", N)` — cross-reference the LangChain delta in `04`.)

**Source.** `deepagents/context-engineering.mdx`.

---

## 5. Subagents (probe C5)

**Wrong prior.** The structure is right (`subagents=[dict, ...]`, delegation via the auto-added `task` tool) but the model uses the legacy keys: `instructions=` on the main agent and `prompt` as the subagent dict key.

**Current API.** Each subagent is a spec dict with required keys `name`, `description`, `system_prompt` (not `prompt`), plus optional `tools`, `model`, `middleware`, `interrupt_on`, `skills`, `response_format`, `permissions`.

```python
agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    system_prompt="You coordinate specialists.",
    subagents=[
        {"name": "researcher", "description": "Finds sources", "system_prompt": "You research thoroughly."},
        {"name": "writer", "description": "Drafts prose", "system_prompt": "You write clearly."},
    ],
)
```

A subagent's `system_prompt` does not inherit from the main agent; `tools`/`model` do inherit unless overridden. A `general-purpose` subagent is auto-added unless you supply one by that name. For a custom compiled graph as a subagent, use `CompiledSubAgent(name, description, runnable=graph)` — the field is `runnable=`, not `graph=` — imported from `deepagents.middleware.subagents`.

**Why it matters.** Same `instructions`/`prompt` legacy-naming trap as topic 1, now on the nested spec. Do not re-teach the list-of-dicts shape, the `task` tool, the general-purpose auto-subagent, or the invoke shape — the model gets those right.

**Source.** `deepagents/subagents.mdx`.

---

## 6. Async subagents (probe C6 — model admitted it did not know)

**Wrong prior.** Believing no first-class API exists, the model hand-rolls parallelism from LangGraph primitives: several sync `task` calls, `asyncio` task cancellation, `aupdate_state`/`Command(resume=...)` for steering.

**Current API.** Async subagents are a first-class preview feature (deepagents 0.5.0 Python / 1.9.0 JS). Configure them by passing `AsyncSubAgent` specs whose fields are `name` (required), `description` (required), `graph_id` (required; the graph/assistant ID on an Agent Protocol server, matching `langgraph.json` for LangGraph deployments), `url` (optional — omit for in-process ASGI transport, set it for HTTP to a remote Agent Protocol server), and `headers` (optional auth). When async subagents are configured, `create_deep_agent` auto-adds `AsyncSubAgentMiddleware`, which gives the supervisor five tools it calls like any other: `start_async_task` (launch, returns a `task_id` immediately, non-blocking), `check_async_task` (status + result), `update_async_task` (steer a running task with new instructions, same `task_id`), `cancel_async_task` (server-side cancellation), and `list_async_tasks`. Each subagent runs on its own thread on an Agent Protocol server (LangSmith Deployments or self-hosted). Task metadata lives in a dedicated `async_tasks` state channel so IDs survive history compaction.

**Why it matters.** This is a whole capability the model does not know exists, so it reconstructs a worse version from lower-level parts. Naming the five tools and the transport model (ASGI co-deploy vs HTTP remote) is the payload.

**Source.** `deepagents/async-subagents.mdx`.

---

## 7. Dynamic subagents (probe R11)

**Wrong prior.** The model emits N parallel `task` tool calls in one turn, and dismisses truly code-driven fan-out to LangGraph's `Send`.

**Current API.** Dynamic subagents (Beta) run on the interpreter runtime. Install `deepagents[quickjs]` plus `langchain-quickjs>=0.2.0` (Python ≥3.11), and pass `CodeInterpreterMiddleware` via `middleware=`. When the agent has subagents and interpreter middleware, the interpreter exposes a built-in `task()` global (on by default; disable with `CodeInterpreterMiddleware(subagents=False)`). The agent then writes JavaScript in the `eval` tool that holds work in variables and dispatches subagents in loops or parallel batches via `task({ description, subagentType, responseSchema? })`, so the number of subagents is decided at runtime in code rather than fixed when the model emits tool calls. The literal word **"workflow"** in the prompt is the documented lever that makes a code-interpreter deep agent fan out from code.

**Why it matters.** The docs explicitly frame the parallel-tool-call approach the model reaches for as the unreliable thing dynamic subagents replace. This is also where the "workflow" trigger word lives — surprising and worth stating.

**Source.** `deepagents/dynamic-subagents.mdx`, `interpreters.mdx`, `subagents.mdx`.

---

## 8. Skills (probe C8 — model admitted it did not know the attach mechanism)

**Wrong prior.** The model defines a skill correctly as a `SKILL.md` folder (frontmatter + body + `scripts/`) but attaches it by rooting a `FilesystemBackend` at the skills directory — which loads zero skills — and uses `instructions=`.

**Current API.** Attach skills with the dedicated `skills=[paths]` parameter (a `list[str]` of source paths, forward-slash, relative to the backend root):

```python
from deepagents.backends import FilesystemBackend
agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    system_prompt="...",
    skills=["pdf-fill"],
    backend=FilesystemBackend(root_dir="skills", virtual_mode=True),
)
```

Passing `skills=` auto-adds `SkillsMiddleware` (before `FilesystemMiddleware`), which handles progressive disclosure: level-1 name/description into the system prompt at startup, level-2 body read on invoke. A backend alone does not scan for skills — the docs state the SDK only loads the sources you pass in `skills`. With the default `StateBackend`, supply skill file contents at invoke via `invoke(files={...})` using `create_file_data()`; a `FilesystemBackend`/`StoreBackend` loads them from disk/store.

**Do not re-teach** the skill *definition* format (`SKILL.md`, YAML `name`/`description`, `scripts/`/`references/`/`assets/`, progressive disclosure) — the model gets that right. Teach only the `skills=` attach mechanism.

**Source.** `deepagents/skills.mdx`, `customization.mdx`.

---

## 9. Human-in-the-loop (probe C9)

**Wrong prior.** The model invents an `interrupt_config` kwarg using LangGraph's old `HumanInterruptConfig` boolean flags (`allow_accept`/`allow_edit`/`allow_respond`/`allow_ignore`) and resumes with a bare list `Command(resume=[{"type": "accept"}])`.

**Current API.** The kwarg is `interrupt_on` on `create_deep_agent`:

```python
from langgraph.types import Command
agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    system_prompt="...",
    tools=[send_email],
    interrupt_on={"send_email": {"allowed_decisions": ["approve", "edit", "reject", "respond"]}},
    checkpointer=checkpointer,   # required
)
result = agent.invoke({"messages": [...]}, config={"configurable": {"thread_id": "t1"}}, version="v2")
if result.interrupts:                                   # JS: result.__interrupt__
    # result.interrupts[0].value == {"action_requests": [...], "review_configs": [...]}
    result = agent.invoke(Command(resume={"decisions": [{"type": "approve"}]}),
                          config={"configurable": {"thread_id": "t1"}}, version="v2")
final = result.value["messages"][-1].content            # note result.value under v2
```

`interrupt_on` maps each tool to `True` (all default decisions), `False` (off), or an `InterruptOnConfig` with `allowed_decisions`; an optional `when` predicate on a `ToolCallRequest` gives conditional interrupts (langchain ≥1.3.3). The decision types are `approve`/`edit`/`reject`/`respond` — there is no `ignore` or `accept`. Edit shape: `{"type": "edit", "edited_action": {"name": tool_name, "args": {...}}}`. Reject shape: `{"type": "reject", "message": "..."}`. Resume is always `Command(resume={"decisions": [...]})` (a dict with a `decisions` key), with the same `thread_id` and `version="v2"`. A checkpointer is required.

**Why it matters.** Nearly every token here is a correction — wrong kwarg name, wrong config shape, wrong decision vocabulary, wrong resume payload, wrong result accessor. The model was `outdated_confident`, so it will produce runnable-looking but broken code without this.

**Source.** `deepagents/human-in-the-loop.mdx`.

---

## 10. Filesystem permissions (probe C10 — model admitted it guessed)

**Wrong prior.** The model invents `FilesystemBackend(permissions={path: "write"/"read"/"none"})` — a dict on the backend.

**Current API.** Permissions are a **list** of `FilesystemPermission` rules on `create_deep_agent`, not a backend dict:

```python
from deepagents import create_deep_agent, FilesystemPermission

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    system_prompt="...",
    backend=FilesystemBackend(root_dir="/workspace", virtual_mode=True),
    permissions=[
        FilesystemPermission(operations=["read", "write"], paths=["/workspace/**"], mode="allow"),
        FilesystemPermission(operations=["write"], paths=["/workspace/config/**"], mode="deny"),
        FilesystemPermission(operations=["read", "write"], paths=["/workspace/secrets/**"], mode="deny"),
    ],
)
```

`operations` is `["read"]` (covers `ls`/`read_file`/`glob`/`grep`) and/or `["write"]` (covers `write_file`/`edit_file`/`delete`). `paths` are glob patterns (`**` recursive, `{a,b}` alternation). Evaluation is first-match-wins with a permissive default (unmatched operations are allowed), so put specific rules before broad ones. A read-only path is a `deny` on `["write"]`; a fully blocked path is `deny` on both — there is no `"none"` level. `mode="interrupt"` pauses for HITL approval (deepagents ≥0.6.8). Permissions require deepagents ≥0.5.2, apply only to the built-in filesystem tools (not custom/MCP tools, not sandbox backends), are inherited by subagents, and `permissions=[]` means unrestricted.

**Source.** `deepagents/permissions.mdx`.

---

## 11. Rubric middleware — LLM-as-judge loop (probe R10)

**Wrong prior.** At high confidence the model claims deepagents has no judge-loop primitive and hand-rolls a critique subagent plus prompt-driven revision loop that self-parses a PASS string.

**Current API.** deepagents ships `RubricMiddleware` (deepagents ≥0.6.5, beta) for exactly this:

```python
from deepagents.middleware import RubricMiddleware   # verify exact import path against rubric.mdx
agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    system_prompt="...",
    middleware=[RubricMiddleware(model="anthropic:claude-sonnet-4-6", max_iterations=3)],
)
result = agent.invoke({"messages": [...], "rubric": "1. Cites sources\n2. Under 200 words"})
```

Trigger the self-evaluate/iterate loop by passing a `rubric` string on invoke state; with no `rubric` the middleware is inert. Configure the grader on the middleware, not in prose: `RubricMiddleware(model=, max_iterations=3, system_prompt=<optional grader prompt>, tools=<optional evidence-gathering tools>, on_evaluation=<callback>)`. The grader returns a fixed verdict enum — `satisfied` / `needs_revision` (feedback injected, agent re-runs) / `max_iterations_reached` / `failed` / `grader_error` — and manages the loop-back itself; you do not parse PASS/FAIL. Observe via the `on_evaluation` callback or `rubric_evaluation_start`/`rubric_evaluation_end` events on `stream.custom`. A `RubricCodeGenerationMiddleware` variant exists for vetted code generation.

**Why it matters.** The model's stated premise ("no primitive exists") is false, so it builds a brittle hand-rolled loop. Naming the middleware and the state-triggered `rubric` mechanism replaces the whole thing.

**Source.** `deepagents/rubric.mdx`.

---

## 12. Harness profiles — per-provider tuning (probe C11 — model did not know)

**Wrong prior.** The model hand-rolls a per-provider Python dict selecting model/tools/`instructions` by provider.

**Current API.** Harness profiles (Beta) tune the harness per provider without touching the `create_deep_agent` call site:

```python
from deepagents import HarnessProfile, register_harness_profile   # verify import against profiles.mdx
register_harness_profile("anthropic", HarnessProfile(system_prompt_suffix="Think step by step."))
register_harness_profile("openai", HarnessProfile(base_system_prompt="You are concise."))
# create_deep_agent(model="anthropic:...") now applies the anthropic profile automatically
```

`HarnessProfile` fields: `base_system_prompt`, `system_prompt_suffix`, `tool_description_overrides`, `excluded_tools`, `excluded_middleware`, `extra_middleware`, `general_purpose_subagent`. `register_harness_profile` is keyed by a bare provider (`"anthropic"`, `"openai"`) or a `provider:model` string, and provider-level and model-level entries merge. deepagents ships built-in Anthropic and OpenAI profiles, so some tuning is automatic on model selection. A companion `ProviderProfile` + `register_provider_profile` (Python-only) packages `init_chat_model` construction kwargs (`init_kwargs`, `pre_init`, `init_kwargs_factory`). YAML config via `HarnessProfileConfig`; JS uses `HarnessProfileOptions`/`registerHarnessProfile` and lacks provider profiles.

**Source.** `deepagents/profiles.mdx`, `customization.mdx`.

---

## 13. Interpreters / programmatic tool calling (probe R12 — model invented the API)

**Wrong prior.** The model invents `CodeExecutionMiddleware(tools=..., sandbox=False)` running Python.

**Current API.** The feature is `CodeInterpreterMiddleware` with programmatic tool calling (PTC), Beta. Install `deepagents[quickjs]` (`langchain-quickjs>=0.2.0`, Python ≥3.11), then:

```python
from deepagents.middleware import CodeInterpreterMiddleware
agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    system_prompt="...",
    tools=[search, fetch, score],
    middleware=[CodeInterpreterMiddleware(ptc=[search, fetch, score])],
)
```

The middleware adds an `eval` tool; the agent writes JavaScript (QuickJS, in-memory, no host filesystem/network/shell/clock by default) and orchestrates the allowlisted tools in loops/branches/retries/parallel batches under a `tools.*` namespace, where tool names are camelCased and awaited (`web_search` becomes `await tools.webSearch(...)`); only the final interpreter result returns to the model. PTC is off by default and enabled solely via the `ptc=` allowlist (tool-name strings or `BaseTool` instances). Other kwargs: `max_ptc_calls` (default 256), `mode` (`"thread"`/`"turn"`/`"call"`, default `"thread"`), `timeout` (5.0s), `tool_name` (`"eval"`), `capture_console`, `max_result_chars`, `subagents` (True). This is the in-loop, non-remote path and runs JavaScript, not Python; the added tool is `eval`, not `execute_python`. PTC calls bypass `interrupt_on` approval.

**Why it matters.** The model invents a plausible Python-shaped API that does not exist. Two facts anchor the correction: the class is `CodeInterpreterMiddleware` with a `ptc=` allowlist, and the interpreter is JavaScript/QuickJS. It is distinct from sandbox backends (topic 14).

**Source.** `deepagents/interpreters.mdx`, `customization.mdx`.

---

## 14. Sandboxes for code execution (probe C12)

**Wrong prior.** The model constructs `langchain_sandbox.PyodideSandboxTool(...)` (which does not exist in these docs) and passes it in `tools=`.

**Current API.** In Deep Agents, sandboxes are **backends, not tools**. Create a provider sandbox, wrap it, and pass it via `backend=`; `create_deep_agent` auto-adds the `execute` tool because the backend implements `SandboxBackendProtocol`:

```python
from deepagents import create_deep_agent
from deepagents.backends.langsmith import LangSmithSandbox
from langsmith.sandbox import SandboxClient

client = SandboxClient()
sb = client.create_sandbox()
try:
    agent = create_deep_agent(model="anthropic:claude-sonnet-4-6", system_prompt="...",
                              backend=LangSmithSandbox(sandbox=sb))
    result = agent.invoke({"messages": [{"role": "user", "content": "analyze data.csv"}]})
finally:
    sb.delete()   # explicit lifecycle
```

Other backends wrap each provider's SDK: `langchain_daytona.DaytonaSandbox`, `langchain_e2b.E2BSandbox`, `langchain_modal.ModalSandbox`, `langchain_runloop.RunloopSandbox`, `langchain_vercel_sandbox.VercelSandbox`, `langchain_agentcore_codeinterpreter.AgentCoreSandbox`, `langchain_nvidia_openshell.OpenShellSandbox`; `LocalShellBackend` is for local dev. Move data across the boundary with `backend.upload_files([(path, bytes)])` / `backend.download_files([paths])`, not agent tools. For pandas/numpy data analysis use a sandbox backend; the QuickJS interpreter (topic 13) is a different, in-loop feature and is not the tool for that.

**Source.** `deepagents/sandboxes.mdx`, `backends.mdx`, `data-analysis.mdx`.

---

## 15. MCP tools (probe C14)

**Wrong prior.** The integration shape is right, but the model uses `instructions=` and the older `transport: "streamable_http"` spelling.

**Current API.**

```python
from deepagents import create_deep_agent
from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient({
    "math": {"transport": "stdio", "command": "python", "args": ["math_server.py"]},
    "weather": {"transport": "http", "url": "https://.../mcp"},   # "http", not "streamable_http"
})
tools = await client.get_tools()
agent = create_deep_agent(model="anthropic:claude-sonnet-4-6", tools=tools, system_prompt="...")
result = await agent.ainvoke({"messages": [{"role": "user", "content": "..."}]})
```

`get_tools()` returns LangChain tools directly — the old `async with client as session` context-manager pattern is not needed. The current HTTP transport value is `"http"` (streamable-http); `"streamable_http"` is only an accepted alias, not the documented idiom. And, as everywhere, `system_prompt=` not `instructions=`.

**Do not re-teach** the `MultiServerMCPClient(...).get_tools()` shape — the model gets it right.

**Source.** `deepagents/mcp.mdx`, `overview.mdx`, `deepagents/code/mcp-tools`.

---

## 16. Production deployment (probe C13)

**Wrong prior.** The model correctly names `langgraph.json` + the CLI + `langgraph_sdk`, but frames the recommended path as the stale "LangGraph Platform / LangGraph Server" and omits per-run `context=`.

**Current API (teach only the delta).** The recommended path is **Managed Deep Agents** — a LangSmith CLI-first hosted runtime (private preview) for creating, running, and operating deep agents; for custom application code, routes, or advanced auth, use a **LangSmith Deployment** directly. The branding is now "LangSmith Deployments" (formerly "LangGraph Platform / Cloud / Server"). Managed deploy uses `langgraph deploy`; self-host still uses `langgraph build` → Docker. Every production invocation should pass **both** `thread_id` (conversation/checkpoints, in `config["configurable"]`) **and** `context=` (per-run data, defined by `context_schema`, not `config.configurable`):

```python
from langgraph_sdk import get_client
client = get_client(url=..., api_key=...)
thread = await client.threads.create()
async for chunk in client.runs.stream(thread["thread_id"], "agent",
                                       input={"messages": [...]},
                                       context={"user_id": "u1"},
                                       stream_mode="updates"):
    ...
```

A deployment injects the checkpointer and store, so do not pass your own.

**Do not re-teach** the `langgraph.json` shape (`dependencies`/`graphs`/`env`), `langgraph dev`/`langgraph build`, or the `get_client`/`threads.create`/`runs.stream` API — the model reproduces those correctly. Teach only: the Managed Deep Agents recommendation, the LangSmith Deployments naming, and the `context=` argument.

**Source.** `deepagents/going-to-production.mdx`, `comparison.mdx`.
