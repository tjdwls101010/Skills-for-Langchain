# Troubleshooting

Symptoms mapped to fixes. Start with the first entry — it diagnoses more problems than the rest combined.

## Claude answered without querying the database

**This is the symptom that matters most.** Every current-API guarantee this plugin makes depends on one thing: a `sqlite3` query running before Claude writes code. If no query ran, the answer came from the model's memory, and its memory predates the APIs this plugin exists to correct — regardless of how confident the output looks.

Check the transcript for a command shaped like:

```bash
sqlite3 -readonly .../references/docs_official.db "SELECT ... docs_fts MATCH ..."
```

If it is absent, work down this list:

1. **Did the skill load at all?** Force it and retry: `/skills-for-langchain:langchain`. If forcing works, this is a triggering problem — see below.
2. **Is `sqlite3` available?** Run `sqlite3 --version`. Without it the skill loads, tries to query, fails, and may fall back to answering anyway.
3. **Does the local SQLite have FTS5?**
   ```bash
   sqlite3 :memory: "PRAGMA compile_options;" | grep FTS5
   ```
   No output means `MATCH` queries error out. System CPython builds on macOS and Linux normally include it; some minimal container images do not.
4. **Just ask.** "Query the plugin's docs database before answering." A single successful query usually re-establishes the pattern for the rest of the session.

## The skill does not trigger automatically

Try `/skills-for-langchain:langchain` first. If explicit invocation works, the skill is installed correctly and your request simply did not match its description.

- **For code work**, name the thing: `deepagents`, `create_deep_agent`, `LangGraph`, `create_agent`, "middleware", "subagent".
- **For the consultant path**, state a goal with build intent — "build something that…", "automate…", "answer questions from…". An open-ended question about agents in general may not match; a described outcome will.

It should **not** trigger on CrewAI, AutoGen, LlamaIndex, or raw OpenAI/Anthropic SDK work. That boundary is deliberate — do not force it there.

## The consultant wrote code before I agreed, or never interviewed

The agreement gate is designed behavior the model follows, not a hard block. The plugin deliberately declares no pre-approved Write or Edit permissions, but nothing mechanically stops Claude from getting ahead of itself.

- **It jumped to code:** say so directly — "don't write anything yet, interview me first." It will back up.
- **It never entered consultant mode:** invoke the skill explicitly and restate the goal as an outcome rather than a question.
- **It proposed without asking anything:** ask it to walk its dimension checklist. It should be asking about task shape, data, memory, human approval, safety, reliability, output shape, and deployment.

## The answer is stale or the API does not exist

Two different causes, and the database tells you which.

```bash
sqlite3 -readonly .claude/skills/langchain/references/docs_official.db \
  "SELECT value FROM meta WHERE key='snapshot_date';"
```

**If the API you expected is newer than that date**, the plugin does not know about it, and no amount of prompting will help. Either refresh the database ([Maintenance and Release](Maintenance-and-Release.md)) or give Claude the current documentation directly.

**If the API is older than that date** but Claude still got it wrong, the search probably missed. FTS5 `MATCH` has sharp edges — a token with a hyphen or heavy underscores can parse as an operator rather than a term. Ask it to search again with different words, or check the page exists at all:

```bash
sqlite3 -readonly .claude/skills/langchain/references/docs_official.db \
  "SELECT path, title FROM docs WHERE body LIKE '%your_api_name%' LIMIT 10;"
```

If the page is there and Claude still missed it, that is worth an issue — see [SUPPORT.md](../../SUPPORT.md).

## My installed package rejects an API the skill suggested

The package wins. Always.

Check what you actually have installed, and compare its release date against the snapshot date. Three things can be true:

- **Your package is older than the docs.** The API exists but you cannot use it yet. Pin or upgrade deliberately.
- **Your package is newer.** The API moved after the snapshot. Trust your package.
- **The API is preview or version-gated.** The database reproduces the official docs as written, including beta and private-preview material, sometimes without a prominent warning.

