<p align="center">
  <img src="assets/skills-for-langchain.png" alt="Skills for LangChain project artwork" width="420">
</p>

<h1 align="center">Skills for LangChain</h1>

<p align="center">
  A Claude Code plugin that consults on your agent design — and looks the current LangChain API up instead of remembering it.
</p>

<p align="center">
  <a href="https://github.com/tjdwls101010/Skills-for-Langchain/releases"><img alt="GitHub release" src="https://img.shields.io/github/v/release/tjdwls101010/Skills-for-Langchain"></a>
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-blue.svg"></a>
  <a href="https://code.claude.com/docs/en/plugins"><img alt="Claude Code plugin" src="https://img.shields.io/badge/Claude_Code-plugin-D97757"></a>
  <a href="https://github.com/tjdwls101010/Skills-for-Langchain/actions/workflows/validate.yml"><img alt="Validation" src="https://github.com/tjdwls101010/Skills-for-Langchain/actions/workflows/validate.yml/badge.svg"></a>
</p>

## Why this exists

LangChain's agent stack moves faster than any model's training data. Ask a capable coding model to build a Deep Agent and it will hand you `create_deep_agent(instructions=...)` — confident, well-structured, and a `TypeError` on the first run. The parameter was renamed. The model has no way to know that, and no way to know that it doesn't know.

This project began by measuring that gap instead of guessing at it. In July 2026, 38 implementation tasks were put to Claude Opus 4.8 with no documentation and no web access, and a separate documentation-armed grader scored every answer against the official docs. All 14 Deep Agents tasks came back wrong or incomplete. `instructions=` appeared in nine of them.

Version 1.0.0 shipped hand-curated corrections for exactly those measured failures. **Version 1.2.0 replaced that with something blunter and more reliable.** Curation was measurably losing content: a 369-line official page on subagent orchestration had been compressed to a single heading, and its ten code samples were simply gone. So the plugin now ships the **full body of 187 official documentation pages** as a searchable SQLite database, and the skill queries it with SQL before it proposes an architecture or writes a line of code.

The measured failures are still why this project exists. The database is how it now delivers.

## What you get

Installing the plugin adds one skill to Claude Code that behaves two different ways depending on what you bring it.

**Describe an outcome, and it consults.** "Build something that reads our support inbox and drafts replies." No framework named, no code shown. It interviews you about the things that actually change the design — where the data lives, whether a human approves before anything is sent, whether memory is per-user — then proposes a concrete architecture on current APIs, and builds only after you agree, to a scope you agree. It will also tell you when an agent is the wrong answer and a plain script would do.

**Hand it existing code, and it just fixes the API.** Writing, editing, or reviewing LangChain, LangGraph, or Deep Agents Python triggers no interview at all. The skill silently looks up the APIs in play and corrects them.

Both behaviors read from the same database. Neither trusts the model's memory.

## Quick start

