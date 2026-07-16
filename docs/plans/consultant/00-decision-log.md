# Decision Log — Consultant enhancement (planning session)

This is the running record of the decisions agreed during the consultant-enhancement planning session. It exists so a later implementation session can see *what was decided and why*, not only the final artifact. The detailed specs live in the sibling files `01`–`05`.

Session date: 2026-07-16 (planning only; implementation is a separate later session).

## Where this sits relative to the earlier plan

The earlier plan (`docs/plans/00-decision-log.md` and `01`–`06`) built the **knowledge skill** shipped as `v1.0.0`: a Python-only background skill at `.claude/skills/langchain/` that auto-triggers on LangChain-ecosystem code and injects only the measured post-cutoff deltas (38 blind probes). That plan is done and shipped. This plan does **not** revisit or re-measure that knowledge; it treats the existing `references/deepagents.md` and `references/langchain-langgraph.md` as a fixed, trusted evidence base and adds a new *behavior* on top of the same skill.

## Goal (in the user's words, paraphrased)

Turn the `langchain` skill from a pure knowledge encyclopedia into a **consultant**. When a user states an abstract goal — "I want to build an agent that does X", "I want to automate this task", "I want it to answer using this data" — the skill-loaded Claude should interview the user (freely, using AskUserQuestion as often as needed), figure out what agent they actually want, propose a concrete LangChain/LangGraph/Deep Agents architecture ("let's use Deep Agents middleware + HITL for this"), discuss it, and — after agreement — actually build it. The user was explicit that this must **not** become a "walking encyclopedia / 척척박사"; the deep knowledge is a means, and the consulting is the point.

## Confirmed decisions

