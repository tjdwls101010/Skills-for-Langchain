# Skills for LangChain

Skills for LangChain is an evidence-built Claude Code plugin that does two things over one shared knowledge base for LangChain 1.x, LangGraph 1.x, and the Deep Agents SDK: it acts as a **solutions consultant** that turns an agent-building goal into a concrete, current-API architecture and builds it on agreement, and it acts as a **current-API guide** that supplies point-in-time Python corrections when you write or review existing code.

It is intentionally not a complete documentation mirror, and the consultant is intentionally not a walking encyclopedia. The project measured 38 implementation tasks, kept 27 included probe tasks, preserved 11 measured-correct areas as regression guards, and organized the resulting corrections behind one automatically triggered skill with three progressively loaded references: an interview process and two API-delta branches.

## Start here

- **Install and use it:** [Getting Started](Getting-Started.md) → [Use Cases](Use-Cases.md) → [Troubleshooting](Troubleshooting.md)
- **Understand or adapt it:** [Coverage and Limits](Coverage-and-Limits.md) → [How It Works](How-It-Works.md) → [Customization](Customization.md)
- **Maintain or contribute:** [Validation and Evidence](Validation-and-Evidence.md) → [Maintenance and Release](Maintenance-and-Release.md) → [Contributing](../../CONTRIBUTING.md)

## Core promise

The plugin tries to be small where the model is already right and precise where it is plausibly wrong. Every included correction should have a measured failure, a current official source, a reason that generalizes, and an explicit version boundary where needed. The consultant follows the same discipline in a different register: it adds interview process and posture, not more API facts, because a capable model already designs sound architectures — what it needs is to ask before assuming and to ground the proposal in the current API by reading those same references before it proposes or writes code.

## Important boundary

v1.1.0 is Python-only and verified against an official-documentation snapshot drafted around April 2026. It contains preview and version-gated APIs and is not a substitute for checking the package version installed in your environment.

Return to the [repository README](../../README.md) or browse the [wiki source map](README.md).