Requires an up-to-date [Claude Code](https://code.claude.com/docs/en/overview) with plugin support.

```bash
claude plugin marketplace add tjdwls101010/Skills-for-Langchain
claude plugin install skills-for-langchain@skills-for-langchain
```

Restart Claude Code, or run `/reload-plugins`. Then ask for something the model reliably gets wrong on its own:

```text
Build a Deep Agent with a system prompt, one tool, and a filesystem backend
that is actually confined. Use current APIs.
```

Claude should run a `sqlite3` query against the plugin's database *before* writing any code, and the result should use `create_deep_agent(system_prompt=...)` with `virtual_mode=True` — not `instructions=`, and not a bare `root_dir` presented as a sandbox. **If it queries the database first, the plugin is working.**

Full installation, pinning, update, and removal instructions are in [Getting Started](docs/wiki/Getting-Started.md).

## How it knows

```text
your request
  └─ the skill description matches
       └─ SKILL.md loads and picks a branch
            ├─ an outcome to build → read consultant.md → interview → propose → build on agreement
            └─ existing code       → query docs_official.db for the APIs in play
```

The shipped skill is three files:

```text
.claude/skills/langchain/
├── SKILL.md                    # always loaded: the branch, the forcing function,
│                               # removed-API gotchas, the DB schema and queries
└── references/
    ├── consultant.md           # read only on the consult path: the interview process
    └── docs_official.db        # 4.4 MB SQLite + FTS5: 187 official docs, full text
```

`SKILL.md` stays short because it loads every time the skill triggers. It carries the three things the database cannot supply on its own: a forcing function telling the model it does *not* reliably know the current API, a compact list of **removed and renamed** APIs — a search over current documentation can only show what exists, never what was deleted — and the schema and worked queries that make "Claude writes the SQL" actually work.

See [How It Works](docs/wiki/How-It-Works.md) for the architecture, and [The Knowledge Base](docs/wiki/The-Knowledge-Base.md) for what is in the database and how it is built.

## What is in the database

A version-stamped snapshot of [`langchain-ai/docs`](https://github.com/langchain-ai/docs), taken at commit `c728061`, snapshot date **2026-07-07**.

| Package | Docs |
|---|---|
| `langchain` | 73 |
| `deepagents` | 53 |
| `langgraph` | 42 |
| `reference` | 9 |
| `concepts` | 4 |
| `migrate` | 3 |
| `releases` | 3 |
| **Total** | **187** |

Every `/snippets/...` code sample is inlined into the document body, so the code that official pages import rather than contain is present and searchable. JavaScript documentation and the 579-file integrations catalog are excluded at build time: this is a Python-only skill, and indexing JavaScript risks emitting it as Python.

Check the snapshot date of your installed copy at any time:

```bash
sqlite3 -readonly .claude/skills/langchain/references/docs_official.db \
  "SELECT key, value FROM meta;"
```

Anything released after that date is unverified by this plugin. See [Coverage and Limits](docs/wiki/Coverage-and-Limits.md).

## Documentation

| If you want to | Start here |
|---|---|
| Install it and get results | [Getting Started](docs/wiki/Getting-Started.md) → [Use Cases](docs/wiki/Use-Cases.md) → [Troubleshooting](docs/wiki/Troubleshooting.md) |
| Understand or fork it | [How It Works](docs/wiki/How-It-Works.md) → [The Knowledge Base](docs/wiki/The-Knowledge-Base.md) → [Customization](docs/wiki/Customization.md) |
| Maintain or release it | [Validation and Evidence](docs/wiki/Validation-and-Evidence.md) → [Maintenance and Release](docs/wiki/Maintenance-and-Release.md) → [Contributing](CONTRIBUTING.md) |

The full documentation set lives in [docs/wiki](docs/wiki/README.md), inside this repository, so documentation changes are reviewed alongside the changes they describe.

## Limits worth knowing before you install

- **Python only.** JavaScript and TypeScript APIs are not in the database and were never measured.
- **A snapshot, not a live feed.** Currency is bounded by `meta.snapshot_date`. Refreshing is one clone and one build script, but it is a manual step.
- **Some documented APIs are preview or version-gated.** The database carries the official documentation as written, including its beta and private-preview material.
- **Guidance is not enforcement.** The skill discusses sandboxes, permissions, and confinement, but documentation cannot isolate a process. Review generated code before running it.
- **One measured model.** The baseline was Claude Opus 4.8 with a January-2026 knowledge cutoff. Results do not automatically generalize to other models.
- **Independent project.** Not affiliated with or endorsed by LangChain, Anthropic, or any other vendor named here.

## Contributing

Contributions are welcome. The most valuable one is a reproducible case where the skill produced stale or wrong API guidance, together with the official source showing what is current. [CONTRIBUTING.md](CONTRIBUTING.md) explains what the current architecture actually accepts as a change — it is different from what v1.0.0 accepted.

Participation is governed by the [Code of Conduct](CODE_OF_CONDUCT.md). Report security issues privately per [SECURITY.md](SECURITY.md); usage questions belong in [SUPPORT.md](SUPPORT.md).

## License and artwork

Software and documentation are under the [MIT License](LICENSE).

The project artwork in `assets/` was supplied separately by the repository owner and is **not** covered by the MIT License. It contains third-party visual elements and marks — read [assets/README.md](assets/README.md) before reusing it.

## Acknowledgements

This project is built on the public documentation of the LangChain, LangGraph, and Deep Agents projects, and on the Claude Code plugin system. Product and company names are trademarks of their respective owners.
