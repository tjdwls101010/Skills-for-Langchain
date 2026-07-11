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

**Mechanism.** Reuse the two probe workflow scripts from the planning session (they are persisted and cache-resumable):

- Round 1: `.../workflows/scripts/langchain-knowledge-probe-wf_bea6d393-a54.js`
- Round 2: `.../workflows/scripts/langchain-knowledge-probe-r2-wf_a3bf4eab-9d3.js`

Author an "after" variant of each: keep the task list and the grader stage unchanged, but change the blind-attempt stage so the agent **has the skill content available** instead of being forbidden from looking things up. The faithful way to do this is to inject the relevant reference file(s) into the attempt agent's prompt (for a DeepAgents task, prepend `references/deepagents.md`; for an LC/LG task, `references/langchain-langgraph.md`; plus the SKILL.md cross-cutting gotchas), then let it write the code. Grade with the identical rubric. This measures exactly one thing: does the skill's content close the delta?

**Success condition.** Every include-list task that was `outdated_confident`/`partial`/`unknown` should now grade `correct` (or at minimum lose its specific `key_deltas`). Any task that does not flip points at a weak section in `03`/`04` — revise that section's wording (usually it means the correction was buried or under-explained) and re-run just that task. Track the flip rate; the target is 100% of the high-value tasks.

**Regression guard.** Also run the seven excluded tasks (A1, A2, A3, A5, A6, B1, B4) and the round-2 excluded tasks (R1, R2, R5, R7, R9) through the "after" variant. They must stay `correct`. If the skill's presence makes a previously-correct task regress, the skill is over-correcting or contradicting the model's good knowledge — fix the offending section. This guard is why the SKILL.md body explicitly tells the model to trust its own correct code.

## What to record

After running the checks, write the outcome into `research/probe-results.md` (an "After" section: flip rate, any tasks that did not flip and what was revised) and into the harness spec's Validation section. This closes the loop: the next refresh has a documented baseline to compare against.
