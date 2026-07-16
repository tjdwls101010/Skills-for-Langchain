# Coverage and Limits

## Coverage model

Coverage is evidence-selected rather than documentation-complete. A topic is included when the official docs show a meaningful current pattern and blind probes show that the model is partial, unknown, or confidently outdated.

The tables below describe the **knowledge** coverage. The consultant behavior (added in v1.1.0) is a separate axis: it is process and posture — an interview protocol and a dimension checklist — not additional measured knowledge, and it draws on exactly the same delta references listed here. Its scope is therefore not a probe-measured content boundary; see [Validation and Evidence](Validation-and-Evidence.md) for how it is validated instead.

## LangChain: 6 deltas

| Topic | Main correction |
|---|---|
| Dynamic system prompts | Prefer `@dynamic_prompt`; use `system_message` for full model-call wrappers |
| Summarization | Use `trigger` and `keep`, not deprecated parameter names |
| Multi-agent coordination | Use agent-as-tool rather than the unmaintained supervisor package |
| Model fallback | Use `ModelFallbackMiddleware` at the agent layer |
| Tool-call limits | Preserve the tool limiter's distinct exit semantics |
| Provider tool search | Use `ProviderToolSearchMiddleware` and deferred-tool extras |

## LangGraph: 4 deltas

| Topic | Main correction |
|---|---|
| Event streaming | Use event streaming v3 typed projections; understand the lower-level v2 shape |
| Declarative error handling | Separate retry from `error_handler` compensation; requires `langgraph>=1.2` |
| Interrupts | Use current saver naming, event driver, and ID-keyed parallel resume |
| `DeltaChannel` | Preserve reducer semantics while bounding checkpoint growth |

## Deep Agents: 16 topics

1. Constructor, explicit model, and built-in capabilities.
2. Backend selection and filesystem security boundaries.
3. Cross-thread memory and multi-user namespace isolation.
4. Automatic context summarization and large-result offloading.
5. Declarative and compiled synchronous subagents.
6. First-class asynchronous subagents.
7. Interpreter-backed dynamic subagents.
8. Reusable Deep Agents skills and source-directory semantics.
9. Human-in-the-loop decisions and resume envelopes.
10. First-match filesystem permissions.
11. Rubric-based evaluation loops.
12. Provider- and model-keyed harness profiles.
13. QuickJS code interpreters and programmatic tool calling.
14. Remote sandbox backends and lifecycle management.
15. MCP tool integration and stateful-session details.
16. Managed Deep Agents, LangSmith Deployments, and production invocation boundaries.

## Deliberately excluded measured-correct areas

The regression guard covers 11 areas that the baseline model already handled correctly. The plugin avoids re-teaching them unless a future refresh finds a real regression:

- Basic `create_agent` construction.
- Agent structured output.
- `ToolRuntime` and per-invocation runtime context.
- LangGraph runtime context and functional API.
- `PIIMiddleware`, `ContextEditingMiddleware`, and `LLMToolSelectorMiddleware`.
- LangGraph `durability=`.
- Postgres persistence with encrypted serialization.

## Limits

- **Python only.** JavaScript and TypeScript APIs are outside the measured scope.
- **Point-in-time.** v1.1.0 is verified against an April-2026 documentation snapshot.
- **Version-sensitive.** Several topics require particular package versions or preview access.
- **Not a package manager.** The plugin does not install or pin Python dependencies.
- **Not a runtime sandbox.** Advice about backends and permissions does not enforce isolation.
- **Not comprehensive docs.** Use official documentation for areas not represented here.
- **Not model-universal.** The probe conclusions apply to a specific measured model and task set.
- **Independent project.** This repository is not affiliated with or endorsed by LangChain or Anthropic.

Canonical content lives in [the LangChain/LangGraph reference](../../.claude/skills/langchain/references/langchain-langgraph.md) and [the Deep Agents reference](../../.claude/skills/langchain/references/deepagents.md).
