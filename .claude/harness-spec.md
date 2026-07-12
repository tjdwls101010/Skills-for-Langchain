# Harness Spec — Skills for LangChain

## Context

This repository is a documentation-first Claude Code skill project. It contains no application build system or test runner; its product is a Python-only background knowledge skill for LangChain 1.x, LangGraph 1.x, and the Deep Agents SDK.

The authoritative implementation inputs are `docs/plans/` and the local official-doc snapshot at `.tmp/docs_langchain/`, drafted around April 2026. The measured consumer baseline is Claude Opus 4.8 with a January 2026 knowledge cutoff. The planning evidence consists of a doc-novelty survey and 38 blind knowledge probes recorded under `docs/plans/research/`.

Generated harness content is written in English to preserve API terminology and reduce translation drift. The interview and handoff remain in Korean.

The existing 65-line `CLAUDE.md` contains general engineering guidance. No user-scope `~/.claude/CLAUDE.md` exists, so there is no concatenation conflict to resolve.

## Goals

- Build the planned `.claude/skills/langchain/` skill using only post-cutoff deltas and high-value gotchas that the probes showed Claude gets wrong or does not know.
- Keep Deep Agents as the center of gravity while limiting LangChain and LangGraph coverage to the measured misses.
- Correct confidently outdated code without re-teaching topics the model already handles correctly.
- Preserve progressive disclosure with one short `SKILL.md` body and two invocation-shaped reference branches.
- Verify every shipped API claim against the local official-doc snapshot, then prove the skill is structurally valid and closes the measured knowledge delta.
- Package the same canonical skill as a public Claude Code plugin and marketplace with a byte-verified release copy that cannot drift silently.
- Commit and push the validated implementation to `origin/main`.

## Behavior inventory

