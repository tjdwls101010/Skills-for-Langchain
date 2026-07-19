# Use Cases

What to actually ask for. Every prompt below is a starting point you can paste and adapt — the value is in the shape of the request, not the exact words.

The plugin works two ways, and the first section is the one most people underuse.

## Start from a goal and let it consult

You do not need to name a framework, show code, or know what a subagent is.

```text
I want something that reads our incoming support emails and drafts replies.
```

What should happen:

1. **It opens in conversation, not with a form.** Where do the emails live? Should it send or only draft? What makes a reply good — a tone, a knowledge base to cite, cases it must never touch? Is there per-customer history? What volume? Does a human review before anything goes out?
2. **Then it converges** with focused questions across the dimensions you have not already settled.
3. **Then it proposes something concrete** — actual constructors, actual middleware, and the reason each piece is there, traced to the answer that drove it.
4. **Then it stops.** Nothing is written until you say build, and the depth of that build is agreed separately: just the agent code, a runnable scaffold, or a full project.

More examples that enter the same path:

```text
Automate our weekly metrics report so it pulls the numbers and writes the summary.
```

```text
We have 400 PDF manuals. I want customers to be able to ask questions against them.
```

```text
Something that watches our error tracker and opens a triaged ticket when a new class of failure appears.
```

**Expect it to talk you out of things.** If what you described is a cron job and forty lines of Python, it is supposed to say so rather than sell you a Deep Agent. That honesty is the reason it is allowed to trigger on requests that never mention LangChain.

The agreement gate is designed behavior the model follows, not a hard-enforced block — if it gets ahead of itself, see [Troubleshooting](Troubleshooting.md).

## Hand it code and it just fixes the API

No interview on this path. Ask for the thing; it looks up what is current and writes that.

### Build a Deep Agent with a real security boundary

```text
Build a Deep Agent that plans work, reads project files, and writes only under
/workspace. Explain the security boundary you actually get.
```

Expect the current constructor with `system_prompt=`, and `virtual_mode=True` on the filesystem backend. Expect it to distinguish **path protection** from **process isolation** — a `root_dir` alone is not a sandbox, and the skill is instructed to say so rather than let the naming imply safety.

### Long-term memory without cross-user leakage

```text
Add long-term memory to this Deep Agent. Memories must survive new threads and
stay isolated per user ID.
```

The interesting part is the isolation. A store with one global namespace works perfectly in testing and leaks one customer's history into another's the first time it serves two users.

### Coordinate specialists

```text
Create a coordinator with research and writing specialists using the current
LangChain multi-agent pattern.
```

This is a gotcha case: the `supervisor` package was removed, and the model reaches for it from memory. Expect agents wrapped as tools under a coordinator `create_agent`, or Deep Agents subagents.

### Run long-lived work concurrently

```text
Run research and implementation specialists in parallel. The coordinator must be
able to check, steer, cancel, and list their tasks.
```

Expect first-class `AsyncSubAgent` specifications passed through `subagents=[...]` rather than hand-rolled `asyncio`. This area is preview — pin your versions and test.

### Keep a long conversation from drowning

```text
Keep this agent useful across a very long conversation, and stop huge tool
outputs from flooding the context window.
```

Worth asking because the answer is partly "you already have this" — Deep Agents does some of it automatically — and partly current middleware parameters whose names changed.

### Stream current LangGraph events

```text
Stream messages, tool calls, values, and interrupts from this LangGraph agent
using the current event API.
```

### Human approval and filesystem permissions

```text
Require approval before destructive file operations, deny access to secrets,
and allow ordinary workspace reads.
```

Two different mechanisms that are easy to conflate: `interrupt_on` decisions, and first-match filesystem permission rules. Defaults are permissive; ask what they actually are.

### Review existing code

```text
Review this agent implementation specifically for outdated LangChain, LangGraph,
or Deep Agents APIs. Cite the current pattern for every correction.
```

The plugin is at least as useful for review as for generation — reviewing is where a renamed parameter gets caught before it reaches production instead of after.

## Ask the knowledge base directly

You can bypass the agent framing entirely and use the database as a documentation search:

```text
What does the official documentation say about Deep Agents sandbox backends?
Quote the relevant part.
```

```text
What changed in the most recent langchain and deepagents releases according to
the changelog in the plugin's database?
```

The second maps onto the `changelog` table, which holds parsed release notes from the snapshot.

## Getting better results

- **Say "use current APIs."** It is not required — the forcing function should fire anyway — but it makes a skipped lookup visible when it happens.
- **Watch for the `sqlite3` call.** It is your evidence that the answer came from documentation rather than memory. No query, no trust.
- **Give it real constraints.** "Must run on a schedule," "compliance requires a human approves sends," "we only have one API key" change the architecture far more than any framework preference.
- **Push back on the proposal.** The consultant is built to revise. Reacting to a concrete design is more productive than answering another open question.
- **Check the snapshot date** when something looks off — see [The Knowledge Base](The-Knowledge-Base.md).

## Where it will not help

Package installation, running your application, writing your tests, or judging whether your deployment is secure. It also does not know about anything released after its snapshot date, and it does not cover JavaScript or TypeScript at all. See [Coverage and Limits](Coverage-and-Limits.md).

---

**Next:** [Coverage and Limits](Coverage-and-Limits.md) for the boundary, or [Troubleshooting](Troubleshooting.md) if something misbehaved.

Back to the [documentation index](README.md).
