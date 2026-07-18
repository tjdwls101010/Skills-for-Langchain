# Customization

Forking the project is encouraged when your organization has a different package baseline, model profile, or engineering policy. Preserve the measured-delta discipline while adapting it.

## Change the trigger boundary

Edit the `description` frontmatter in `.claude/skills/langchain/SKILL.md` when your fork should trigger on additional imports, constructors, or intents.

Good additions are concrete and discoverable:

- A new top-level package import.
- A new constructor that replaces an old one.
- A task category with repeated version-sensitive failures.

Avoid vague phrases such as “all AI work.” Broad descriptions steal unrelated tasks and spend context without providing relevant corrections.

## Add organization-specific conventions

Prefer a separate, clearly labeled section or reference for organization policy. Distinguish policy from upstream API fact:

```text
Upstream API: what the official package supports.
Organization policy: what this team chooses to require.
```

Examples include approved model providers, minimum package versions, deployment boundaries, logging rules, or mandatory sandbox providers.

## Add a new reference branch

Add a reference only when a real invocation branch would avoid loading a large amount of unrelated material. A branch is justified when:

- It has a distinct task trigger.
- It is large enough to bury cross-cutting corrections.
- Typical users need it independently of the existing branches.

Update the routing section in `SKILL.md`, the plugin documentation, and the harness spec together.

## Change the package baseline

If your project is pinned to older package versions, do not overwrite the current guidance with ambiguous statements. Add explicit version gates or maintain a release branch whose verification stamp matches your environment.

For a newer baseline:

1. Capture the official docs and package versions.
2. Re-run the novelty survey.
3. Re-run blind probes rather than assuming every documentation change is a model gap.
4. Update only the deltas that changed.
5. Preserve old evidence as historical evidence.

## Keep corrections reason-first

A durable correction states:

- The plausible wrong prior.
- The current API.
- Why the distinction matters.
- The version or exception boundary.
- The official source.

Do not add bare replacement tables without the reason. The explanation is what lets an agent handle adjacent cases that were not in the original probe.

## Keep one source of truth

Edit the canonical `.claude/skills/langchain/` files first, then mirror them into `plugins/skills-for-langchain/skills/langchain/`. `validate_evidence.py` checks the SemVer/CHANGELOG coupling and that a full `diff -rq` shows the whole skill directory — including `references/consultant.md` and the committed `docs_official.db` — identical between the two locations; do not make independent edits that allow the project harness and installed plugin to diverge.

Run [the validation workflow](Validation-and-Evidence.md) after every customization.