| id | behavior/knowledge/constraint | layer | component | status |
|----|-------------------------------|-------|-----------|--------|
| B1 | Auto-trigger for Python work involving LangChain, LangGraph, or Deep Agents, while excluding unrelated agent frameworks and raw provider SDK work. | skill | `.claude/skills/langchain/` | validated |
| B2 | Orient the model around LangChain as framework, LangGraph as runtime, and Deep Agents as harness. | skill | `.claude/skills/langchain/SKILL.md` | validated |
| B3 | Correct `create_deep_agent(instructions=...)` and legacy subagent `prompt` to the current `system_prompt` names. | skill | `.claude/skills/langchain/SKILL.md` | validated |
| B4 | Preserve current model IDs that look post-cutoff and require explicit `provider:model` or `BaseChatModel` configuration. | skill | `.claude/skills/langchain/SKILL.md` | validated |
| B5 | Establish `langchain.agents.create_agent` as the already-compiled agent baseline rather than `create_react_agent`, `AgentExecutor`, or `initialize_agent`. | skill | `.claude/skills/langchain/SKILL.md` | validated |
| B6 | Document the current Deep Agents constructor, built-in tools and capabilities, and `create_file_data()` input seeding. | skill | `.claude/skills/langchain/references/deepagents.md` | validated |
| B7 | Prevent false filesystem-sandbox claims by explaining `FilesystemBackend(..., virtual_mode=True)` and the `CompositeBackend` boundary. | skill | `.claude/skills/langchain/references/deepagents.md` | validated |
| B8 | Prevent cross-user memory leakage by documenting `StoreBackend(namespace=...)`, store provisioning, and thread-scoped versus cross-thread storage. | skill | `.claude/skills/langchain/references/deepagents.md` | validated |
| B9 | Explain that summarization and large-result offloading are built in, with the current thresholds and the separate on-demand compaction option. | skill | `.claude/skills/langchain/references/deepagents.md` | validated |
| B10 | Document current synchronous subagent specs and `CompiledSubAgent(..., runnable=...)`. | skill | `.claude/skills/langchain/references/deepagents.md` | validated |
| B11 | Replace hand-rolled parallelism with first-class async subagents and their start, check, update, cancel, and list tools. | skill | `.claude/skills/langchain/references/deepagents.md` | validated |
| B12 | Explain interpreter-backed dynamic subagents, the `task()` global, and the documented `workflow` prompt lever. | skill | `.claude/skills/langchain/references/deepagents.md` | validated |
| B13 | Attach Deep Agents skills through `skills=[paths]` rather than assuming a backend scans directories. | skill | `.claude/skills/langchain/references/deepagents.md` | validated |
| B14 | Document current HITL `interrupt_on`, decision vocabulary, resume envelope, checkpointer, and v2 result access. | skill | `.claude/skills/langchain/references/deepagents.md` | validated |
| B15 | Document first-match filesystem permission rules as `FilesystemPermission` objects on `create_deep_agent`. | skill | `.claude/skills/langchain/references/deepagents.md` | validated |
| B16 | Replace hand-rolled judge loops with `RubricMiddleware` and its state-triggered fixed-verdict iteration loop. | skill | `.claude/skills/langchain/references/deepagents.md` | validated |
| B17 | Document provider- and model-keyed harness profiles and the separate Python provider profiles. | skill | `.claude/skills/langchain/references/deepagents.md` | validated |
| B18 | Replace invented Python execution middleware with QuickJS `CodeInterpreterMiddleware(ptc=[...])` and its `eval` tool. | skill | `.claude/skills/langchain/references/deepagents.md` | validated |
| B19 | Treat remote code sandboxes as backends that inject `execute`, with explicit file transfer and lifecycle management. | skill | `.claude/skills/langchain/references/deepagents.md` | validated |
| B20 | Use the current MCP adapter integration, `system_prompt`, and documented `transport: "http"` spelling. | skill | `.claude/skills/langchain/references/deepagents.md` | validated |
| B21 | Use Managed Deep Agents and LangSmith Deployments terminology and preserve the production `thread_id` versus `context` split. | skill | `.claude/skills/langchain/references/deepagents.md` | validated |
| B22 | Replace deprecated `SummarizationMiddleware` arguments with `trigger` and `keep`. | skill | `.claude/skills/langchain/references/langchain-langgraph.md` | validated |
| B23 | Replace the unmaintained supervisor package with the agent-as-tool coordinator pattern. | skill | `.claude/skills/langchain/references/langchain-langgraph.md` | validated |
| B24 | Use `ModelFallbackMiddleware` instead of model-runnable `.with_fallbacks()` for agents. | skill | `.claude/skills/langchain/references/langchain-langgraph.md` | validated |
| B25 | Preserve the distinct `ToolCallLimitMiddleware` exit semantics and checkpointer requirement. | skill | `.claude/skills/langchain/references/langchain-langgraph.md` | validated |
| B26 | Use `ProviderToolSearchMiddleware` and tool extras rather than hand-wiring provider beta payloads. | skill | `.claude/skills/langchain/references/langchain-langgraph.md` | validated |
| B27 | Prefer LangGraph event streaming v3 and its typed projections over legacy tuple-shaped stream handling. | skill | `.claude/skills/langchain/references/langchain-langgraph.md` | validated |
| B28 | Distinguish declarative `error_handler` compensation from retry policy and document graph-wide defaults. | skill | `.claude/skills/langchain/references/langchain-langgraph.md` | validated |
| B29 | Preserve the modern interrupt driver, `InMemorySaver`, and ID-keyed parallel resume map without re-teaching the known core pattern. | skill | `.claude/skills/langchain/references/langchain-langgraph.md` | validated |
| B30 | Use `DeltaChannel` to preserve reducer semantics while bounding checkpoint growth. | skill | `.claude/skills/langchain/references/langchain-langgraph.md` | validated |
| B31 | Record the point-in-time verification stamp and a reproducible refresh procedure based on official docs, novelty survey, and blind probes. | skill | `.claude/skills/langchain/SKILL.md` | validated |
| B32 | Point project-level sessions to this spec without duplicating a component inventory in `CLAUDE.md`. | CLAUDE.md | `CLAUDE.md` | validated |
| B33 | Prefer `@dynamic_prompt` for state-dependent prompt rewriting and use `system_message` rather than the deprecated `ModelRequest.override(system_prompt=...)` compatibility path. | skill | `.claude/skills/langchain/references/langchain-langgraph.md` | validated |
| B34 | Publish a byte-verified release copy of the canonical project skill through a strict Claude Code plugin manifest with SemVer metadata. | plugin | `plugins/skills-for-langchain/` | validated |
| B35 | Expose the repository as an installable same-repository Claude Code marketplace using stable public identifiers. | marketplace | `.claude-plugin/marketplace.json` | validated |

