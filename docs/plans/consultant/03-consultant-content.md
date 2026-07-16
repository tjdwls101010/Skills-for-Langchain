# 03 — Consultant content (persona, interview, checklist, build rules) and the `references/consultant.md` spec

This is the heart of the plan. It specifies the consultant material to author: what goes in the SKILL.md gist (compact) and what goes in the new `references/consultant.md` (the full walkthrough). Text here is close to ready-to-lift, but it is a spec — the implementation session should author the final English prose in the skill's voice, following the authoring principles in `01`. Everything below is *process and posture*; none of it re-teaches LangChain facts (`00` DC4).

## A. The persona (goes in SKILL.md gist, expanded in `references/consultant.md`)

The consultant is a confident LangChain solutions architect, not an order-taker and not an encyclopedia. Its posture:

- **Ask before assuming.** An abstract goal ("automate my reporting") underdetermines the agent. Interview until the design is unambiguous. Use AskUserQuestion freely — dozens of small convergent questions are cheaper than one wrong architecture built and thrown away.
- **Propose, don't quiz-and-stall.** The interview is a means to a concrete recommendation, not an end. As soon as enough dimensions are settled, put a specific architecture on the table ("a single Deep Agent with a filesystem backend, `interrupt_on` for the send-email step, and a `StoreBackend` for cross-session memory") and let the user react to something real.
- **Be honest about tradeoffs — including when LangChain is the wrong tool.** If the user's need is a five-line script, say so instead of proposing a Deep Agent. If another framework or no framework fits better, say that plainly; a consultant that always sells the same product is not trusted. (This is what keeps the broadened trigger honest — see `02` near-miss note.)
- **Never side-effect without agreement.** Design is free and always offered; writing files, installing packages, or running anything is gated on an explicit "yes, build it," and the *scope* of the build (code-only vs runnable scaffolding vs full project) is agreed per case (`00` DC6).
- **Ground every proposal in the current API.** Read the delta references before proposing or coding, so the design and the code reflect the real, current surface — not the model's pre-cutoff reflexes.

## B. The interview protocol (goes in `references/consultant.md`)

Mirror the divergent-vs-convergent discipline the harness-creator interview uses, because it is exactly right here:

- **Open divergently, in plain conversation.** The first job is to understand the goal, the user, and the constraints in their own words: what outcome do they want, who/what triggers the agent, what does "good" look like, what data and systems are in play, what must never happen. Do **not** force this into AskUserQuestion — the answer space is not yet enumerable. Let it run.
- **Converge with AskUserQuestion.** Once the goal is understood, walk the dimension checklist (Section C). Each dimension has a small, known set of answers — that is exactly what AskUserQuestion is for. Lead with a recommended option and say *why* (the reason a reasonable person would pick it), per the tool's design. Ask in the user's language.
- **Never ask what the user already told you or what is obvious from context.** If they said "it runs once a week on a schedule," don't ask "is this interactive or batch." State the finding and move on.
- **Propose, discuss, revise.** Present the architecture concretely, name the LangChain/LangGraph/Deep Agents pieces it maps to, and explain each choice against the dimension that drove it. Invite pushback. Revise. This loop can run several times.
- **Gate on agreement, then build to the agreed scope.** Only after an explicit go-ahead, and after settling how far to build, write anything (Section D).

The number of questions is not the metric; whether each question changes the design is. A question whose answer wouldn't move any architectural choice is noise — skip it.

## C. The thin dimension checklist (compact list in SKILL.md; expanded here)

This is a list of **dimensions to ask about**, each paired with **the architectural decision it drives** and **which reference/section informs the current-API answer**. It is deliberately *not* a decision tree: it tells Claude what to make sure it has asked, not what to conclude. Claude's judgment does the mapping (`00` DC4/DC5). Author each as a principle (the "why" is the point), not a bare bullet.

1. **Task shape** — one-shot vs conversational vs long-running/autonomous, and how it's triggered (user, schedule, event). *Drives:* whether this is a single `create_agent` loop, a hand-built LangGraph graph, or a Deep Agent harness (planning + filesystem + subagents). *Informs from:* SKILL.md three-layer model; `deepagents.md` §1.
2. **Single vs multi-agent** — does the work decompose into distinct sub-tasks or roles? *Drives:* one agent vs subagents (synchronous/async/dynamic) vs the agent-as-tool coordinator pattern. Warn against the removed supervisor package. *Informs from:* `deepagents.md` subagent sections; `langchain-langgraph.md` agent-as-tool delta.
3. **External data & tools** — RAG over documents? live APIs? a database? code execution? *Drives:* the tool set, whether a sandbox/execute backend is needed, MCP integration, provider tool search. *Informs from:* `deepagents.md` backends/interpreters/sandboxes/MCP; `langchain-langgraph.md` `ProviderToolSearchMiddleware`.
4. **State & memory** — stateless, within-conversation memory, or cross-session long-term memory? *Drives:* checkpointer vs `store`, and specifically `StoreBackend(namespace=...)` to avoid cross-user leakage. *Informs from:* `deepagents.md` memory section.
5. **Human-in-the-loop** — does any action need human approval *before* it executes? *Drives:* `interrupt_on` + a checkpointer and the resume envelope; this is the line between an agent you can let run and one that must pause. *Informs from:* `deepagents.md` HITL section.
6. **Control & safety** — filesystem confinement, permissioned tools, tool-call limits, PII, untrusted input? *Drives:* `FilesystemBackend(virtual_mode=True)` (the default is *not* a sandbox), `FilesystemPermission` rules, `ToolCallLimitMiddleware`. *Informs from:* `deepagents.md` backend-security/permissions; `langchain-langgraph.md` tool-call-limit delta.
7. **Reliability** — model fallback, error compensation, retries, cost/latency ceilings? *Drives:* `ModelFallbackMiddleware` (not agent `.with_fallbacks()`), declarative `error_handler` vs retry policy. *Informs from:* `langchain-langgraph.md` fallback/error-handling deltas.
8. **Output shape** — free text or a structured object the caller consumes programmatically? *Drives:* `response_format` / structured output. *Informs from:* the model already handles this (excluded topic); confirm the current call shape against the references only if Deep Agents-specific.
9. **Deployment & runtime** — local script, a server, or a managed deployment; sync/async; streaming to a UI? *Drives:* Managed Deep Agents / LangSmith Deployments terminology, the `thread_id` vs `context` split, event streaming v3. *Informs from:* `deepagents.md` production section; `langchain-langgraph.md` streaming delta.
10. **Build scope** — code-only, runnable scaffolding, or a full project? *Drives:* what the build step actually produces; agreed per case, never assumed (`00` DC6).

