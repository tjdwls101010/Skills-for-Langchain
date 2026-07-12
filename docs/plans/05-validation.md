# 05 — Validation protocol

This defines what "the skill works" means, concretely, and how to prove it. The spine is the before/after probe: the probe tasks are a regression suite whose verdicts should flip once the skill is in place. There are three checks, from cheapest to most real.

## Check 1 — Structural gate (`validate_harness.py`)

Non-negotiable. From the target repo root:

```
python3 "/Users/seongjin/.claude/skills/harness-creator/scripts/validate_harness.py" --path .
```

Must exit 0 (no errors). This verifies the SKILL.md frontmatter YAML parses (a parse failure silently disables auto-triggering), that reference pointers resolve, and that there is no spec-vs-disk drift. It does **not** grade the `description` for trigger quality — that is Check 2's manual step.

## Check 2 — Trigger quality (manual + optional e2e)

The `description` is the only mechanism that loads the skill, so it must fire on real ecosystem work and stay quiet on unrelated work. First, re-read the `description` against the harness-creator `references/skills.md` triggering and near-miss guidance (this is called out as a step `validate_harness.py` cannot do for you). Then sanity-check it against these prompts.

Should trigger (positives):

- "Build a deep agent that can plan and use a filesystem."
- "Add human-in-the-loop approval before my deepagents agent sends email."
- "My deep agent needs memory that persists across sessions."
- "Tune my deep agent differently for Anthropic vs OpenAI models."
- "Create a LangChain agent that falls back to a second model if the first fails."
- "Stream events from my LangGraph agent and show tool calls."
- "Set up a multi-agent system where a coordinator delegates to specialists." (LangChain)

Should NOT trigger (near-misses):

- "Build an agent with CrewAI / AutoGen / LlamaIndex." (different framework)
- "Write a Python script to parse this CSV." (no agent framework)
- "Call GPT with the OpenAI SDK." (raw SDK, not being bridged to LangChain)
- "Set up a FastAPI endpoint." (unrelated)

Optionally verify triggering for real with a headless session (spends tokens; get consent):

```
python3 "/Users/seongjin/.claude/skills/harness-creator/scripts/run_e2e.py" \
  --project . --prompt "Build a deep agent that can plan and use a filesystem" --isolate
```

Note (from the harness-creator docs): `run_e2e.py`'s headless permission handling (`--isolate` + `--dangerously-skip-permissions`) is a documented best guess, not empirically confirmed — say so before the first real run.

## Check 3 — Before/after delta closure (the core proof)

This is the reason the probe was built to be reusable (decision D9). "Before" is already captured in `research/probe-results.md`: the include-list tasks graded `outdated_confident` / `partial` / `unknown`. "After" re-runs those same tasks with the skill's content available, and the success condition is that the verdicts flip to `correct`.

**Mechanism.** Use the exact task prompts and baseline grading records committed in `research/probe-round1-tasks.json` and `research/probe-round2-tasks.json`; the original planning-session workflow paths were ephemeral and are not a repository dependency. Build an "after" variant that keeps those task prompts and the doc-armed grading rubric unchanged, but changes the blind-attempt stage so the agent **has the skill content available** instead of being forbidden from looking things up. The faithful way to do this is to inject the relevant reference file(s) into the attempt agent's prompt (for a DeepAgents task, prepend `references/deepagents.md`; for an LC/LG task, `references/langchain-langgraph.md`; plus the SKILL.md cross-cutting gotchas), then let it write the code. Preserve internal knowledge for topics the skill explicitly marks measured-correct and intentionally omitted; making the supplied delta material the sole authority creates a false regression on exclusions. Grade with the identical verdict rubric and official-doc source hints stored beside each prompt. This measures exactly one thing: does the skill's content close the delta?

**Success condition.** Every include-list task that was `outdated_confident`/`partial`/`unknown` should now grade `correct` (or at minimum lose its specific `key_deltas`). Any task that does not flip points at a weak section in `03`/`04` — revise that section's wording (usually it means the correction was buried or under-explained) and re-run just that task. Track the flip rate; the target is 100% of the high-value tasks.

**Regression guard.** Also run the six Round-1 excluded tasks (A1, A3, A5, A6, B1, B4) and the five Round-2 excluded tasks (R1, R2, R5, R7, R9) through the "after" variant. They must stay `correct`. If the skill's presence makes a previously-correct task regress, the skill is over-correcting or contradicting the model's good knowledge — fix the offending section. This guard is why the SKILL.md body explicitly tells the model to trust its own correct code.

### 2026-07-12 implementation override — Codex-only residual gate

The user explicitly replaced the final residual validation mechanism: do not invoke Claude for any remaining check. For each residual task, run an isolated Codex attempt agent that receives only the exact current `SKILL.md` plus the applicable generated reference and records the SHA-256 of every supplied file. Then run two independent Codex graders that receive the attempt plus the official-doc source paths, but not the generated skill, the other grader, or prior verdicts. Both graders must return `correct`; the attempt digest and generated-file hashes must match the current files. A separate Codex synthesis reviewer verifies the hashes, agreement, and absence of material residuals. Preserve the attempt, grader, and synthesis JSON in `research/probe-codex-results.json`.

This override is intentionally narrower than re-running all 38 scenarios: the historical full suites already cover the other 35 tasks, while A2, C6, and C8 were the only residuals. If Codex identifies a real API defect, update the baseline classification and skill content before repeating the affected task. That rule reclassified A2 from an exclusion to an included delta because `ModelRequest.override(system_prompt=...)` is deprecated compatibility behavior; new middleware code should use `@dynamic_prompt` or `request.override(system_message=SystemMessage(...))`.

## What to record

After running the checks, write the outcome into `research/probe-results.md` (an "After" section: flip rate, any tasks that did not flip and what was revised) and into the harness spec's Validation section. This closes the loop: the next refresh has a documented baseline to compare against.