## Component specs

### `.claude/skills/langchain/SKILL.md`

- Frontmatter name: `langchain`.
- Invocation contract: `/langchain` standalone and `/skills-for-langchain:langchain` when installed from the marketplace, derived from the directory name.
- Description: deliberately broad positive triggers for LangChain, LangGraph, and Deep Agents Python work; explicit near-miss boundary for CrewAI, AutoGen, LlamaIndex, and raw OpenAI or Anthropic SDK usage unless bridged through LangChain.
- Invocation policy: model-invocable and user-invocable; no `disable-model-invocation`, `allowed-tools`, hooks, or forked context.
- Body: a short three-layer mental model, the cross-cutting corrections B3-B5, exact routing to the two real reference files, the measured exclusion reminder, and the point-in-time maintenance note.

### `.claude/skills/langchain/references/deepagents.md`

- One co-located reference because Deep Agents tasks routinely cross constructor, backend, subagent, memory, and context topics in one invocation.
- Sixteen measured topic sections in build-flow order: core, backends, memory, context, synchronous subagents, async subagents, dynamic subagents, skills, HITL, permissions, rubrics, profiles, interpreters, sandboxes, MCP, and production.
- Each section leads with the plausible wrong prior, gives the current minimal API, and explains the reason or failure mode that lets the model generalize.
- Claims and import paths are verified against the cited local `.mdx` files before delivery.
- The LangSmith sandbox lifecycle example must clean up with `client.delete_sandbox(ls_sandbox.name)`; the planning draft's `sb.delete()` does not match the official integration guide.
- MCP verification must use `langchain/mcp.mdx` and `deepagents/code/mcp-tools.mdx`; `deepagents/mcp.mdx` is only a redirect stub in this snapshot.

### `.claude/skills/langchain/references/langchain-langgraph.md`

- One thin reference containing only six LangChain and four LangGraph measured deltas.
- A scope note explicitly states that measured-correct topics are intentionally absent so the model does not distrust correct prior knowledge.
- Each section follows wrong prior → current API → why it matters and is verified against the cited local `.mdx` files.

### `CLAUDE.md`

- Preserve the existing general engineering guidance.
- Add one concise pointer to `.claude/harness-spec.md` and one trigger-oriented sentence for loading current LangChain-ecosystem knowledge.
- Do not enumerate reference topics or components; the filesystem and this spec remain the inventory sources of truth.

### `plugins/skills-for-langchain/.claude-plugin/plugin.json`

- Stable plugin name: `skills-for-langchain`; display name: `Skills for LangChain`.
- Explicit SemVer is the release cache key and must be bumped with every published release.
- The plugin root is `plugins/skills-for-langchain/`, isolating the package from project-only `CLAUDE.md` and other harness files so direct strict validation passes.
- The packaged `skills/langchain/` files mirror the canonical `.claude/skills/langchain/` files, and `scripts/validate_evidence.py` enforces byte equality.
- Metadata links to the public repository, MIT license, and maintainer identity.

### `.claude-plugin/marketplace.json`

- Stable marketplace name: `skills-for-langchain`.
- The single entry uses `source: "./plugins/skills-for-langchain"`, so users must add the GitHub repository or a git/local checkout rather than a raw marketplace JSON URL.
- The marketplace entry intentionally omits `version`; `plugin.json` is the sole version authority.
- `strict: true` makes the plugin manifest authoritative for component discovery.

### Components deliberately not generated

- No rules: the knowledge is task-triggered, not path-specific, and there is no application tree to target with `paths:` globs.
- No hooks or permissions: no requirement must deterministically block an action, and hooks would add latency without enforcing a project safety boundary.
- No agents: this is reference knowledge, not a read-heavy role whose exploration should be isolated.
- No workflows: implementation and future refreshes vary with the measured delta set; a fixed orchestration would freeze the wrong shape.

## Design rationale

