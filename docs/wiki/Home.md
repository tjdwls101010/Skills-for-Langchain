# Skills for LangChain

Skills for LangChain is an evidence-built Claude Code plugin that supplies point-in-time Python API corrections for LangChain 1.x, LangGraph 1.x, and the Deep Agents SDK.

It is intentionally not a complete documentation mirror. The project measured 38 implementation tasks, kept 27 included probe tasks, preserved 11 measured-correct areas as regression guards, and organized the resulting corrections behind one automatically triggered skill with two progressively loaded references.

## Start here

- **Install and use it:** [Getting Started](Getting-Started.md) → [Use Cases](Use-Cases.md) → [Troubleshooting](Troubleshooting.md)
- **Understand or adapt it:** [Coverage and Limits](Coverage-and-Limits.md) → [How It Works](How-It-Works.md) → [Customization](Customization.md)
- **Maintain or contribute:** [Validation and Evidence](Validation-and-Evidence.md) → [Maintenance and Release](Maintenance-and-Release.md) → [Contributing](../../CONTRIBUTING.md)

## Core promise

The plugin tries to be small where the model is already right and precise where it is plausibly wrong. Every included correction should have a measured failure, a current official source, a reason that generalizes, and an explicit version boundary where needed.

## Important boundary

v1.1.0 is Python-only and verified against an official-documentation snapshot drafted around April 2026. It contains preview and version-gated APIs and is not a substitute for checking the package version installed in your environment.

Return to the [repository README](../../README.md) or browse the [wiki source map](README.md).