If the shipped guidance was simply wrong against current official documentation, file a bug with package versions and a minimal reproduction.

## The database file is missing or unreadable

```bash
claude plugin list        # find the plugin's install path
```

Then confirm the file is there and is a real database:

```bash
sqlite3 -readonly <path>/references/docs_official.db "SELECT count(*) FROM docs;"
```

Expect 187. A file smaller than about 4 MB, or an error like "file is not a database," means a truncated download — reinstall:

```bash
claude plugin uninstall skills-for-langchain@skills-for-langchain
claude plugin marketplace update skills-for-langchain
claude plugin install skills-for-langchain@skills-for-langchain
```

If you cloned the repository yourself and the file is a few hundred bytes of text beginning with `version https://git-lfs`, you have an LFS pointer rather than the binary — this repository does not use LFS, so that indicates a mirror or proxy that does.

## An old answer persists after updating

The version in `plugin.json` is the cache key. Confirm all four:

- The maintainer bumped the version. Content changes without a bump do not propagate.
- You refreshed the marketplace.
- You updated the plugin.
- You restarted Claude Code.

```bash
claude plugin marketplace update skills-for-langchain
claude plugin update skills-for-langchain@skills-for-langchain
```

If you pinned the marketplace to a tag, updates will not move you — see [Getting Started](Getting-Started.md).

## Local and installed copies conflict

`claude --plugin-dir <path>` takes precedence over an installed plugin of the same name for that session.

The trap is running it **inside this repository**, where `.claude/skills/langchain/` also loads and you can no longer tell which copy answered. Always start local-plugin sessions from a temporary directory:

```bash
PLUGIN_DIR="$PWD/plugins/skills-for-langchain"
(cd "$(mktemp -d)" && claude --plugin-dir "$PLUGIN_DIR")
```

Exit that session before evaluating the installed copy, and avoid copying the skill into additional user or project locations — duplicate trigger candidates produce confusing results.

## `claude plugin` is unavailable

Update Claude Code and check the version:

```bash
claude --version
```

The manifests are validated in CI against Claude Code 2.1.207. Older releases may not support relative-path marketplace sources.

## Marketplace validation fails

```bash
claude plugin validate .claude-plugin/marketplace.json --strict
claude plugin validate plugins/skills-for-langchain/.claude-plugin/plugin.json --strict
```

Confirm you are at the repository root, that `.claude-plugin/marketplace.json` exists, and that identifiers are lowercase kebab-case where required.

## Installation cannot find files

Use the repository shorthand, not a raw JSON URL:

```bash
claude plugin marketplace add tjdwls101010/Skills-for-Langchain
```

The catalog's `./plugins/skills-for-langchain` source is resolved inside the checked-out marketplace repository. A bare `marketplace.json` URL brings none of it.

## Installed, but the skill is missing

1. Restart Claude Code, or `/reload-plugins`.
2. `claude plugin list`.
3. `claude plugin details skills-for-langchain@skills-for-langchain`, if your version supports it.
4. Invoke `/skills-for-langchain:langchain` explicitly.
5. Validate both manifests with `--strict`.

## A filesystem or sandbox example looks unsafe

**Stop before running it.**

`virtual_mode=True` gives path normalization and escape protection. It does **not** give process isolation — a tool that executes code is not contained by it. Filesystem permission rules do not automatically constrain custom tools, MCP tools, or every sandbox backend. And nothing in this plugin defends an agent against prompt injection arriving through the content it reads.

Use an isolation boundary appropriate to your actual threat model, and read [SECURITY.md](../../SECURITY.md).

Report unsafe generated guidance **privately**, not in a public issue — guidance wrong about safety reaches every user of the plugin.

---

**Next:** [Getting Started](Getting-Started.md) to reinstall cleanly, or [SUPPORT.md](../../SUPPORT.md) to file something.

Back to the [documentation index](README.md).
