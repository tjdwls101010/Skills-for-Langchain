# How It Works

## One plugin, one skill, two reference branches

The repository root is the marketplace root. The distributable plugin has its own strict-validating directory, while the project harness remains canonical:

```text
.claude-plugin/
└── marketplace.json

.claude/skills/langchain/
├── SKILL.md
└── references/
    ├── deepagents.md
    └── langchain-langgraph.md

plugins/skills-for-langchain/
├── .claude-plugin/plugin.json
└── skills/langchain/
    ├── SKILL.md
    └── references/...
```

The marketplace entry uses `source: "./plugins/skills-for-langchain"`. Installing from the GitHub marketplace copies only that plugin directory into Claude Code's versioned cache. `scripts/validate_evidence.py` requires the three packaged skill files to be byte-identical to the canonical `.claude/skills/langchain/` files.

## Automatic triggering

Claude Code compares the user's task with the skill description. The description deliberately names imports, constructors, and architectural areas so that a request can trigger even when the user does not mention a version.

The boundary also names nearby frameworks that should not trigger the skill: CrewAI, AutoGen, LlamaIndex, and raw provider SDK work unless bridged through LangChain.

Users can always force-load the skill with:

```text
/skills-for-langchain:langchain
```

## Progressive disclosure

`SKILL.md` contains only:

- A three-layer mental model: LangChain as framework, LangGraph as runtime, Deep Agents as harness.
- Corrections that matter across many tasks.
- Routing instructions for the two references.
- A point-in-time verification warning.

Detailed content lives in references. A Deep Agents task reads the Deep Agents branch; a LangChain or LangGraph task reads the thinner shared branch. A task spanning both can read both.

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
