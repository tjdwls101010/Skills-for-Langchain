# 04 — Validation plan

State the honest framing first (`00` DC10): the v1.0.0 knowledge skill had a *measurable* success criterion — 38 blind probes flip from wrong to correct. The consultant does not. "Did it consult well" is judgment, not a gradable fact. So validation here has two tiers: **mechanical gates** that must pass (structural + no-regression), and a **behavioral dry-run** that is a qualitative check a human reviews, not a pass/fail script. Present it to the user that way; do not manufacture a false metric.

## Tier 1 — Mechanical gates (must pass)

1. **`validate_harness.py` exits 0.**
   `python "/Users/seongjin/.claude/skills/harness-creator/scripts/validate_harness.py" --path .`
   Checks structural integrity: frontmatter parses, pointers resolve (including the new `references/consultant.md` and the SKILL.md routing line that points at it), no drift, no unknown tool names. Fix until zero errors.

2. **Plugin mirror is byte-identical** (`00` DC9).
   `diff -rq .claude/skills/langchain plugins/skills-for-langchain/skills/langchain` returns no differences. If the repo has an existing sync/build step, use it; otherwise copy the three-then-four files across and re-diff.

3. **`validate_evidence.py` still passes** (if it covers the skill files).
   `python scripts/validate_evidence.py` — run it and confirm the consultant additions did not break whatever evidence/stamp invariants it enforces. (This session did not read that script in full; the implementer should check what it asserts and whether the new `references/consultant.md` needs to satisfy any stamp rule. If it only validates the three delta files, the new consultant reference is out of its scope and that is fine — just confirm, don't assume.)

## Tier 2 — Trigger tests (the description does the right thing)

Because the description was broadened (`02`), verify it triggers on the new consult situations, still triggers on code, and still does *not* steal from neighbors. These are quick manual trigger checks (or `run_e2e.py` prompts if the user consents to spending tokens).

**Should enter CONSULTANT mode** (goal expressed, often no code, no framework named):
- "I want to build an agent that triages my support inbox and drafts replies."
- "Can you help me automate our weekly metrics report?"
- "I want something that answers customer questions from our PDF manuals."
- "지원 문의를 분류하고 답변 초안을 써주는 에이전트를 만들고 싶어." (Korean goal — must still trigger and interview in Korean.)

**Should get DELTAS-ONLY** (editing existing LangChain code; no interview):
- "Fix this `create_agent` call to add a summarization middleware." (existing code)
- "Review this `create_deep_agent` setup." (existing code)

**Should NOT trigger at all** (near-miss):
- "Build me an agent with CrewAI." (names a different framework)
- "Help me call the OpenAI Responses API directly." (raw provider SDK, not bridged through LangChain)

For each, record: did it load, and did it pick the correct behavior (consult vs deltas-only vs no-trigger). A consult prompt that loads but jumps straight to writing code without interviewing is a **fail** — the branch logic in SKILL.md (`02` body item 2) needs tightening.

## Tier 3 — Consultant behavioral dry-run (qualitative, human-reviewed)

Run 2–3 of the consult prompts above through a **fresh session with the skill loaded** and read the transcript against this rubric. This is the real test of whether the consultant works; it is judged, not scored.

- **Interviews before proposing.** It opens divergently (understands the goal in conversation) and then converges with AskUserQuestion over the checklist — it does not leap to an architecture on turn one.
- **Covers the dimensions without being robotic.** It touches the relevant checklist dimensions (skipping ones the user already answered) and does not ask questions that wouldn't move the design.
- **Reads the references before proposing.** The proposal reflects the *current* API — e.g. it says `create_deep_agent(system_prompt=...)`, `create_agent`, explicit `provider:model`, agent-as-tool over the removed supervisor package, `ModelFallbackMiddleware` over agent `.with_fallbacks()`. Stale reflexes leaking in means the reference-usage rule (`02` body item 5) is not landing.
- **Proposal is concrete and tied to dimensions.** It names specific components and explains each against the dimension that drove it, not a generic "you could use LangChain."
- **Honest about fit.** On a prompt where a Deep Agent is overkill (try one: "I just need to summarize a text file once"), it says so rather than over-engineering.
- **Respects the agreement gate.** It does not write files or run anything until told to, and it settles build scope before building.
- **Language.** The whole interview is in the user's language.

## Tier 4 — Delta-injection regression guard (must not break v1.0.0)

The change adds to SKILL.md and adds one reference file; it must not degrade the deltas-only behavior the probes measured.

- **Structural:** the cross-cutting corrections and three-layer model are still present verbatim in SKILL.md, and the two delta references are byte-unchanged (`git diff` shows no change to `references/deepagents.md` or `references/langchain-langgraph.md`).
- **Behavioral spot-check (optional but recommended):** re-run 2–3 of the highest-value probe tasks from `docs/plans/research/` (e.g. the `instructions=`→`system_prompt=` task, a supervisor→agent-as-tool task) with the skill loaded and confirm they still come out correct. The consultant additions should not change these; this guards against an accidental edit to the shared body that weakened a correction.

## What "done" reports to the user

A short honest summary: mechanical gates green (validate_harness 0, plugin byte-identical, evidence check passed); trigger tests behaved (consult / deltas-only / no-trigger each correct); the dry-run transcripts show real interviewing, current-API proposals, and the agreement gate holding; and the delta references are untouched so v1.0.0 behavior is intact. Plus the caveat: the consultant's quality is a judgment call reviewed in the dry-run, not a probe-measured number — if the user wants a stronger signal, more dry-run scenarios (at token cost) are the lever.