| # | Decision | Choice | Rationale |
|---|----------|--------|-----------|
| DC1 | Skill structure | **One skill.** Enhance the existing `.claude/skills/langchain/` in place; SKILL.md carries the consultant persona, goals, and reference-usage. No second skill directory, no new slash command; invocation stays `/langchain`. | User chose "컨설턴트를 상위로, 지식을 흡수" then "하나의 스킬로 만들고 싶어." Keeping knowledge as one shared copy under a consultant SKILL.md means zero knowledge duplication, which was the real concern behind rejecting the two-skill option. |
| DC2 | Two behaviors, one skill | The skill still **auto-triggers** and, on plain code work, **silently injects the deltas** (v1.0.0 behavior preserved). On an agent-building request it instead runs the **consultant interview**. The SKILL.md body branches on the situation. | The two behaviors have different trigger contexts but share the same knowledge. The user explicitly required keeping the auto-injection ("자동주입 살리고") — it is the measured value of v1.0.0 and must not regress. |
| DC3 | Consultant entry point | **Auto-enter consultant mode when the user expresses an abstract agent-building goal** — not slash-only. A `/langchain` invocation also works, but a natural-language goal is enough. Plain edits to existing LangChain code do **not** launch an interview. | Supersedes the earlier "슬래시 전용" answer once the structure collapsed to one auto-triggering skill (a single auto-triggering skill cannot be strictly slash-only for one of its behaviors). The user picked "목적을 말하면 자동으로 컨설턴트 진입", which also matches the original vision of proactive consulting. |
| DC4 | Consultant knowledge depth | **Process, not encyclopedia.** Author only an interview protocol, a thin dimension checklist, and the discipline "read the delta references before proposing or implementing." Do **not** author a goal→architecture decision tree or a capability catalog. | User pushback, quoted: "결정 프레임워크를 미리 규정하는 것보다 … 클로드의 지능과 창의성을 무시하진 마." Claude already knows what middleware/HITL/RAG/subagents are conceptually; the gap it must close at *implementation* time is the current API, which the existing delta references already cover. A decision tree would be a rail that caps Claude's own mapping ability. |
| DC5 | Thin dimension checklist | **Agreed** (thin only). A short list of *dimensions to ask about* (not answers) so the interview never silently assumes one: task shape, single-vs-multi agent, external data/tools, state & memory, human-in-the-loop, control & safety, reliability, output shape, deployment/runtime, and build scope. Each item states *what architecture decision it drives*, so it reads as a principle, not a form. | The failure mode is not Claude mis-mapping a goal; it is Claude forgetting to *ask* about a dimension and assuming. A checklist of questions respects intelligence while adding discipline. |
| DC6 | Output scope of "build it" | **Design always; implement only after explicit agreement; the build's depth (code-only vs runnable scaffolding vs full project) is agreed with the user per case** — no fixed default depth. | User chose "설계는 항상, 구현은 합의 후" and "매번 사용자와 범위 합의." Mirrors the harness-creator philosophy of a hard agreement gate before side-effecting generation. |
| DC7 | Language | **Skill files in English** (persona, checklist, instructions, code), matching the existing skill and the earlier plan's D4/D7. The interview *conversation* happens in the user's language (Korean here). | Consistency with the shipped skill; English preserves API terminology and Claude's own parsing/triggering. Language of the conversation is a runtime behavior, not a file-authoring choice. |
| DC8 | Progressive disclosure | Keep the **auto-inject path lean**: SKILL.md holds the persona, the consult-vs-deltas branch, the thin checklist, the reference-usage rules, and the existing three-layer model + cross-cutting gotchas + routing. The heavier interview walkthrough and worked example go into a **new `references/consultant.md`**, read only when actually consulting. | SKILL.md auto-loads on every code edit; padding it with the full interview script would tax the delta-injection path with text it never needs (skills.md progressive-disclosure doctrine). The consult path is the only one that branches into the walkthrough, so that is the correct split seam. |
| DC9 | Plugin mirror | The implementation must re-sync `plugins/skills-for-langchain/skills/langchain/` to be **byte-identical** to `.claude/skills/langchain/` after the change, and verify with `diff -rq`. | The plugin copy is a real copy, not a symlink (verified this session); `harness-spec.md` B34 requires a byte-verified release copy that cannot drift. Every skill edit is therefore a two-location edit. |
| DC10 | Validation approach | Trigger tests (consult / deltas-only / no-trigger) + a **consultant dry-run** on 2–3 example goals + a **delta-injection regression guard** + `validate_harness.py` exit 0 + plugin byte-diff. Stated honestly: this is **weaker than the v1.0.0 probe suite** because "did it consult well" is not mechanically gradable the way "is this API current" is. | The consultant's quality is judgment, not a measurable fact. Pretending otherwise would set the implementation session up to fabricate a false success metric. |

## Session Q&A record (for provenance)

AskUserQuestion rounds, in order, with the user's chosen answers:

1. Structure → "컨설턴트를 상위로, 지식을 흡수" (later refined to one skill, DC1).
2. Knowledge depth → user rejected a pre-defined decision framework, said to trust Claude's intelligence + the delta knowledge (DC4).
3. Output range → "설계는 항상, 구현은 합의 후" (DC5/DC6).
4. Consultant trigger → "슬래시 명령만" (later superseded by DC3 once structure became one auto-triggering skill).
5. Knowledge auto-injection → "유지 — 자동주입 살리고 컨설턴트는 슬래시" (DC2).
6. Thin checklist → "동의 — 얇은 체크리스트만" (DC5).
7. Implementation depth → "매번 사용자와 범위 합의" (DC6).
8. Entry structure → "하나의 스킬로 만들고 싶어. SKILL.md에 컨설턴트로서의 페르소나와 목표, 레퍼런스 문서 활용 방식을 적는" (DC1, DC8).
9. Command name → "." = no separate name needed; keep `/langchain`.
10. Interview trigger → "목적을 말하면 자동으로 컨설턴트 진입" (DC3).

## Method note

This session = planning only. No SKILL.md is written and no component is generated. The deliverable is this self-contained plan under `docs/plans/consultant/`, which a fresh Claude session can implement from without re-deriving scope. Per the harness-creator loop, `harness-spec.md` is **not** updated this session (no files were generated); the implementation session updates it as part of generation (see `05`).
