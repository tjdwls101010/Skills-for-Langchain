# How It Works

## One plugin, one skill, three reference branches

The repository root is the marketplace root. The distributable plugin has its own strict-validating directory, while the project harness remains canonical:

```text
.claude-plugin/
└── marketplace.json

.claude/skills/langchain/
├── SKILL.md
└── references/
    ├── consultant.md          # interview process (consult path)
    ├── deepagents.md          # current-API deltas
    └── langchain-langgraph.md # current-API deltas

plugins/skills-for-langchain/
├── .claude-plugin/plugin.json
└── skills/langchain/
    ├── SKILL.md
    └── references/...
```

The marketplace entry uses `source: "./plugins/skills-for-langchain"`. Installing from the GitHub marketplace copies only that plugin directory into Claude Code's versioned cache. `scripts/validate_evidence.py` pins the byte hashes of the three probe-measured skill files (`SKILL.md` and the two delta references), and the full `diff -rq` on every skill edit keeps all packaged files — including `consultant.md` — byte-identical to the canonical `.claude/skills/langchain/` files.

## Automatic triggering and the consult-vs-deltas branch

Claude Code compares the user's request with the skill description. The description deliberately names both the consultant intent (design or build an agent, automate a multi-step task, build an assistant, answer from data — even with no framework named and no code shown) and the code-work surface (imports, constructors, architectural areas), so a request triggers whether it is a goal or a coding task.

Once loaded, the `SKILL.md` body decides which behavior to run. An outcome-shaped request — especially with no existing code and no framework named — enters the consultant: read `consultant.md` and interview. A request that writes, edits, or reviews existing LangChain-ecosystem code takes the deltas-only path: no interview, just the corrections and the relevant delta reference. Genuine ambiguity gets a single clarifying question, not a full interview.

The boundary also names nearby frameworks that should not trigger the skill: CrewAI, AutoGen, LlamaIndex, and raw provider SDK work unless bridged through LangChain. A framework-agnostic "build me an agent" legitimately loads this skill — it is the LangChain consultant — and part of that role is saying honestly when LangChain is not the right fit.

Users can always force-load the skill with:

```text
/skills-for-langchain:langchain
```

## Progressive disclosure

`SKILL.md` loads whenever the skill triggers, so it holds only what both paths need up front:

- The consult-vs-deltas branch, a compact consultant gist (persona, the thin ten-dimension checklist, the reference-usage rule).
- A three-layer mental model: LangChain as framework, LangGraph as runtime, Deep Agents as harness.
- Corrections that matter across many tasks.
- Routing instructions for the three references.
- A point-in-time verification warning.

Detailed content lives in references. The consult path reads `consultant.md` (the interview walkthrough, the expanded checklist, the build rules, one worked example) plus the relevant delta reference (`deepagents.md` and/or `langchain-langgraph.md`) before it proposes an architecture and again before it writes code — all only when consulting, and never paid on the deltas-only path. On the deltas-only path a Deep Agents task reads the Deep Agents branch; a LangChain or LangGraph task reads the thinner shared branch; a task spanning both can read both.

This shape keeps the always-loaded context small while preserving enough explanation for the model to generalize beyond copied examples.

## Why not more components?

- **No hooks:** the project supplies judgment, not a deterministic action that must intercept a tool call.
- **No permissions:** the plugin itself executes nothing and needs no tool access policy.
- **No MCP server:** all knowledge is static and local; network access at use time would make behavior less deterministic.
- **No custom agents:** the content is general background knowledge rather than a separate role with isolated context.
- **No workflows:** refresh and validation change with the measured delta set; a fixed orchestration would become stale.

## Evidence-selected content

The content boundary comes from two axes:

1. A documentation novelty survey identifies what is new or changed.
2. Blind probes identify what the consumer model actually gets wrong.

Only their useful intersection becomes skill content. This prevents the plugin from turning into a large, redundant manual that competes with correct model knowledge.

## Repository roles

- `.claude/skills/langchain/` is the canonical project-harness source.
- `plugins/skills-for-langchain/` is the strict-validating release package.
- `.claude-plugin/marketplace.json` is the discovery layer.
- `docs/wiki/` is user and maintainer documentation.
- `docs/plans/` is the design and audit record.
- `docs/plans/research/` is the evidence record.

Next: [Customization](Customization.md) or [Validation and Evidence](Validation-and-Evidence.md).
