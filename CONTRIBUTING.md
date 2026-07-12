# Contributing

Thank you for helping keep Skills for LangChain accurate, focused, and useful.

## What belongs in this project

The skill carries measured deltas: current Python API knowledge that a capable coding model gets wrong, only partially knows, or does not know. A contribution is strongest when it includes all three of the following:

1. A reproducible task or code sample showing the outdated behavior.
2. A current official LangChain, LangGraph, Deep Agents, or Claude Code source.
3. A focused correction that explains the reason or failure mode rather than merely replacing one token with another.

Avoid adding broad tutorials, restating stable APIs the model already handles, speculative abstractions, or undocumented behavior presented as fact.

## Before opening an issue

- Search existing issues and the [wiki](docs/wiki/README.md).
- Confirm the behavior against the relevant installed package version.
- Check whether the API is preview, beta, private preview, or version-gated.
- Remove credentials, proprietary prompts, customer data, and private source code from reproductions.

## Development setup

```bash
git clone https://github.com/tjdwls101010/Skills-for-Langchain.git
cd Skills-for-Langchain
claude plugin validate .claude-plugin/marketplace.json --strict
claude plugin validate plugins/skills-for-langchain/.claude-plugin/plugin.json --strict
python3 scripts/validate_evidence.py
```

You can load the local plugin without installing it:

```bash
PLUGIN_DIR="$PWD/plugins/skills-for-langchain"
(cd "$(mktemp -d)" && claude --plugin-dir "$PLUGIN_DIR")
```

## Making a change

1. Create a focused branch from `main`.
2. Update the canonical files under `.claude/skills/langchain/`.
3. Update the corresponding plan or evidence record when the measured content boundary changes.
4. Update user documentation when installation, behavior, coverage, or limitations change.
5. Add an entry under `[Unreleased]` in `CHANGELOG.md` for user-visible changes.
6. Run all validation commands and inspect `git diff --check`.

Edit `.claude/skills/langchain/` as the canonical source, then mirror the same files under `plugins/skills-for-langchain/skills/langchain/`. `scripts/validate_evidence.py` enforces byte-for-byte equality so the release copy cannot drift silently.

## Validation expectations

At minimum, run:

```bash
claude plugin validate .claude-plugin/marketplace.json --strict
claude plugin validate plugins/skills-for-langchain/.claude-plugin/plugin.json --strict
python3 scripts/validate_evidence.py
git diff --check
```

If API guidance changes, also verify the claim against official documentation and add or update a probe that demonstrates the delta. Do not rewrite historical evidence to make a new result look cleaner; append a clearly labeled new run or repair record.

## Pull requests

Keep pull requests small enough to review. Explain:

- What outdated behavior is being corrected.
- Which official source supports the correction.
- Why the change belongs in the always-loaded skill body or one of the two references.
- What validation was run.
- Whether the change affects plugin versioning, installation, or documented limitations.

By contributing, you agree that your contribution is licensed under the project's MIT License.

## Community standards

Be respectful and constructive. All participation is governed by [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). Report security issues privately according to [SECURITY.md](SECURITY.md).