One skill is the correct consolidation boundary because all included behaviors share one user intent: writing current Python for the LangChain ecosystem. Multiple skills would spend shared description budget and create competing triggers.

Two references follow genuine invocation branches. Deep Agents work needs its interconnected topics together, while ordinary LangChain or LangGraph work needs only the thin delta file. Splitting further by raw length would add routing decisions without reducing what a typical invocation must read.

The content boundary is empirical. Topics graded correct in the 38 blind probes remain excluded even when the docs label them novel, because re-teaching already-correct knowledge dilutes the corrections and can cause regressions. The highest-value content is either confidently outdated, unknown, or partial in a way that produces broken or unsafe code.

Advisory knowledge belongs in a skill, not in hooks or permissions. The task requires better judgment when an ecosystem request appears, not deterministic interception of a tool call or path.

## Validation

### Free deterministic checks

- Run the harness-creator validator after each component-writing pass and again after the change history and CLAUDE.md pointer are final. Delivery requires zero errors; strict mode should also be reviewed so warnings are intentional.
- Re-read the final skill description against positive and near-miss prompts in `docs/plans/05-validation.md`, because structural validation cannot grade trigger quality.
- Check every backticked `references/...` pointer resolves and keep the `SKILL.md` body under the validator's 500-line guideline.
- Validate the marketplace and plugin manifests separately with `claude plugin validate <manifest> --strict`, then run an isolated marketplace add/install/details smoke test before publishing a release.
- Run `python3 scripts/validate_evidence.py` to verify task counts, current generated-file hashes, residual consensus, and release metadata.

### Content verification

- Verify all 16 Deep Agents and 10 LangChain/LangGraph sections against their cited official `.mdx` sources in `.tmp/docs_langchain/`.
- Pre-generation source audit completed on 2026-07-12: constructor names, middleware parameters, backend security, namespace isolation, context thresholds, subagent fields and tools, HITL, permissions, rubrics, profiles, interpreter semantics, sandbox backends, MCP transport, production invocation, event streaming, error handling, interrupts, and `DeltaChannel` were checked against the local official docs. The pre-generation audit corrected the planned LangSmith sandbox cleanup and MCP source selection. The first after-probe then exposed two additional plan-level precision gaps: async subagent specs must be passed directly through `subagents=` for automatic middleware attachment, and `skills=` entries are top-level source directories rather than individual skill directories. Independent post-probe review also tightened the 20,000-token input-offload precondition and distinguished per-pass rubric results from terminal `max_iterations_reached` state.
- Re-run include-list probe scenarios with the relevant generated skill content injected and require each original `outdated_confident`, `partial`, or `unknown` key delta to disappear.
- Re-run the 11 measured-correct exclusion scenarios as a regression guard; they must remain correct.
- Record the resulting flip rate and any repair iterations in `docs/plans/research/probe-results.md` and this section.

### Results

