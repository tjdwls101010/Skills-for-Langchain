# Security Policy

## Supported versions

Security fixes are provided for the latest published release.

| Version | Supported |
|---|---|
| 1.x | Yes |
| < 1.0 | No |

## Reporting a vulnerability

**Do not open a public issue** for anything that could put users at risk.

Use [GitHub private vulnerability reporting](https://github.com/tjdwls101010/Skills-for-Langchain/security/advisories/new). If that channel is unavailable to you, email `chunghun1@naver.com` with the subject `Skills for LangChain security report`.

Include:

- The affected version — the plugin version, and the database `snapshot_date` if the issue involves shipped guidance.
- Impact: what an attacker gains, and who is exposed.
- Reproduction steps, ideally the exact prompt and the resulting output.
- Any mitigation you have already identified.

Expect acknowledgement within 7 days and a status update within 14 days. Time to a fix depends on severity and on whether the root cause is in this repository or upstream. Please give a reasonable window for coordinated disclosure before publishing.

## What this plugin actually does on your machine

Worth being precise, because "a plugin that ships a 4.4 MB binary" deserves a straight answer.

**What is installed.** Three files: `SKILL.md`, `references/consultant.md`, and `references/docs_official.db`. Nothing else. The plugin declares **no hooks, no MCP servers, no executable commands, no background processes, and no dependency installation**. The validation scripts under `scripts/` are repository maintenance tooling; they are not part of the plugin and never run on a user's machine.

**What the binary is.** `docs_official.db` is a SQLite database containing the text of public LangChain documentation. It is data, not code — SQLite does not execute stored content. It is built by `scripts/build_docs_db.py` (standard library only, no network at build time) from a `git clone` of the public [`langchain-ai/docs`](https://github.com/langchain-ai/docs) repository, and the exact source commit is stamped inside it. You can inspect everything it contains:

```bash
sqlite3 -readonly references/docs_official.db "SELECT key, value FROM meta;"
sqlite3 -readonly references/docs_official.db "SELECT path, title FROM docs ORDER BY path;"
```

**What the skill causes Claude to do.** When the skill is active, Claude runs local `sqlite3 -readonly` queries against that file. Those queries are local and read-only, and the skill makes no network requests of its own.

## The boundary this project cannot enforce

The skill discusses filesystem confinement, sandboxes, permissioned tools, code execution, and credentials, and it will steer generated code toward the safer option — `virtual_mode=True` rather than a bare `root_dir`, a namespaced store rather than a shared one, human approval before an irreversible action.

**Documentation cannot enforce any of that.** A skill influences what Claude writes; it does not isolate a process, sandbox a filesystem, or contain an untrusted input. Agents that read email, browse the web, or execute code are exposed to prompt injection regardless of what this plugin advises.

You remain responsible for reviewing generated code before running it, pinning your own dependency versions, protecting secrets, granting least privilege, and testing in the environment you will actually deploy to.

## Reporting bad guidance

If the skill produced code that is insecure rather than merely outdated — a confinement that does not confine, a credential handling pattern that leaks — treat it as a security report and use the private channel above, not a public issue. Guidance that is wrong about *safety* reaches every user of the plugin.
