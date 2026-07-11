# 02 — SKILL.md specification

This specifies the top-level `.claude/skills/LangChain/SKILL.md` exactly: the directory name, the frontmatter, and the body. The body is deliberately short — it loads on every trigger, so it holds only the always-applicable material (mental model, cross-cutting gotchas, routing) and pushes the bulk into the two reference files. Everything below is close to final copy; the implementation session should paste it, then verify each technical claim against the cited docs before shipping.

## Directory name

Use `.claude/skills/LangChain/` (capitalized as the framework capitalizes itself). An empty `.claude/skills/LangChain/` directory already exists on disk from a prior session — reuse it. The directory name is the invocation contract (`/LangChain`), so do not rename it to `skill1`/`langchain-stuff`/etc. The user's request wrote it "Langchain"; "LangChain" is the correct casing and is what the existing directory already uses.

## Frontmatter

```yaml
---
name: LangChain
description: >-
  Current (2026) APIs and gotchas for the LangChain ecosystem — LangChain 1.x,
  LangGraph 1.x, and the Deep Agents SDK (deepagents). Load whenever writing or
  editing Python that builds or configures agents with any of these: importing
  langchain / langgraph / deepagents, calling create_agent or create_deep_agent,
  or working with middleware, subagents, backends, long-term memory,
  human-in-the-loop, permissions, streaming, structured output, or agent
  deployment — even if the user never names a version. Load it especially for
  Deep Agents work, where the model's built-in knowledge is most outdated. It
  carries only the deltas that changed in recent releases (for example
  create_deep_agent(system_prompt=...) not instructions=; create_agent not
  create_react_agent; the deprecated supervisor pattern), so it corrects
  confidently-wrong code the model would otherwise write. Not for other agent
  frameworks (LlamaIndex, CrewAI, AutoGen, the raw OpenAI or Anthropic SDKs)
  unless they are being bridged to LangChain.
---
```

Frontmatter judgment calls, with reasons:

- **`description` is the entire trigger signal** and is the most important thing in this file. It is written to over-trigger deliberately, because the cost asymmetry is steep: a needless load costs a little context, but a missed load means the model writes deprecated code with full confidence and never knows the skill existed. It names the underlying intent ("building or configuring agents"), lists concrete surface triggers (the import names and function names), flags the Deep Agents priority, states what the skill actually contains (deltas, so the model knows this is a correction resource), and draws the near-miss boundary (other frameworks) so it does not steal triggers from unrelated agent work. When the docs are refreshed, re-check this line first — new top-level API names should be added to the trigger list.
- **Do not set `user-invocable: false`.** Leaving it invocable lets the user type `/LangChain` to force-load the reference before starting a session, which is a reasonable convenience; the primary mechanism is still auto-trigger via `description`.
- **Do not set `disable-model-invocation`.** Auto-triggering is the whole point of this skill.
- **No `allowed-tools`, no `hooks`, no `context: fork`.** This is reference knowledge, not a task with a verb, so none of those apply.

Note the mechanical trap the validator guards against: if this YAML fails to parse, the skill still loads on `/LangChain` but silently stops auto-triggering (empty metadata, no `description` to match). Run `validate_harness.py` after writing it.

## Body

Keep the body to roughly this length. It is loaded on every trigger, so anything that is not needed on nearly every invocation belongs in a reference file instead.

```markdown
# LangChain ecosystem — current APIs and gotchas

This skill carries only what has **changed or is new** in the LangChain ecosystem relative to older knowledge — the deltas the model tends to get confidently wrong. It does not restate the parts the model already handles correctly (basic `create_agent` usage, custom middleware, `ToolRuntime`, structured output, LangGraph runtime context and the functional API, `PIIMiddleware`/`ContextEditingMiddleware`, `durability=`, Postgres persistence). If your code already matches the current API for one of those, trust it.

Verified against LangChain 1.x / LangGraph 1.x / deepagents (Python) — snapshot April 2026. See "Staying current" at the bottom before trusting this on a much newer release.

## The three layers (orient here first)

- **LangChain** is the framework: `create_agent` builds one agent (model + tools + middleware). Reach for it when customizing a single agent's loop.
- **LangGraph** is the runtime underneath: hand-rolled graphs, persistence, interrupts, streaming. Reach for it when you need control LangChain's agent abstraction does not give you.
- **Deep Agents** (`deepagents`) is the batteries-included harness on top: planning, a virtual filesystem, subagents, memory, and context management built in via `create_deep_agent`. Reach for it when you want an agent that plans and manages its own context without wiring it yourself. This is where the model's knowledge is weakest — see references/deepagents.md.

## Cross-cutting gotchas (apply on almost every task)

- **Deep Agents uses `system_prompt=`, never `instructions=`.** `create_deep_agent(instructions=...)` and the subagent dict key `prompt` are both from an old version and raise `TypeError` / are ignored today. The current names are `system_prompt=` on the constructor and `system_prompt` in each subagent spec.
- **Model IDs in this ecosystem are real, including ones that look like typos.** `claude-sonnet-4-6`, `claude-opus-4-8`, `gpt-5.5`, `gemini-3.5-flash` are valid current IDs. Never "correct" them to older-looking numbers. Pass the model explicitly as a `provider:model` string (for example `model="anthropic:claude-sonnet-4-6"`), resolved via `init_chat_model`, or as a `BaseChatModel` instance — do not rely on a hidden default.
- **The agent constructor is `create_agent` from `langchain.agents`**, not `create_react_agent` (langgraph.prebuilt) and not the removed `AgentExecutor`/`initialize_agent`. It returns an already-compiled graph — there is no `.compile()` step.

## Which reference to open

- **references/deepagents.md** — anything with `deepagents` / `create_deep_agent`: built-in tools, backends and filesystem security, subagents (sync/async/dynamic), memory, context engineering, skills, human-in-the-loop, permissions, harness profiles, sandboxes and interpreters, rubric middleware, MCP, and production deployment.
- **references/langchain-langgraph.md** — the handful of `create_agent`/LangGraph deltas: `SummarizationMiddleware` parameters, the deprecated supervisor pattern, `ModelFallbackMiddleware`, `ToolCallLimitMiddleware`, `ProviderToolSearchMiddleware`, event streaming (`stream_events` v3), declarative error handling, `interrupt` nuances, and `DeltaChannel`.

## Staying current

This skill is a point-in-time distillation. To refresh it against a newer release, follow references/../ (see the maintenance note): re-fetch the official docs, re-run the knowledge probes in the plan, and update only the deltas that changed. Treat a version far past the stamp above with caution and verify against the live docs.
```

## Notes for the implementer

- The "Staying current" section references the maintenance procedure. Point it at wherever the refresh procedure ultimately lives — either a short `references/maintenance.md` (if you decide the procedure is worth bundling) or the plan's `05`/`06`. Decide this while authoring; a one-paragraph pointer is enough, do not bloat the body.
- The body intentionally repeats the excluded list once (top paragraph) because telling the model *not to distrust its own correct code* is itself high-value: without it, a "correction skill" can make the model second-guess things it was doing right. Keep that paragraph.
- Verify the three cross-cutting gotchas against the docs before shipping: `system_prompt=` (deepagents/overview.mdx, customization.mdx), the model-ID list (any quickstart), and `create_agent` location (langchain/agents.mdx).
