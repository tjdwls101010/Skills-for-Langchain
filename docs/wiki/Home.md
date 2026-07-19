# Home — what this project is

The full version of the README's "why this exists," for a reader deciding whether this belongs in their toolchain.

## The problem

A coding model's knowledge of a library is frozen at its training cutoff. For most libraries that is survivable — the API you learned two years ago mostly still works. The LangChain agent ecosystem is not most libraries. Between the measured baseline (Claude Opus 4.8, January 2026 cutoff) and the documentation snapshot this project ships (July 2026), constructors were renamed, an entire coordination package was removed, and the recommended way to do several ordinary things changed.

The dangerous part is not that the model is out of date. It is that **the model cannot tell.** Asked for a Deep Agent, it produces well-structured, idiomatic, confident Python built on `create_deep_agent(instructions=...)` — a parameter that no longer exists and raises `TypeError` on the first call. There is no hedge in the output, because from the model's side nothing is uncertain.

This was measured, not assumed. In July 2026, 38 implementation tasks were given to that model with no documentation and no web access, and a separate documentation-armed grader scored each answer. **All 14 Deep Agents tasks came back wrong or incomplete.** `instructions=` appeared in nine of them.

## What this project does about it

It is a [Claude Code plugin](https://code.claude.com/docs/en/plugins) containing a single skill. Installed, the skill triggers automatically whenever a conversation turns to LangChain, LangGraph, or Deep Agents — or whenever someone describes an agent they want built, in any words at all.

The skill's core instruction is a refusal to trust memory. Before it proposes an architecture or writes a line of ecosystem code, it queries a database of official documentation that ships inside the plugin, and treats what it reads there as ground truth over what it remembers.

## Two behaviors, one knowledge base

**Solutions consultant.** Given a goal rather than code — "automate this weekly report," "answer questions from these PDFs," "something that triages our inbox" — it runs an interview before it designs. It works through ten dimensions that each drive one architectural decision, asks about the ones you have not already settled, then proposes something concrete and named. It writes nothing until you say to, and agrees the scope of the build separately.

Critically, it is allowed to talk you out of it. A consultant who recommends the same product every time is not a consultant, and the skill is explicitly instructed to say when an agent is overkill and a plain script is the right answer.

**Current-API guide.** Given existing code, there is no interview at all. The skill silently looks up the APIs in play and corrects them. This was the entire v1.0.0 behavior and it is protected against regression.

The branch is decided in the first few lines of `SKILL.md`. See [How It Works](How-It-Works.md).

## Why a database instead of curated notes

The first two releases carried hand-distilled corrections: two reference files written by reading the official docs and extracting what the probes showed the model got wrong. It worked, and it had a defect that could not be engineered away.

**Distillation silently drops things.** The measured case: `deepagents/dynamic-subagents.mdx` is a 369-line official page containing more than ten orchestration patterns — tournament, loop, adversarial, fan-out — each with working code. The distilled reference compressed it to a single section heading. The code was gone, and nothing in the process would ever have flagged it, because a summary that loses content looks exactly like a summary that does not.

The second defect was cost: refreshing meant re-running blind probes and re-curating by hand, so it would not happen often enough.

Version 1.2.0 removed the distillation step entirely. The plugin now ships **the full body of 187 official documentation pages** in a SQLite database with full-text search, and Claude queries it with SQL. A database cannot pre-drop what it stores, and refreshing is one `git clone` and one build script.

What survives from the curated era is one short list, and its logic is worth understanding: **a search over current documentation can show you what exists, but never what was removed.** Absence is not searchable. So `SKILL.md` still carries roughly ten lines of gotchas covering removed and renamed APIs — the `supervisor` package that no longer exists, `create_react_agent` for `create_agent`, `.with_fallbacks()` where middleware is now correct. That is the only hand-written API knowledge left in the project, and it is there precisely because the database structurally cannot supply it.

See [The Knowledge Base](The-Knowledge-Base.md).

## Who it is for

- **Anyone writing LangChain-ecosystem Python with Claude Code**, who would rather not discover a renamed parameter at runtime.
- **People who know what they want but not how to build it** — the consultant path exists for goals stated in plain language, with no framework named.
- **Teams evaluating whether an agent is the right shape** for a problem at all, who want a straight answer rather than a sale.

## What it deliberately does not do

Non-goals define this project as sharply as its goals.

- **It does not teach LangChain.** It is not a tutorial, a course, or a replacement for reading the documentation. It is a lookup layer for a model that would otherwise guess.
- **It does not cover JavaScript or TypeScript.** Those docs are excluded from the corpus at build time, deliberately: indexing them invites emitting JavaScript as Python.
- **It does not track releases automatically.** The database is a stamped snapshot. There is no background updater.
- **It does not install packages, run your application, or test anything.** Verification of generated code is yours.
- **It does not enforce safety.** It steers toward `virtual_mode=True` over a bare `root_dir`, and toward human approval before irreversible actions — but a document cannot sandbox a process. See [SECURITY.md](../../SECURITY.md).
- **It does not restate what the model already gets right.** That was the founding discipline and it still holds, though its expression changed: v1.0.0 excluded correct topics from a curated file; v1.2.0 keeps the gotchas list short instead.

## Current state

Version **1.2.0**. The database snapshot is dated **2026-07-07**, built from `langchain-ai/docs` at commit `c728061`.

The project is stable in the sense that its shape has settled and its validators pass on every push. It is maintained by one person, best-effort — see [SUPPORT.md](../../SUPPORT.md) for what that means in practice.

---

**Next:** [Getting Started](Getting-Started.md) to install it, or [How It Works](How-It-Works.md) for the architecture.

Back to the [documentation index](README.md) · [project README](../../README.md).