- `validate_harness.py --path .`: PASS with 0 errors and 0 warnings.
- `validate_harness.py --path . --strict`: PASS with 0 errors and 0 warnings.
- `audit_harness.py --path .`: no component drift, dead links, hook issues, or user-scope conflicts.
- Manual trigger review: the 911-character description covers all seven positive scenarios and explicitly excludes the four near-miss classes in `docs/plans/05-validation.md`; no structural option disables model or user invocation.
- Historical Round-1 first after-pass: 23/26 correct. C6 and C8 revealed real reference gaps; later Codex review established that A2 also contained a real deprecated compatibility call and belonged in scope.
- Round-2 after-pass: 12/12 correct without repair.
- Targeted A2/C6/C8 repair-context retry after reference and prompt repair: 3/3 correct, using concise correction context and a shorter same-schema grader rather than the strict full-suite mechanism.
- Strict full-suite proof using generated files and the original grader: 35/38 correct, comprising 24/27 include-list flips and 11/11 measured-correct exclusions under the corrected baseline; residuals were A2, C6, and C8.
- Historical combined observed result across the strict full suites and separately labeled repair-context retry: 38/38 correct. The attempted historical faithful retry returned HTTP 429 and is not counted as final evidence.
- By explicit user decision, final residual validation used Codex subagents only and did not invoke Claude. Isolated attempts for A2, C6, and C8 embedded the exact current generated-file hashes; two independent official-doc graders per task returned `correct` (6/6), and a separate synthesis reviewer confirmed all attempt/grader hashes and found no material residuals.
- The Codex gate exposed and repaired A2 before its final pass: `ModelRequest.override(system_prompt=...)` is deprecated compatibility behavior. The reference now prefers `@dynamic_prompt`, or `request.override(system_message=SystemMessage(...))` when full wrapper control is required.
- Independent Codex API audit against the official snapshot passed after correcting summarization-helper wiring, interpreter import, rubric naming, model fallback wording, delete version gates, and sandbox path precision. The final split review also separated `deepagents deploy` from direct `langgraph deploy`, corrected stateful MCP sessions to `client.session("server_name")`, preserved "LangGraph Server" as a technical runtime term, and added the `langgraph>=1.2` error-handler gate; a focused re-review passed on the corrected hashes.
- Headless e2e: skipped by explicit user decision; it is optional and not part of the content-closure proof.
- Reclassified final baseline: 27/27 included probe tasks are correct after loading the skill, and all 11 exclusions remain correct. Exact Codex attempts, grader records, hashes, and synthesis are preserved in `docs/plans/research/probe-codex-results.json`.
- Public plugin normalization changed the canonical identifier to `langchain`; the three residual attempts and six independent grader records were regenerated against the release-candidate hashes, again producing 6/6 `correct`, synthesis pass, and no material residuals.
- Direct strict validation passed separately for `.claude-plugin/marketplace.json` and `plugins/skills-for-langchain/.claude-plugin/plugin.json`.
- Isolated local smoke test: marketplace add, plugin install, plugin list, and plugin details all passed; Claude Code reported version 1.0.0, one `langchain` skill, and no agents, hooks, MCP servers, or LSP servers.
- `python3 scripts/validate_evidence.py`: PASS with 38 tasks, 27 includes, 11 exclusions, matching generated-file hashes, and matching v1.0.0 release metadata.

### Optional paid e2e

- With explicit user consent only, run two to four isolated headless scenarios covering a positive Deep Agents trigger, a positive LangChain or LangGraph trigger, and an unrelated-framework near miss.
- Grade transcripts with cited tool-use or file evidence; surface-level compliance without evidence is a failure.
- The first run must be presented as verification of the headless permission mechanism itself because `--isolate` plus skipped permissions is documented as a reasoned default, not previously confirmed in this project.

## Change history

- 2026-07-12 — user approved the recovered spec and authorized the 38-scenario probe regression; headless e2e was explicitly declined.
- 2026-07-12 — sync/improve planning pass: audited the existing harness, recovered intent from `docs/plans/`, read the complete harness-creator reference and script package, verified the planned API surface against the local official docs, recorded initial source-level corrections, and proposed this spec.
- 2026-07-12 — generated the three-file skill and minimal `CLAUDE.md` pointer; ran both full after suites plus a three-task repair pass; repaired C6/C8 plus independent precision findings; preserved exact prompts and compact before/after evidence; passed normal and strict structural validation with zero findings.
- 2026-07-12 — user replaced the remaining validation method with Codex-only subagent review. The Codex gate found and repaired A2's deprecated override argument, then closed A2/C6/C8 with 2/2 independent `correct` verdicts per task and a passing hash/consensus synthesis. Added B33 and expanded the measured LC/LG reference from nine to ten deltas.
- 2026-07-12 — final independent Codex reviews found four version/branding precision issues and two plan-count/status inconsistencies. Corrected them, reran structural validation and the complete current-hash residual gate, obtained 6/6 independent `correct` verdicts again, and marked B1–B33 `validated`.
- 2026-07-12 — normalized the skill identifier to lowercase for public plugin compatibility and added a dedicated strict-validating Claude plugin plus same-repository marketplace manifest for the v1.0.0 release.
- 2026-07-12 — added public README/wiki and standard open-source governance files, regenerated current-hash residual evidence after identifier normalization, passed strict plugin/harness/evidence validation, and completed an isolated install/details smoke test; marked B34–B35 `validated`.
