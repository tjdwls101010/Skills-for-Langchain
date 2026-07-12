# 06 — Implementation checklist (for the next session)

An ordered, self-contained step list for the session that builds the skill from this plan. Each step names the doc that specifies it and the verification that closes it. Do them in order; the validation steps are not optional.

## Preconditions

- **The doc snapshot must be present.** `.tmp/docs_langchain/` is gitignored (it is ~71 MB), so a fresh clone will not have it. The build needs it to verify every API claim in `03`/`04` against ground truth. If it is missing, re-fetch the LangChain docs (`docs.langchain.com/oss/python/...`) into `.tmp/docs_langchain/` — see `research/README.md` for provenance. Do not author from this plan alone; the plan is a distillation and the docs are the source of truth.
- **Read `01-overview.md` first**, then keep `02`, `03`, `04` open while authoring.

## Build steps

1. **SKILL.md** → per `02`. Reuse the existing `.claude/skills/LangChain/` directory (do not rename it). Paste the frontmatter and body, then verify the three cross-cutting gotchas against the cited docs. Verify: file exists, YAML is well-formed.

2. **references/deepagents.md** → per `03`, all 16 topics in the recommended order. For each topic, verify the `current_api` against the cited `.mdx` file before writing it as fact — correct anything the docs contradict (the plan flags several "verify import path" spots). Write in conviction style: reason-first, teach only the delta, omit the "do not re-teach" parts. Add the version stamp at the top.

3. **references/langchain-langgraph.md** → per `04`, 6 LangChain + 4 LangGraph deltas. Same verification discipline. Add the version stamp and the top-of-file reminder that excluded topics are deliberately absent.

4. **Maintenance note.** Decide where the refresh procedure lives (a short paragraph in SKILL.md's "Staying current" section pointing at the plan, or a small `references/maintenance.md`). Keep it to a paragraph: re-fetch docs, re-run the survey and both probes, re-cross the axes, update only changed deltas, bump the stamp.

## Validation steps (per `05`)

5. **Structural gate.** Run `validate_harness.py --path .` and fix until it exits 0. This catches YAML parse failures (which silently disable auto-triggering) and unresolved pointers.

6. **Trigger review.** Re-read the `description` against the harness-creator `references/skills.md` triggering/near-miss guidance, and sanity-check it against the positive/negative prompt lists in `05`. `validate_harness.py` does not do this for you.

7. **Before/after delta closure.** Run the "after" probe variants described in `05` from the exact prompts and source hints committed in `research/probe-round1-tasks.json` and `research/probe-round2-tasks.json`; inject the reference content into the attempt stage. For the final residual gate, follow the user's Codex-only override: isolated Codex attempt agents receive the exact generated files, two independent Codex graders per task verify against official docs, and no Claude process is invoked. Confirm the include-list verdicts flip to `correct` and the excluded tasks do not regress. Revise any `03`/`04` section whose task did not flip, then re-run that task. Record hashes, grader consensus, and the flip rate in `research/probe-results.md`.

8. **(Optional) e2e trigger test** via `run_e2e.py` with user consent, to confirm the skill auto-triggers and is used in a real headless session.

## Wrap-up steps

9. **Create/update the harness spec.** The harness-creator flow expects `.claude/harness-spec.md` to exist and match disk (its hard line #3). Create it from this plan: Context, Goals, the Behavior-inventory table (one row per included topic, `status: generated` once files exist and `validated` once Check 3 passes), Component specs (the three files), Design rationale (why DeepAgents-centric, why these exclusions — cite the probe), and Validation (the flip-rate result). This is what a future `audit_harness.py` diffs against.

10. **CLAUDE.md pointer.** If a pointer helps discovery, add one line noting the skill exists and what it is for — do not enumerate its contents (that duplicates the skill and drifts). Keep it minimal.

11. **Commit and push.** One commit for the generated skill + spec + validation results, pushed to `origin main` (the repo is already wired). Message: what was generated and the flip-rate proof.

## Guardrails specific to this build

- **The single highest-frequency correction is `system_prompt=` not `instructions=`** (it appears across most DeepAgents topics). Make sure it lands in the SKILL.md body and is not only buried per-topic — if the model loads the body and gets nothing else, that one line already prevents the most common failure.
- **Do not restate the excluded list's topics as instructions.** They are measured-correct; re-teaching them wastes context and can cause the regression Check 3 guards against.
- **Keep the SKILL.md body short.** Bulk goes in references. The body loads on every trigger; a long body buries the cross-cutting gotchas that are its whole reason to exist.
- **Verify, do not trust.** Every code snippet in `03`/`04` came from a grader reading the docs, but this plan is one remove from the source. The docs win any disagreement.
