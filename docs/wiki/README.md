# Skills for LangChain — documentation

The full documentation for the project. It lives in the main repository rather than in GitHub's separate Wiki so that documentation, skill content, manifests, and evidence all move through one review.

**New here?** Read [Home](Home.md) for what the project is and why it exists, then [Getting Started](Getting-Started.md) to install it.

## Pages

| Page | What it covers |
|---|---|
| [Home](Home.md) | What the project is, the problem it solves, who it is for, and what it deliberately does not do. |
| [Getting Started](Getting-Started.md) | Prerequisites, installing, pinning, verifying, updating, removing, and running a local checkout. |
| [Use Cases](Use-Cases.md) | What to actually ask for — the consult path and current-API recipes, with prompts you can paste. |
| [How It Works](How-It-Works.md) | The architecture: one plugin, one skill, two behaviors, and why there are no hooks or agents. |
| [The Knowledge Base](The-Knowledge-Base.md) | What is inside `docs_official.db`, its schema, how Claude queries it, and how it is built. |
| [Coverage and Limits](Coverage-and-Limits.md) | What the database contains, what was excluded and why, and where the guidance stops being reliable. |
| [Customization](Customization.md) | Adapting a fork: corpus selection, the gotchas list, the trigger boundary, organization conventions. |
| [Validation and Evidence](Validation-and-Evidence.md) | What is checked today, and the historical probe measurements that started the project. |
| [Maintenance and Release](Maintenance-and-Release.md) | Refreshing the database, the release checklist, versioning policy. |
| [Troubleshooting](Troubleshooting.md) | The skill not triggering, database failures, stale answers, local-versus-installed conflicts. |

## Reading paths

**Using the plugin** — [Getting Started](Getting-Started.md) → [Use Cases](Use-Cases.md) → [Troubleshooting](Troubleshooting.md)

**Understanding or forking it** — [Home](Home.md) → [How It Works](How-It-Works.md) → [The Knowledge Base](The-Knowledge-Base.md) → [Customization](Customization.md)

**Maintaining or contributing** — [Validation and Evidence](Validation-and-Evidence.md) → [Maintenance and Release](Maintenance-and-Release.md) → [Contributing](../../CONTRIBUTING.md)

## How these files are organized

Two pages carry the load, and they do not overlap:

- **[How It Works](How-It-Works.md)** is about the *machinery* — how a request reaches the skill, how the skill branches, why the package is shaped the way it is.
- **[The Knowledge Base](The-Knowledge-Base.md)** is about the *content* — what the database holds, how it is queried, and how it is rebuilt.

Everything else hangs off one of those two.

## Publishing to the GitHub Wiki

This directory does **not** synchronize with GitHub's separate Wiki repository. These files are the source of truth. `Home.md` and `_Sidebar.md` follow GitHub Wiki naming so a mirror is possible later; if one is ever published, automate the copy from here rather than editing two places. Note that the `../../` links to root files would need rewriting in any such mirror.

---

Back to the [project README](../../README.md).
