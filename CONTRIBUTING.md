# Contributing

Thanks for helping keep Skills for LangChain accurate and honest.

This project is unusual, so it is worth two sentences before the process: there is no application here, no test suite, and no runtime. The product is a Claude Code skill whose substance is a **generated database of official documentation** — which means the highest-value contribution is usually evidence that the skill gave someone bad guidance, not a hand-written paragraph of API knowledge.

## What the project accepts

The architecture changed in v1.2.0, and so did what a useful contribution looks like. Curated API prose used to be the whole point; it is now the one thing that gets rejected, because hand-distillation is exactly the failure this project moved away from.

**Highly wanted**

- **A reproduction where the skill produced stale, wrong, or unsafe API guidance.** Include the prompt, what Claude produced, and the official documentation page that shows what is current. This is the single most useful issue you can file.
- **A removed or renamed API that the gotchas list is missing.** The gotchas in `SKILL.md` exist for one reason: a search over *current* documentation can show what exists but never what was deleted. If Claude reaches for something that no longer exists and the database cannot correct it, that belongs in the gotchas — with the evidence that it is genuinely gone.
- **Build-pipeline fixes** in `scripts/build_docs_db.py` — a snippet import that fails to resolve, a Mintlify fence shape that the colon-count stack mishandles, a corpus selection that misses or wrongly includes a directory.
- **Consultant-process improvements** in `references/consultant.md` — sharper interview questions, a dimension that turns out to be missing. Process, not API facts.
- **Documentation corrections**, especially anything in `docs/wiki/` that has drifted from what the code actually does.

**Not accepted**

- **Hand-written API explanations added to the skill.** If the answer is in the official documentation, it is already in the database; adding a distilled copy re-creates the drift that v1.2.0 deleted. If it is *not* in the database, the fix is to the corpus selection or a database refresh.
- **Tutorials, general LangChain teaching, or restating APIs the model already handles well.**
- **Undocumented or reverse-engineered behavior presented as fact.**
- **A rewrite of historical evidence.** The probe records under `docs/plans/research/` are a record of measurements that happened. Correct them only if the record itself is inaccurate, and then say so explicitly rather than quietly editing.

## Before you open an issue

- Search existing issues and read the [wiki](docs/wiki/README.md), particularly [Troubleshooting](docs/wiki/Troubleshooting.md).
- Check the snapshot date of the database you are running against — an "outdated" answer is often a database older than the API you are comparing to:
  ```bash
  sqlite3 -readonly .claude/skills/langchain/references/docs_official.db \
    "SELECT value FROM meta WHERE key='snapshot_date';"
  ```
- Confirm the behavior against your actually-installed package version, and check whether the API is beta, preview, or version-gated.
- Strip credentials, customer data, proprietary prompts, and private source from anything you paste.

## Development setup

No dependencies to install. The scripts are standard-library Python 3.10+; the validators need a `sqlite3` with FTS5 compiled in, which system CPython on macOS and Linux normally has.

```bash
git clone https://github.com/tjdwls101010/Skills-for-Langchain.git
cd Skills-for-Langchain

python3 scripts/validate_docs_db.py
python3 scripts/validate_evidence.py
claude plugin validate .claude-plugin/marketplace.json --strict
claude plugin validate plugins/skills-for-langchain/.claude-plugin/plugin.json --strict
```

To exercise your local copy in a real Claude Code session without installing it:

```bash
PLUGIN_DIR="$PWD/plugins/skills-for-langchain"
(cd "$(mktemp -d)" && claude --plugin-dir "$PLUGIN_DIR")
```

Running from a temporary directory matters — it keeps this repository's own `.claude/` out of the session, so you are testing the packaged plugin rather than the canonical source.

Rebuilding the database is only needed if you are changing the corpus or refreshing the snapshot; the procedure is in [Maintenance and Release](docs/wiki/Maintenance-and-Release.md).

## The rule that catches most contributors

**Every skill edit is a two-location edit.**

`.claude/skills/langchain/` is the canonical source. `plugins/skills-for-langchain/skills/langchain/` is the published copy, and `scripts/validate_evidence.py` compares every file in both trees by SHA-256 — including the 4.4 MB `docs_official.db`. Edit one and not the other and validation fails, by design, so the release copy cannot drift silently.

```bash
diff -rq .claude/skills/langchain plugins/skills-for-langchain/skills/langchain
```

## Making a change

1. Branch from `main`. Recent releases went through pull requests rather than direct pushes.
2. Edit the canonical files under `.claude/skills/langchain/`, then mirror them into `plugins/skills-for-langchain/skills/langchain/`.
3. Update `docs/wiki/` when behavior, installation, coverage, or limits change.
4. Add an entry under `[Unreleased]` in `CHANGELOG.md` for anything user-visible.
5. Run the checks below, and `git diff --check` for whitespace damage.

Recent commit subjects use a `type: summary` form (`feat:`, `docs:`, `chore:`) — check `git log` and match what is there.

**Markdown convention:** do not hard-wrap prose mid-sentence. One paragraph is one line. Hard wraps break exact-string edits and turn a two-word change into a twelve-line diff.

## Checks

```bash
python3 scripts/validate_docs_db.py
python3 scripts/validate_evidence.py
claude plugin validate .claude-plugin/marketplace.json --strict
claude plugin validate plugins/skills-for-langchain/.claude-plugin/plugin.json --strict
git diff --check
```

CI (`.github/workflows/validate.yml`) runs `validate_evidence.py`, both strict manifest validations, and a whitespace check on every push and pull request. Note that CI does **not** currently run `validate_docs_db.py` — if you touch the database or the build script, run it locally and say so in the pull request.

## Pull requests

Keep them small enough to actually review. In the description, cover:

- What was wrong, with a reproduction if the trigger was bad guidance.
- The official source supporting the fix.
- Why it belongs where you put it — the always-loaded `SKILL.md`, the consultant process, the build script, or the corpus.
- Which checks you ran, including any that CI does not cover.
- Whether it affects versioning, installation, or a documented limit.

The [pull request template](.github/PULL_REQUEST_TEMPLATE.md) carries this as a checklist.

By contributing, you agree your contribution is licensed under the project's [MIT License](LICENSE).

## Community standards

Be respectful and constructive. Participation is governed by [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). Report security issues privately per [SECURITY.md](SECURITY.md) rather than in a public issue.
