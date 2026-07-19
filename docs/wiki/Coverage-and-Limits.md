# Coverage and Limits

What this plugin knows, what it deliberately does not, and where its answers stop being reliable. Read this before you trust it on something that matters.

## The coverage model changed in v1.2.0

Through v1.1.0, coverage was **evidence-selected**: a topic was in the skill only if blind probes showed the model got it wrong. That produced a precise but narrow surface — 6 LangChain corrections, 4 LangGraph, 16 Deep Agents topics — and a real risk that anything outside those lists fell back to memory.

Since v1.2.0, coverage is **corpus-defined**. The plugin ships the full body of 187 official documentation pages and the skill searches them, so the question is no longer "which topics were selected" but "which pages are in the database." Selection was abandoned because it was measurably losing content — see [Home](Home.md) for the case that forced it.

So the honest statement of coverage is: **whatever the official Python documentation says, in the seven directories listed below, as of 2026-07-07.**

## What is in the corpus

| Package | Docs | What it covers |
|---|---|---|
| `langchain` | 73 | Agents, middleware, models, tools, structured output, streaming |
| `deepagents` | 53 | The harness: subagents, backends, memory, skills, permissions, sandboxes, deployment |
| `langgraph` | 42 | The runtime: graphs, persistence, interrupts, streaming, error handling |
| `reference` | 9 | API reference material |
| `concepts` | 4 | Cross-cutting conceptual pages |
| `migrate` | 3 | Migration guides |
| `releases` | 3 | Release notes and the changelog |
| **Total** | **187** | ~3.3 M characters, snippets inlined |

To see the exact list your copy has:

```bash
sqlite3 -readonly .claude/skills/langchain/references/docs_official.db \
  "SELECT package, path, title FROM docs ORDER BY package, path;"
```

## What is excluded, and why

**JavaScript and TypeScript documentation — entirely.** Not a coverage gap to be filled later; a deliberate exclusion. A Python-only skill whose database contains JavaScript is a skill that can retrieve JavaScript and present it as Python. The `:::js` conditional blocks inside otherwise-shared pages are stripped at build time for the same reason, and a validator asserts that none survived.

**`python/integrations` — 579 files.** A catalog of individual providers, vector stores, and connectors. It is roughly four times the size of everything included, and it is a parts list rather than design guidance. Excluding it keeps the shipped binary at 4.4 MB. If you need it, [Customization](Customization.md) explains how to add it back in a fork.

**Anything published after the snapshot date.** There is no background updater.

## The gotchas: the only hand-written knowledge left

A search over current documentation has one structural blind spot. It can show what exists; it cannot show what was **deleted**. There is no query for the absence of a page, and "no results" is indistinguishable from "wrong search terms."

So `SKILL.md` carries a short list of removed and renamed APIs the database can never correct:

| The model's reflex | What is actually current |
|---|---|
| `create_deep_agent(instructions=...)` | `system_prompt=` — `instructions=` raises `TypeError` |
| Subagent specs keyed on `prompt` | `system_prompt` |
| `create_react_agent`, `AgentExecutor`, `initialize_agent` | `from langchain.agents import create_agent` |
| Calling `.compile()` on the result | It already returns a compiled graph |
| The `supervisor` package | Removed — use subagents or agent-as-tool coordination |
| `.with_fallbacks()` on an agent | Model fallback is middleware |
| "Correcting" `claude-sonnet-4-6`, `claude-opus-4-8`, `gpt-5.5`, `gemini-3.5-flash` backward | These IDs are current and intentional — leave them alone |

That last row is a real measured failure mode: the model sees a version number higher than anything in its training data, concludes it is a typo, and helpfully edits working code into broken code.

## Limits

**Python only.** JavaScript and TypeScript are not in the corpus and were never measured.

**Point-in-time.** The snapshot is dated **2026-07-07**, from `langchain-ai/docs` at commit `c728061`. Anything released upstream after that is unverified. Check what your installed copy actually has:

```bash
sqlite3 -readonly .claude/skills/langchain/references/docs_official.db \
  "SELECT value FROM meta WHERE key='snapshot_date';"
```

**Version-sensitive, including preview material.** The database reproduces the official documentation as written — which includes beta, preview, private-preview, and version-gated APIs, sometimes without a prominent warning. Several capabilities the skill will happily use require a specific minimum package version. Verify against what you have actually installed.

**Documentation currency is not package currency.** The docs describing a feature and the released package implementing it can disagree. When your installed package rejects an API the skill suggested, the package wins.

**Not a package manager.** It does not install, pin, or resolve Python dependencies.

**Not a sandbox.** Guidance about backends, permissions, and confinement is guidance. `virtual_mode=True` constrains paths; it does not isolate a process. Nothing here defends an agent against prompt injection from the untrusted input it reads. See [SECURITY.md](../../SECURITY.md).

**Not a substitute for review.** Generated code is a draft. The plugin does not run it, test it, or judge whether your deployment is safe.

**One measured model.** The evidence baseline was Claude Opus 4.8 with a January-2026 knowledge cutoff. A different model has a different knowledge boundary, so the gotchas may be unnecessary for one model and insufficient for another.

**The consultant is not measurable the same way.** Whether an interview produced a good architecture is a judgment call, not a gradeable fact. It is validated by behavioral review rather than by scoring — see [Validation and Evidence](Validation-and-Evidence.md).

**Independent project.** Not affiliated with or endorsed by LangChain, Anthropic, or any other vendor named in this documentation.

## When to distrust it

- The transcript shows **no `sqlite3` query** before the code. The skill answered from memory.
- Your installed package **rejects** the suggested API. Compare the release date against `snapshot_date`.
- The topic is **JavaScript**, or a **specific integration provider**. Neither is in the corpus.
- The answer concerns **something announced recently**. The database does not know.
- The advice is about **safety**, and you were about to rely on it without reading the code.

---

**Next:** [The Knowledge Base](The-Knowledge-Base.md) for how the corpus is built, or [Customization](Customization.md) to change it.

Back to the [documentation index](README.md).
