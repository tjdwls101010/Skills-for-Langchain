# Maintenance and Release

## Refreshing the knowledge baseline

1. Fetch a new official Python documentation snapshot for LangChain, LangGraph, and Deep Agents.
2. Record source provenance, file count, byte count, and an aggregate digest.
3. Re-run the documentation novelty survey.
4. Re-run both blind probe task sets against the intended consumer model.
5. Cross the doc-side and model-side results.
6. Update only the corrections that remain useful.
7. Re-run included tasks and measured-correct regression guards with the generated files.
8. Update verification stamps, evidence records, wiki coverage, and the changelog.

Do not silently replace the old snapshot or old verdicts. A new snapshot is a new evidence baseline.

## Content review checklist

- Every section names the plausible wrong prior.
- Every current API claim has an official source.
- Imports and constructor parameters are verified, not inferred.
- Version gates, preview status, defaults, and exceptions are explicit.
- Security boundaries distinguish path protection, permissions, sandboxes, and remote execution.
- Measured-correct topics remain absent unless new evidence changes the classification.
- `SKILL.md` remains short enough that cross-cutting corrections are visible.

## Plugin release checklist

1. Choose the SemVer impact.
2. Update only `plugins/skills-for-langchain/.claude-plugin/plugin.json` as the plugin version authority.
3. Update `CHANGELOG.md` and release-facing documentation.
4. Run:

   ```bash
   claude plugin validate .claude-plugin/marketplace.json --strict
   claude plugin validate plugins/skills-for-langchain/.claude-plugin/plugin.json --strict
   python3 scripts/validate_evidence.py
   git diff --check
   ```

5. Review manifest names against documentation:

   - Marketplace: `skills-for-langchain`
   - Plugin: `skills-for-langchain`
   - Skill: `langchain`
   - Invocation: `/skills-for-langchain:langchain`

6. Commit and push the release changes.
7. Create and push an annotated `vMAJOR.MINOR.PATCH` tag.
8. Publish a non-draft GitHub Release with installation commands, validation facts, and limitations.
9. Add the tagged marketplace in a clean configuration and smoke-test installation.

## Versioning policy

- **MAJOR:** incompatible plugin identity, invocation, or behavior changes.
- **MINOR:** new measured coverage or new user-visible capability.
- **PATCH:** corrections, documentation improvements, or evidence fixes that preserve the public contract.

Because `plugin.json` contains an explicit version, pushing a commit without bumping it does not update an installed cached plugin. Do not duplicate the version in the marketplace entry.

## Marketplace compatibility

The marketplace entry uses a relative plugin source under the repository. Supported installation sources are the GitHub repository shorthand, a git URL, or a local checkout. Do not document a raw `marketplace.json` URL because it cannot provide the relative plugin files.

## Brand asset

The project artwork has a separate rights notice in [assets/README.md](../../assets/README.md) and is not covered by the MIT License. Confirm rights before using it in a derivative distribution or a community marketplace submission.