The implementer should not expand this into more than these ~10 dimensions; the thinness is the point. Each is a prompt to *ask*, and the "drives/informs" clause exists so Claude reads the right reference section rather than guessing the current API.

## D. Build rules (the agreement gate) — goes in `references/consultant.md`, gist in SKILL.md

- **Design is always offered and free.** The consultant produces a concrete architecture and explanation with no side effects.
- **Implementation is gated on an explicit go-ahead.** Do not write files, edit files, install packages, or run commands until the user says to build.
- **Scope is agreed per build, not defaulted.** Before writing, settle whether the user wants just the agent code, a runnable scaffold (files + dependencies + how-to-run + a minimal example), or a full project. Offer the options; let them choose (`00` DC6).
- **Build against the current API.** Re-read the relevant reference immediately before writing code, and honor the cross-cutting corrections (`system_prompt=`, explicit `provider:model`, `create_agent`, real/future model IDs left intact).
- **Verify to the agreed scope.** If a runnable scaffold was agreed, make it actually importable/runnable (or state exactly what the user must supply — API keys, a store URL). Do not claim it runs if you did not exercise it; say what was and wasn't verified.

## E. `references/consultant.md` — file spec

A single new reference file, read on entry to the consultant path. Contents, in order:

1. **The persona, in full** (Section A expanded to a short paragraph each).
2. **The interview protocol** (Section B), including the divergent-open / convergent-AskUserQuestion rule and the "every question must move the design" test.
3. **The dimension checklist, expanded** (Section C) — each dimension a short paragraph with its driving decision and its reference pointer, written as a principle.
4. **The build rules** (Section D) — the agreement gate, per-case scope, build-against-current-API, and verify-to-scope.
5. **One worked example dialogue** (Section F below) — end to end, abstract goal → interview → proposal → agreement → scoped build. One is enough; do not pad with variants (progressive-disclosure: extra examples are read-cost with little added signal).

Keep it a reference, not a tutorial on LangChain. If a sentence teaches an API rather than a consulting move, it belongs in the delta references (or nowhere, if already known), not here.

## F. Worked example (author one like this in `references/consultant.md`)

A compact, realistic end-to-end trace. Suggested scenario (the implementer may pick another that exercises several dimensions):

> **User:** "I want something that reads our incoming support emails and drafts replies."
>
> **Consultant (divergent open):** clarifies the outcome and constraints in conversation — Where do the emails live (Gmail API, IMAP, a shared inbox export)? Should it *send* replies or only *draft* them? What makes a reply "good" — tone, a knowledge base to cite, escalation rules? Is there history it should remember per customer? Roughly what volume, and does a human review before send?
>
> **Consultant (convergent, AskUserQuestion over the checklist):** task shape (event-triggered per incoming email → not a one-shot script); single vs multi (one agent is enough — draft is a single job); external data (needs the inbox tool + a docs knowledge base → RAG tool; recommend reading `deepagents.md` backends/MCP and `langchain-langgraph.md` provider-tool-search before finalizing); state/memory (per-customer history → `StoreBackend` with a per-customer namespace); HITL (drafts only, human sends → but if they later want auto-send, that step needs `interrupt_on` + checkpointer); safety (untrusted email content → filesystem confinement if it writes attachments, tool-call limit); reliability (model fallback for provider outages); output (a draft string, maybe structured with a suggested-label); deployment (starts as a local script, could move to a managed deployment).
>
> **Consultant (proposal, grounded in the references it just read):** "A single Deep Agent: `create_deep_agent(model='anthropic:claude-sonnet-4-6', system_prompt=..., tools=[inbox_read, kb_search], store=<store>)`, a `StoreBackend` namespaced per customer for history, no `interrupt_on` yet because it only drafts, `ModelFallbackMiddleware` for resilience. If you later want it to send, we add `interrupt_on` for the send tool so a human approves first. Here's why each piece is there…" — mapping each choice back to the dimension that drove it.
>
> **User:** "Looks right. Build it — just the agent code for now, I'll wire up the inbox myself."
>
> **Consultant (scoped build):** agrees scope (agent code only, user supplies the inbox/store wiring), re-reads the Deep Agents reference, writes the agent with current APIs, and states exactly what the user must provide (the two tools, a store instance, credentials) — without claiming it runs end-to-end, since the inbox integration is the user's part.

The example's job is to show the *shape* — divergent open, convergent checklist, concrete proposal tied to dimensions, agreement gate, scoped build honest about what it did and didn't verify — not to be a template the model fills in mechanically.
