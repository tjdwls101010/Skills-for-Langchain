# Getting Started

## What you are installing

Three terms are involved:

- **Marketplace:** a catalog that tells Claude Code where this plugin lives.
- **Plugin:** the distributable package named `skills-for-langchain`.
- **Skill:** the background knowledge unit named `langchain`, invoked as `/skills-for-langchain:langchain` after marketplace installation.

The repository root is the marketplace root. The distributable plugin lives under `plugins/skills-for-langchain/`, while `.claude/skills/langchain/` remains the canonical project-harness source. Release validation enforces byte-for-byte equality between the canonical and packaged skill files.

## Prerequisites

- A current Claude Code release with plugin support. The v1.0.0 manifest was validated with Claude Code 2.1.207.
- Git access to GitHub.
- A trusted environment. Claude Code plugins are high-trust extensions even when, like this one, they contain only knowledge files.

Check your version:

```bash
claude --version
```

## Install from GitHub

Add the repository as a marketplace, then install the plugin:

```bash
claude plugin marketplace add tjdwls101010/Skills-for-Langchain
claude plugin install skills-for-langchain@skills-for-langchain
```

Restart Claude Code or run:

```text
/reload-plugins
```

The primary installation path uses the GitHub repository shorthand. Do not add the raw `marketplace.json` URL: the catalog uses a relative plugin source, and a raw JSON URL does not include the rest of the repository.

## Pin to a stable release

To pin the marketplace checkout to v1.0.0:

```bash
claude plugin marketplace add tjdwls101010/Skills-for-Langchain@v1.0.0
claude plugin install skills-for-langchain@skills-for-langchain
```

## Verify installation

List installed plugins:

```bash
claude plugin list
```

Inside Claude Code, explicitly load the skill once:

```text
/skills-for-langchain:langchain
```

Then try a task whose answer depends on a measured delta:

```text
Build a Deep Agent with two asynchronous specialists and show how the coordinator steers or cancels them.
```

A current answer should use `AsyncSubAgent` specifications through `create_deep_agent(subagents=[...])`, automatic async-subagent middleware, and the current task lifecycle tools rather than hand-rolled `asyncio` orchestration.

## Update an unpinned installation

Refresh the marketplace and update the plugin:

```bash
claude plugin marketplace update skills-for-langchain
claude plugin update skills-for-langchain@skills-for-langchain
```

Restart Claude Code after an update. Published releases use explicit SemVer, so maintainers must bump `plugins/skills-for-langchain/.claude-plugin/plugin.json` before users receive a new cached version.

## Move a pinned installation to a newer release

A marketplace added with `@v1.0.0` stays pinned to that tag. Ordinary marketplace and plugin update commands cannot move it to a different tag. Remove the pinned marketplace, add the desired release ref, and reinstall:

```bash
claude plugin marketplace remove skills-for-langchain
claude plugin marketplace add tjdwls101010/Skills-for-Langchain@v1.1.0
claude plugin install skills-for-langchain@skills-for-langchain
```

## Remove

```bash
claude plugin uninstall skills-for-langchain@skills-for-langchain
claude plugin marketplace remove skills-for-langchain
```

Removing a marketplace also removes plugins installed from it. Export or preserve any unrelated local configuration before changing marketplace state.

## Local development

```bash
git clone https://github.com/tjdwls101010/Skills-for-Langchain.git
cd Skills-for-Langchain
claude plugin validate .claude-plugin/marketplace.json --strict
claude plugin validate plugins/skills-for-langchain/.claude-plugin/plugin.json --strict

PLUGIN_DIR="$PWD/plugins/skills-for-langchain"
(cd "$(mktemp -d)" && claude --plugin-dir "$PLUGIN_DIR")
```

Starting the local-plugin session from a temporary directory prevents the project-local `.claude/skills/langchain` copy from loading alongside the namespaced plugin skill. When a locally loaded plugin has the same name as the installed marketplace plugin, `--plugin-dir` takes precedence for that session.

Next: [Use Cases](Use-Cases.md) or [Troubleshooting](Troubleshooting.md).
