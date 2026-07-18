<p align="center">
  <img src="assets/skills-for-langchain.png" alt="Skills for LangChain project artwork" width="420">
</p>

<h1 align="center">Skills for LangChain</h1>

<p align="center">
  An evidence-built Claude Code plugin that consults on building agents with LangChain, LangGraph, and Deep Agents — and keeps the Python on current APIs.
</p>

<p align="center">
  <a href="https://github.com/tjdwls101010/Skills-for-Langchain/releases"><img alt="GitHub release" src="https://img.shields.io/github/v/release/tjdwls101010/Skills-for-Langchain"></a>
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-blue.svg"></a>
  <a href="https://code.claude.com/docs/en/plugins"><img alt="Claude Code plugin" src="https://img.shields.io/badge/Claude_Code-plugin-D97757"></a>
  <a href="https://github.com/tjdwls101010/Skills-for-Langchain/actions/workflows/validate.yml"><img alt="Validation" src="https://github.com/tjdwls101010/Skills-for-Langchain/actions/workflows/validate.yml/badge.svg"></a>
</p>

LangChain's agent ecosystem moves quickly. A capable model can still produce code that looks convincing while using renamed parameters, retired constructors, guessed imports, or incomplete safety boundaries. Skills for LangChain gives Claude Code a compact, version-stamped correction layer built from measured failures instead of a generic documentation dump.

The plugin has **two behaviors over one shared knowledge base**:

- **Solutions consultant.** Describe an outcome — "build an agent that triages my support inbox", "automate this weekly report", "answer questions from these PDFs" — even with no framework named and no code shown, and Claude interviews you, proposes a concrete architecture grounded in the *current* API, and builds it only after you agree on the shape and scope.
- **Current-API guide.** When you are writing or reviewing existing LangChain-ecosystem code, the same skill silently supplies the measured post-cutoff corrections with no interview.

The consultant does not sell LangChain regardless of fit: when an agent is overkill or a different tool suits better, it says so.

> [!IMPORTANT]
> As of v1.2.0 the shared knowledge base is a searchable database of the current official docs (`references/docs_official.db`) that Claude queries before proposing or writing ecosystem code. It is a version-stamped snapshot (Python-only, includes preview or version-gated APIs); check `SELECT value FROM meta WHERE key='snapshot_date'` for its date and verify anything newer against the current official docs.

## Why this project exists

The project started from a simple premise: do not teach an agent everything—teach it what it actually gets wrong.

We compared an April-2026 LangChain documentation snapshot with 38 blind implementation probes. Topics the model already handled correctly were intentionally excluded. Topics that were partial, unknown, or confidently outdated became focused corrections with source references and failure-mode explanations.

| Plausible but wrong output | Correction carried by the plugin |
|---|---|
| `create_deep_agent(instructions=...)` | Use `system_prompt=...` |
| `create_supervisor(...).compile()` as the current multi-agent pattern | Use agents wrapped as tools under a coordinator `create_agent` |
| `FilesystemBackend(root_dir=...)` described as a sandbox | Use `virtual_mode=True` for path protection and a real sandbox backend for process isolation |
| `ModelRequest.override(system_prompt=...)` in new middleware | Prefer `@dynamic_prompt` or override `system_message` |
| Hand-rolled long-running subagent concurrency | Use first-class `AsyncSubAgent` specifications and task lifecycle tools |

## What it covers

| Area | Measured coverage |
|---|---|
| LangChain | 6 deltas: dynamic prompts, summarization parameters, agent-as-tool coordination, model fallback, tool-call limits, provider tool search |
| LangGraph | 4 deltas: event streaming v3, declarative error handling, interrupt refinements, `DeltaChannel` |
| Deep Agents | 16 topics spanning constructors, backends, memory, context engineering, sync/async/dynamic subagents, skills, HITL, permissions, rubrics, profiles, interpreters, sandboxes, MCP, and production |

