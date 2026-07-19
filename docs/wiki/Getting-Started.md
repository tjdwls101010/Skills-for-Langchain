# Getting Started

Install the plugin, confirm it is actually working, and know how to update or remove it.

## What you are installing

Three terms, because Claude Code distinguishes them:

- **Marketplace** — a catalog telling Claude Code where plugins live. This repository *is* the marketplace; `.claude-plugin/marketplace.json` is its manifest.
- **Plugin** — the distributable package, named `skills-for-langchain`, under `plugins/skills-for-langchain/`.
- **Skill** — the actual unit of behavior, named `langchain`, invocable as `/skills-for-langchain:langchain` once installed.

The skill is *model-invocable*, so you rarely type that command. It loads on its own when a conversation involves LangChain-ecosystem Python or an agent someone wants built.

Installing places three files on your machine: `SKILL.md`, `references/consultant.md`, and the 4.4 MB `references/docs_official.db`. No hooks, no MCP servers, no background processes — see [SECURITY.md](../../SECURITY.md).

## Prerequisites

- **Claude Code with plugin support.** The manifests are validated in CI against Claude Code 2.1.207.
- **`sqlite3` on your PATH**, with FTS5 compiled in. System builds on macOS and Linux normally have it. Verify:
  ```bash
  sqlite3 --version
  ```
  Without it the skill still loads but cannot query the database — the failure mode is covered in [Troubleshooting](Troubleshooting.md).
- **GitHub access**, since the marketplace is a git repository.

Check your Claude Code version:

```bash
claude --version
```

## Install

```bash
claude plugin marketplace add tjdwls101010/Skills-for-Langchain
claude plugin install skills-for-langchain@skills-for-langchain
```

Then restart Claude Code, or run:

```text
/reload-plugins
```

Use the GitHub repository shorthand, not a raw `marketplace.json` URL. The catalog points at a plugin by relative path (`./plugins/skills-for-langchain`), and a bare JSON URL brings none of the repository that path refers to.

## Pin to a release

An unpinned marketplace tracks the repository's default branch, so you receive changes as they land. To hold a fixed version, append a git tag when adding the marketplace:

```bash
claude plugin marketplace add tjdwls101010/Skills-for-Langchain@v1.1.0
claude plugin install skills-for-langchain@skills-for-langchain
```

Check the [releases page](https://github.com/tjdwls101010/Skills-for-Langchain/releases) for the tags that actually exist before pinning — the plugin version in `plugin.json` moves ahead of the tag list between releases, so the newest available tag may be older than the newest shipped version.

## Verify it works

List what is installed:

```bash
claude plugin list
```

Then run the real test. The point is not whether the answer looks plausible — it is **whether Claude consults the database before answering**. Ask for something it gets wrong from memory:

```text
Build a Deep Agent with two asynchronous specialists, and show how the
coordinator steers or cancels them. Use current APIs.
```

**A working installation looks like this:**

1. A `sqlite3 -readonly ... MATCH ...` command runs against `docs_official.db` *before* any code is written.
2. The result uses `create_deep_agent(system_prompt=...)` — not `instructions=`.
3. Async specialists are declared as `AsyncSubAgent` specifications passed through `subagents=[...]`, not hand-rolled `asyncio` orchestration.

If step 1 does not happen, the skill did not load, and nothing after it is trustworthy — go to [Troubleshooting](Troubleshooting.md).

To check the consultant path instead, state a goal with no code and no framework:

```text
I want something that answers customer questions from our PDF manuals.
```

It should interview you about the design — where the PDFs live, who asks, whether answers need citations — before proposing anything, and write no files until you agree.

## Know what snapshot you have

Every answer the plugin gives is bounded by the age of its database. Check it:

```bash
sqlite3 -readonly ~/.claude/plugins/*/skills-for-langchain/skills/langchain/references/docs_official.db \
  "SELECT key, value FROM meta;"
```

Adjust the path to wherever your Claude Code installation keeps plugins; `claude plugin list` will tell you. You should see a `snapshot_date`, the upstream `source_commit`, and a `doc_count`. Anything published upstream after that date is outside what this plugin knows.

## Update

```bash
claude plugin marketplace update skills-for-langchain
claude plugin update skills-for-langchain@skills-for-langchain
```

Restart Claude Code afterwards. Releases use explicit SemVer and the version in `plugin.json` is the cache key — if a maintainer changes content without bumping it, clients may keep serving the cached copy.

## Move a pinned installation

A marketplace added with a tag stays on that tag; ordinary update commands will not move it. Remove and re-add:

```bash
claude plugin marketplace remove skills-for-langchain
claude plugin marketplace add tjdwls101010/Skills-for-Langchain@v1.1.0
claude plugin install skills-for-langchain@skills-for-langchain
```

Substitute the tag you want from the [releases page](https://github.com/tjdwls101010/Skills-for-Langchain/releases). Dropping the `@tag` entirely returns you to tracking the default branch.

## Remove

```bash
claude plugin uninstall skills-for-langchain@skills-for-langchain
claude plugin marketplace remove skills-for-langchain
```

Removing a marketplace also removes the plugins installed from it.

## Run a local checkout

For development, or to try changes before publishing:

```bash
git clone https://github.com/tjdwls101010/Skills-for-Langchain.git
cd Skills-for-Langchain

python3 scripts/validate_docs_db.py
claude plugin validate .claude-plugin/marketplace.json --strict
claude plugin validate plugins/skills-for-langchain/.claude-plugin/plugin.json --strict

PLUGIN_DIR="$PWD/plugins/skills-for-langchain"
(cd "$(mktemp -d)" && claude --plugin-dir "$PLUGIN_DIR")
```

Starting that session from a temporary directory is deliberate. Run it inside the repository and this project's own `.claude/skills/langchain/` loads alongside the packaged plugin skill, and you can no longer tell which one answered. When both are present, `--plugin-dir` wins for that session — but the ambiguity is not worth the risk.

---

**Next:** [Use Cases](Use-Cases.md) for what to ask for, or [Troubleshooting](Troubleshooting.md) if verification failed.

Back to the [documentation index](README.md).
