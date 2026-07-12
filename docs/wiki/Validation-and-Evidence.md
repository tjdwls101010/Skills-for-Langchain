# Validation and Evidence

## Why measurement matters

The failure mode this project addresses is confident outdatedness. Asking a model what it does not know is therefore insufficient: the model may report an obsolete pattern as current with high confidence.

The project uses two evidence axes.

## Axis 1: documentation novelty

The official LangChain documentation snapshot was surveyed and classified into:

- `NOVEL`: a surface likely absent from the measured model's prior knowledge.
- `CHANGED`: a familiar surface whose API or recommendation moved.
- `KNOWN`: stable material that should not be copied into the skill without probe evidence.

The catalog is [docs/plans/research/novelty-catalog.md](../plans/research/novelty-catalog.md). Snapshot provenance and the aggregate digest are recorded in [docs-snapshot-manifest.md](../plans/research/docs-snapshot-manifest.md). The ignored 71 MB snapshot is not reconstructible from the repository alone; fetching live docs creates a new baseline.

## Axis 2: blind knowledge probes

Thirty-eight implementation tasks were attempted by Claude Opus 4.8 with a January-2026 knowledge cutoff, without documentation or web access, and graded against official sources.

| Verdict | Meaning | Scope decision |
|---|---|---|
| `correct` | Current API and task requirements satisfied | Exclude; use as regression guard |
| `outdated_confident` | Plausible, confident, but materially obsolete | Highest-value inclusion |
| `partial` | Correct scaffolding with missing or wrong specifics | Include the missing delta |
| `unknown` | No usable current answer | Include focused guidance |

Exact prompts and compact baseline records are preserved in [Round 1](../plans/research/probe-round1-tasks.json) and [Round 2](../plans/research/probe-round2-tasks.json).

## Baseline result

- 27 included probe tasks.
- 11 measured-correct exclusions.
- Included content resolves to 6 LangChain deltas, 4 LangGraph deltas, and 16 Deep Agents content topics. Deep Agents has 17 included probe tasks because C1 and C2 combine into one content topic.

## After-run evidence tiers

The after-run record is layered:

1. Full generated-file suites used the original doc-armed grading mechanism.
2. The strict combined result was 35/38 under the corrected baseline.
3. A separately labeled repair-context run confirmed the three residuals but is not represented as an identical-protocol full closure.
4. The user-approved final residual gate used current generated files, isolated Codex attempts, two independent official-doc graders per task, and a separate synthesis reviewer.

The final recorded state is 27/27 included probe tasks correct and 11/11 exclusions preserved. Exact current-file attempts, grader verdicts, and hashes are in [probe-codex-results.json](../plans/research/probe-codex-results.json). The compact combined after record is [probe-after-results.json](../plans/research/probe-after-results.json).

## Structural validation

The release requires:

```bash
claude plugin validate .claude-plugin/marketplace.json --strict
claude plugin validate plugins/skills-for-langchain/.claude-plugin/plugin.json --strict
python3 scripts/validate_evidence.py
git diff --check
```

The harness was also checked with the harness-creator normal and strict validators and audited for drift, dead links, hook issues, and user-scope conflicts.

## What is not claimed

- The evidence is not one identical-protocol 38/38 run.
- Headless E2E was skipped and is not release evidence.
- The probes do not prove performance for every model, prompt, package version, or application domain.
- Passing a code-generation probe does not prove runtime correctness, security, or production fitness.

## Evaluating a future refresh

A future refresh should preserve the task IDs when the intent is unchanged, append evidence rather than rewrite history, and clearly separate:

- A model that learned an API and no longer needs the correction.
- An API that changed and needs a new correction.
- A probe whose wording accidentally constrained or leaked the answer.
- A regression caused by over-correction in the skill.

Next: [Maintenance and Release](Maintenance-and-Release.md).
