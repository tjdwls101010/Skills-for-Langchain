# 05 — Implementation checklist (ordered)

For the fresh session that implements this plan. Work top to bottom. All harness-creator script paths are absolute (they run from a plugin cache in some installs, so relative paths break). Do not start until you have read `00`–`04`; the scope guardrail in `01` (process, not encyclopedia) is the thing most likely to be violated under momentum.

## Step 0 — Orient

- Load the `langchain` skill's current files and re-read them: `.claude/skills/langchain/SKILL.md`, `references/deepagents.md`, `references/langchain-langgraph.md`. Note that the two references are **frozen** by this plan — you will not edit them.
- Read `.claude/harness-spec.md` (rows B1–B35, all `validated`) so your new rows continue the numbering and match the format.
- Run the audit for a clean baseline: `python "/Users/seongjin/.claude/skills/harness-creator/scripts/audit_harness.py" --path .`

## Step 1 — Author `references/consultant.md` (new)

Write the new reference per `03` Section E: persona (full), interview protocol, the ~10-dimension checklist expanded (each a principle with its driving decision and reference pointer), the build rules (agreement gate + per-case scope + build-against-current-API + verify-to-scope), and **one** worked example dialogue. English, no mid-sentence wrapping. Keep it consulting-process material only — if a sentence teaches a LangChain API, delete it (it belongs in the delta references or is already known).

## Step 2 — Edit `SKILL.md`

Per `02`:
- Broaden the `description` (consultant clause first, keep the code triggers, keep the CrewAI/AutoGen/LlamaIndex/raw-SDK near-miss boundary). Do **not** add `disable-model-invocation`.
- Add the body gist: title/identity, the consult-vs-deltas branch, the compact persona, the compact dimension checklist, the reference-usage rule, and a routing line pointing at `references/consultant.md`.
- **Preserve verbatim:** the three-layer "Orient by layer" model, the "Cross-cutting corrections", the reference routing (extended by the consultant line), and the "Staying current" maintenance note.
- Keep the added gist in the ~40–70 line range; overflow goes to `references/consultant.md`, not into SKILL.md.

Because SKILL.md is re-read live within a session, you can test-trigger it immediately after saving (see Step 5) without restarting.

## Step 3 — Sync the plugin mirror (`00` DC9)

Copy the updated `SKILL.md` and the new `references/consultant.md` (and confirm the two frozen references are still identical) into `plugins/skills-for-langchain/skills/langchain/`, then verify:

`diff -rq .claude/skills/langchain plugins/skills-for-langchain/skills/langchain` → must show no differences.

If the repo has a build/sync script that generates the plugin copy from the canonical source, prefer that over a manual copy, and re-diff regardless.

## Step 4 — Update the spec and pointers

- **`.claude/harness-spec.md`:** add new behavior-inventory rows for the consultant and their component specs. Suggested rows (renumber to continue from B35):
  - Consultant behavior: enter consultant mode on an abstract agent-building goal; interview before proposing; layer = skill; component = `.claude/skills/langchain/SKILL.md` + `references/consultant.md`.
  - Deltas-only preservation: plain LangChain code work still gets silent delta injection with no interview; component = `SKILL.md`.
  - Broadened trigger with preserved near-miss boundary; component = `SKILL.md` description.
  - Thin dimension checklist (no decision tree); component = `references/consultant.md`.
  - Agreement gate: design always, implement only after explicit go-ahead, scope per case; component = `references/consultant.md`.
  - New reference file exists and is pointer-reachable from SKILL.md; component = `references/consultant.md`.
  Update the Component specs, Design rationale (cite `00` DC1–DC10), and Change history (date, mode = extend, summary) sections. Set the new rows' `status` to `generated` after files exist, then `validated` after Step 5 passes. Also reflect the plugin-mirror obligation under B34's spec.
- **`CLAUDE.md`:** its one pointer line (line 7) currently says to load the skill before relying on remembered APIs. Lightly extend it to note the skill also *consults* on building agents from a goal — but keep it a one-line pointer, never a component inventory (that lives in `harness-spec.md`). Example addition: "...; it also acts as a consultant that interviews you and designs a LangChain/Deep Agents architecture when you describe an agent you want to build." Do not enumerate files or behaviors here.

## Step 5 — Validate (per `04`)

- **Tier 1 mechanical:** `validate_harness.py --path .` exits 0; plugin `diff -rq` clean; `scripts/validate_evidence.py` still passes (confirm what it covers).
- **Tier 2 trigger tests:** run the consult / deltas-only / no-trigger prompts; confirm each picks the right behavior. A consult prompt that skips the interview and writes code is a fail — tighten the SKILL.md branch.
- **Tier 3 dry-run:** run 2–3 consult prompts in a fresh session; review transcripts against the rubric (interviews first, reads references, concrete dimension-tied proposal, honest about fit, agreement gate holds, right language).
- **Tier 4 regression:** `git diff` shows the two delta references unchanged; optionally re-run 2–3 high-value probe tasks to confirm deltas-only still lands.

Fix and re-run until Tier 1 is green and the Tier 3 dry-run reads as a real consultant, not a code-first assistant.

## Step 6 — Release / version handling

- Check `docs/releases/` and the plugin manifest for how v1.0.0 was versioned. This change adds a user-facing capability (consulting) → it is at least a **minor** bump (e.g. v1.1.0) under SemVer, not a patch. Follow whatever release note / changelog convention the repo already uses; do not invent a new one.
- Ensure any version string that appears in both the canonical and plugin copies is updated in **both** and re-diffed (Step 3's invariant must still hold after the bump).

## Step 7 — Commit and push

- One focused commit (or a small logical series): the new reference, the SKILL.md edit, the plugin sync, the spec/CLAUDE.md/version updates. Every changed line should trace to this plan.
- Commit message: describe the consultant enhancement and reference this plan (`docs/plans/consultant/`). End with the required co-author trailer.
- Push to `origin/main` per the repo's existing flow (v1.0.0 was released to `main`). Confirm with the user before pushing if there is any doubt about branch policy.

## Guardrails to re-read if you feel the change growing

- **Not an encyclopedia** (`01`, `00` DC4): if you are writing lists of what LangChain can do, stop.
- **Don't touch the delta references** (`01`): they are the frozen evidence base.
- **Keep the auto-inject path lean** (`00` DC8): SKILL.md is paid on every code edit; heavy consultant material goes to `references/consultant.md`.
- **The agreement gate is real** (`00` DC6): design always, build only on an explicit yes, scope agreed per case.
- **Two locations, always** (`00` DC9): every skill edit is also a plugin-mirror edit, verified by `diff -rq`.
