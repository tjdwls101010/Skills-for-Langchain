# Support

## Start here

Most questions are answered in the wiki:

- [Getting Started](docs/wiki/Getting-Started.md) — installing, pinning, updating, removing.
- [Use Cases](docs/wiki/Use-Cases.md) — what to actually ask for, with prompts that work.
- [Troubleshooting](docs/wiki/Troubleshooting.md) — the skill not triggering, database failures, stale answers.

## The first thing to check

Two facts explain a large share of "the plugin gave me a wrong answer" reports. Collect both before filing anything:

```bash
# 1. Is the skill actually querying the database, or answering from memory?
#    Watch for a sqlite3 command in the transcript before Claude writes code.

# 2. How old is the database you are running against?
sqlite3 -readonly .claude/skills/langchain/references/docs_official.db \
  "SELECT value FROM meta WHERE key='snapshot_date';"
```

If no query ran, the skill did not load — that is a triggering problem, and [Troubleshooting](docs/wiki/Troubleshooting.md) covers it. If a query ran but the answer is stale, compare the snapshot date against when the API you expected was released; the plugin does not know about anything published after that date.

## Asking a question

Open a [GitHub issue](https://github.com/tjdwls101010/Skills-for-Langchain/issues/new/choose) with:

- Your Claude Code version and the installed plugin version.
- The database `snapshot_date` from the query above.
- Relevant Python package versions (`langchain`, `langgraph`, `deepagents`).
- The prompt you gave, with private data removed.
- What you expected and what you got.

## What is in scope

**In scope:** the plugin failing to trigger, the database being missing or unreadable, guidance that is outdated or wrong against current official documentation, the consultant skipping its interview or writing files before you agreed, installation and update problems.

**Out of scope:** general LangChain application debugging, questions about your own agent's business logic, and issues in LangChain, LangGraph, or Deep Agents themselves — those belong in their own repositories. The exception is when the problem traces back to guidance this plugin shipped, which makes it ours.

## Security

Do not report a vulnerability, or unsafe generated guidance, in a public issue. Follow [SECURITY.md](SECURITY.md).

## No service-level agreement

This is a community-maintained project with a single maintainer. Support is best-effort and response times are not guaranteed. If something is blocking you and you have a fix, a pull request will always move faster than an issue — see [CONTRIBUTING.md](CONTRIBUTING.md).