The plugin deliberately does not repeat measured-correct areas such as basic `create_agent`, agent structured output, `ToolRuntime`, runtime context, the LangGraph functional API, `PIIMiddleware`, `ContextEditingMiddleware`, `LLMToolSelectorMiddleware`, `durability=`, and Postgres persistence.

See [Coverage and Limits](docs/wiki/Coverage-and-Limits.md) for the detailed boundary.

## Install

### From the Claude Code marketplace

Prerequisite: an up-to-date [Claude Code](https://code.claude.com/docs/en/overview) installation with plugin support.

```bash
claude plugin marketplace add tjdwls101010/Skills-for-Langchain
claude plugin install skills-for-langchain@skills-for-langchain
```

Restart Claude Code or run `/reload-plugins`, then invoke the skill explicitly if desired:

```text
/skills-for-langchain:langchain
```

The skill is model-invocable, so both a natural-language agent-building goal and a normal LangChain, LangGraph, or Deep Agents coding task can trigger it automatically — the first enters the consultant, the second gets silent current-API guidance.

### Pin the marketplace to a release

```bash
claude plugin marketplace add tjdwls101010/Skills-for-Langchain@v1.1.0
claude plugin install skills-for-langchain@skills-for-langchain
```

### Test a local checkout

```bash
git clone https://github.com/tjdwls101010/Skills-for-Langchain.git
cd Skills-for-Langchain
claude plugin validate .claude-plugin/marketplace.json --strict
claude plugin validate plugins/skills-for-langchain/.claude-plugin/plugin.json --strict

PLUGIN_DIR="$PWD/plugins/skills-for-langchain"
(cd "$(mktemp -d)" && claude --plugin-dir "$PLUGIN_DIR")
```

Detailed installation, update, and removal instructions are in [Getting Started](docs/wiki/Getting-Started.md).

## Use it

Ask Claude Code the way you normally would.

**Start from a goal, and it consults.** Describe the outcome and let it interview you before proposing:

```text
I want to build an agent that reads our incoming support emails and drafts replies.
```

It asks the questions that actually change the design (where the emails live, draft vs. send, per-customer memory, human review), then proposes a concrete current-API architecture and builds it only once you agree on the scope.

**Or hand it a concrete task, and it guides the code.** Examples:

```text
Build a Deep Agent with user-isolated long-term memory and a safely rooted filesystem.
```

```text
Add automatic summarization and model fallback to this LangChain agent using current APIs.
```

```text
Stream LangGraph v3 events, including messages, tool calls, and interrupts.
```

```text
Run two long-lived Deep Agent specialists concurrently and let the coordinator steer or cancel them.
```

The plugin supplies API corrections and architectural guardrails; it does not install Python dependencies, execute your application, or replace project-specific testing and security review.

## How it works

```text
request
  → skill description matches
  → short SKILL.md decides the branch:
      • agent-building goal → read consultant.md → interview → propose → build on agreement
      • existing code       → query docs_official.db for the APIs in play → apply gotchas
```

The implementation uses progressive disclosure:

```text
.claude/skills/langchain/
├── SKILL.md
└── references/
    ├── consultant.md        # read on the consult path: interview, checklist, build rules
    └── docs_official.db      # SQLite + FTS5: full body of the ~187 core docs, snippets inlined
```

`SKILL.md` stays short because it loads whenever the skill triggers; it carries the consultant gist, a forcing function ("you don't reliably know the current API — query the DB first"), a compact list of removed/renamed-API gotchas the DB can't surface, and the DB schema with example queries. The depth lives in the DB, which Claude searches with SQL, and in `consultant.md` for the interview process. The DB is rebuilt from `langchain-ai/docs` by `scripts/build_docs_db.py`. The public plugin lives under `plugins/skills-for-langchain/`; release validation requires its packaged skill bytes — including the `.db` — to match the canonical project skill exactly.

Read [How It Works](docs/wiki/How-It-Works.md) for the design rationale.

## Evidence and validation

The validation record is intentionally layered and should not be read as one identical-protocol 38/38 run.

- 38 baseline tasks established 27 included probe tasks and 11 measured-correct regression guards. C1 and C2 combine into one Deep Agents content topic, so the public coverage map contains 26 content topics.
- The strict generated-file suite produced 35/38 correct under the corrected baseline.
- The three residuals were repaired and rechecked with current-file Codex attempts, two independent official-doc graders per task, and a separate hash/consensus synthesis.
- Final recorded state: 27/27 included probe tasks correct and 11/11 exclusions preserved.
- Harness validation passed with zero errors and zero warnings in normal and strict modes.
- The v1.1.0 consultant behavior is validated by a five-scenario headless behavioral dry-run (consult EN+KO, deltas-only, near-miss, honest-fit), not by the probe suite — consult quality is a judgment call, honestly a lighter bar than "is this API current."

The probe record above is the historical basis for the correction knowledge. **v1.2.0** changed the knowledge substrate: the two hand-distilled delta references were replaced by `references/docs_official.db`, a searchable snapshot of the full official docs (with code snippets inlined) that Claude queries with SQL. The DB build is validated separately by `scripts/validate_docs_db.py` (schema, row counts, zero unresolved snippets, snippet-inlining regression, FTS hits); the residue that a search over current docs can't surface — removed and renamed APIs — survives as a compact gotchas list in `SKILL.md`.

Raw prompts, verdicts, hashes, and synthesis records live under [docs/plans/research](docs/plans/research/). The complete methodology is explained in [Validation and Evidence](docs/wiki/Validation-and-Evidence.md).

## Documentation

Choose a path based on what you want to do:

| Audience | Start here |
|---|---|
| Plugin user | [Getting Started](docs/wiki/Getting-Started.md) → [Use Cases](docs/wiki/Use-Cases.md) → [Troubleshooting](docs/wiki/Troubleshooting.md) |
| Customizer | [Coverage and Limits](docs/wiki/Coverage-and-Limits.md) → [How It Works](docs/wiki/How-It-Works.md) → [Customization](docs/wiki/Customization.md) |
| Maintainer | [Validation and Evidence](docs/wiki/Validation-and-Evidence.md) → [Maintenance and Release](docs/wiki/Maintenance-and-Release.md) → [Contributing](CONTRIBUTING.md) |

The canonical wiki source is [docs/wiki](docs/wiki/README.md). It is kept in the main repository so documentation changes can be reviewed alongside skill changes.

## Scope and limitations

- Python only; JavaScript and TypeScript APIs were not measured.
- Verified against a point-in-time April-2026 documentation snapshot, not against every future release.
- Some included APIs are beta, preview, private preview, or version-gated.
- The measured consumer baseline was Claude Opus 4.8 with a January-2026 knowledge cutoff. Blind attempts had no documentation or web access; results should not be generalized to every model or prompt distribution.
- Security guidance in the skill does not turn local filesystem access or code execution into a sandbox.
- This is an independent community project. It is not affiliated with or endorsed by LangChain, Anthropic, OpenAI, Google, or their respective product teams.

## Contributing

Contributions are welcome, especially when they include a reproducible outdated behavior, the current official source, and a focused correction that does not duplicate knowledge the model already handles.

Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request. Community participation is governed by the [Code of Conduct](CODE_OF_CONDUCT.md). Security-sensitive reports should follow [SECURITY.md](SECURITY.md); usage questions should follow [SUPPORT.md](SUPPORT.md).

## License and artwork

The software and documentation are licensed under the [MIT License](LICENSE).

The project artwork was supplied separately by the repository owner and is not granted under the MIT License by this repository. It contains third-party visual elements and marks; see [assets/README.md](assets/README.md) before reuse.

## Acknowledgements

This project builds on the public work and documentation of the LangChain, LangGraph, Deep Agents, and Claude Code communities. Product and company names are trademarks of their respective owners.
