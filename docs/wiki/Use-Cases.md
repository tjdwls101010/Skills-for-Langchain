# Use Cases

The plugin is most useful when an apparently ordinary task crosses a recent API boundary. The prompts below are recipes, not fixed commands; adapt them to your application.

## 1. Build a Deep Agent safely

```text
Build a Deep Agent that plans work, reads project files, and writes only under /workspace. Explain the security boundary.
```

The skill reinforces the current constructor, built-in tools, `FilesystemBackend(..., virtual_mode=True)`, and the distinction between path protection and process isolation. It does not make local execution safe by itself.

## 2. Add cross-thread memory without cross-user leakage

```text
Add long-term memory to this Deep Agent. Memories must survive new threads and remain isolated by user ID.
```

The skill routes long-term data through `StoreBackend` and a runtime-derived namespace instead of silently sharing one global memory space.

## 3. Coordinate specialists

```text
Create a coordinator with research and writing specialists using the current LangChain multi-agent pattern.
```

The skill replaces the unmaintained supervisor package pattern with agents wrapped as tools under a coordinator `create_agent`.

## 4. Run long-lived work concurrently

```text
Run research and implementation specialists in parallel. The coordinator must be able to check, steer, cancel, and list their tasks.
```

The Deep Agents reference supplies the first-class `AsyncSubAgent` specification and current task lifecycle tools. The feature is preview and should be version-pinned and tested.

## 5. Manage context growth

```text
Keep this agent useful in a very long conversation and prevent huge tool outputs from flooding the context window.
```

The skill explains which summarization and offloading behaviors Deep Agents already provides automatically, when explicit compaction is useful, and which LangChain middleware parameters replaced deprecated names.

## 6. Stream current LangGraph events

```text
Stream messages, tool calls, values, and interrupts from this LangGraph agent using the current event API.
```

The skill points to `stream_events(..., version="v3")`, typed projections, and the lower-level v2 `StreamPart` shape instead of legacy tuple handling.

## 7. Add HITL and filesystem permissions

```text
Require approval before destructive file operations and deny access to secrets while allowing ordinary workspace reads.
```

The skill separates `interrupt_on` decision handling from first-match `FilesystemPermission` rules and calls out permissive defaults and inheritance behavior.

## 8. Review existing code

```text
Review this agent implementation specifically for outdated LangChain, LangGraph, or Deep Agents APIs. Cite the relevant current pattern for every correction.
```

The plugin is as useful for review as generation. It should not be treated as the only source of truth when installed package versions or current official docs disagree with the April-2026 snapshot.

See [Coverage and Limits](Coverage-and-Limits.md) for the complete measured boundary.
