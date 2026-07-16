# Troubleshooting

## `/plugin` or `claude plugin` is unavailable

Update Claude Code, restart it, and check the version:

```bash
claude --version
```

The v1.1.0 marketplace was validated with Claude Code 2.1.211. Older versions may not support current relative-path marketplace plugins or newer manifest fields.

## Marketplace validation fails

Run from the repository root:

```bash
claude plugin validate .claude-plugin/marketplace.json --strict
claude plugin validate plugins/skills-for-langchain/.claude-plugin/plugin.json --strict
```

Confirm that `.claude-plugin/marketplace.json` exists and that the marketplace, plugin, and skill identifiers are lowercase kebab-case where required.

## Plugin installation cannot find files

Use the GitHub repository shorthand:

```bash
claude plugin marketplace add tjdwls101010/Skills-for-Langchain
```

Do not add the raw `marketplace.json` URL. The catalog's relative `./plugins/skills-for-langchain` source is resolved inside the checked-out marketplace repository.

## Plugin is installed but the skill is missing

1. Restart Claude Code or run `/reload-plugins`.
2. Check `claude plugin list`.
3. Run `claude plugin details skills-for-langchain@skills-for-langchain` if available in your Claude Code version.
4. Invoke `/skills-for-langchain:langchain` explicitly.
5. Validate `.claude-plugin/marketplace.json` and `plugins/skills-for-langchain/.claude-plugin/plugin.json` separately with `--strict`.

## The skill does not trigger automatically

Try explicit invocation first. If explicit invocation works, the request may not match the skill description. For a code task, include the actual framework or constructor in the prompt, such as `deepagents`, `create_deep_agent`, `LangGraph`, or `create_agent`. For the consultant path, state the outcome as an agent-building goal ("build an agent that…", "automate…", "answer from these docs") rather than an open-ended question — the description triggers on goals, but a vague prompt with no build intent may not match.

Do not force the skill on unrelated raw provider SDK, CrewAI, AutoGen, or LlamaIndex tasks unless they are explicitly bridged through LangChain.

## The consultant writes code before I agree, or does not interview

Consultant behavior is advisory, not enforced — the skill leads Claude to interview and gate on agreement, but it is guidance a model follows, not a hard block. If it jumps ahead, say so ("interview me first" / "don't write anything yet"). If it never enters consultant mode on a genuine agent-building goal, invoke `/skills-for-langchain:langchain` explicitly and restate the goal.

## An old answer persists after updating

Published plugins use explicit SemVer as the cache key. Confirm that:

- The maintainer bumped `plugins/skills-for-langchain/.claude-plugin/plugin.json`.
- You refreshed the marketplace.
- You updated the plugin.
- You restarted Claude Code.

```bash
claude plugin marketplace update skills-for-langchain
claude plugin update skills-for-langchain@skills-for-langchain
```

## Local and installed copies conflict

`claude --plugin-dir /absolute/path/to/plugins/skills-for-langchain` takes precedence over an installed marketplace plugin with the same name for that session. Start it outside the repository root to avoid loading the project-local skill at the same time, and exit the local test session before evaluating the installed copy.

The repository also exposes the skill as project-local `.claude/` configuration. Avoid copying the same skill into additional user or project locations, which can produce duplicate trigger candidates.

## The installed package rejects an API from the skill

Check the installed `langchain`, `langgraph`, and `deepagents` versions. The skill contains version gates and preview APIs, but your environment may be older or newer than the April-2026 snapshot.

Prefer the actual package signature and current official docs when they disagree with the snapshot. Open a bug report with package versions and a minimal reproduction if the shipped guidance is wrong.

## A filesystem or sandbox example is unsafe

Stop before running it. `virtual_mode=True` provides path normalization and escape protection; it does not provide process isolation. Filesystem permissions do not automatically constrain custom tools, MCP tools, or every sandbox backend. Use a real isolation boundary appropriate to your threat model.

Report security-sensitive problems according to [SECURITY.md](../../SECURITY.md), not in a public issue.
