# Maintenance and Release

Maintainer procedures: refreshing the documentation snapshot, and publishing a release.

## Refreshing the database

This is the main recurring task. Since v1.2.0 it involves no probing and no manual curation — clone, build, validate, bump.

### 1. Clone the upstream documentation

```bash
rm -rf .tmp/docs_langchain
git clone --depth 1 https://github.com/langchain-ai/docs .tmp/docs_langchain
```

Clone the **whole repository**, not just `src/oss/`. The code snippets live at `src/snippets/`, outside the documentation tree, and a partial copy is exactly how the original snapshot ended up without them.

`.tmp/` is gitignored. Do not commit it — it is roughly 71 MB.

### 2. Build

```bash
python3 scripts/build_docs_db.py \
  --src .tmp/docs_langchain \
  --out .claude/skills/langchain/references/docs_official.db \
  --mirror plugins/skills-for-langchain/skills/langchain/references/docs_official.db
```

`--mirror` writes both copies in one pass, which is the easiest way not to forget the second one.

**Read the report before continuing.** It prints per-package document counts, the snippet-substitution total, changelog rows, the resolved snapshot date and source commit, and the final file size. What you are looking for:

- Per-package counts in the same neighborhood as the previous build. A package dropping to near zero means the upstream directory moved.
- A snippet-substitution count that has not collapsed. The v1.2.0 build did 346. A sharp fall means imports stopped resolving — and the code is what you would be losing.
- A size warning above 20 MB, which almost always means the integrations catalog leaked into the corpus.

The build fails hard on an unresolved snippet import or an import cycle. That is intended: a silently degraded database is worse than no new database.

### 3. Validate

```bash
python3 scripts/validate_docs_db.py
```

Every check must pass. The one that matters most is the `dynamic-subagents` assertion — it is the regression this database exists to prevent. See [Validation and Evidence](Validation-and-Evidence.md).

### 4. Re-check the gotchas by hand

The only step requiring judgment. The gotchas list in `SKILL.md` covers removed and renamed APIs, and **no automated check can tell you it is still accurate** — that is the same blind spot that makes the list necessary in the first place.

Read the freshly parsed changelog for anything that removes, renames, or replaces an API:

```bash
sqlite3 -readonly .claude/skills/langchain/references/docs_official.db \
  "SELECT date, package, version, summary FROM changelog ORDER BY date DESC LIMIT 20;"
```

Add a gotcha when something the model will reach for has disappeared. Remove one when the reflex it corrects is no longer plausible. Keep the list short — it loads on every trigger.

### 5. Confirm the mirror and bump

```bash
diff -rq .claude/skills/langchain plugins/skills-for-langchain/skills/langchain
```

Then follow the release checklist below. A refreshed snapshot is user-visible, so it is at least a minor bump.

## Release checklist

1. **Choose the SemVer impact** using the policy below.
2. **Update `plugins/skills-for-langchain/.claude-plugin/plugin.json`.** This is the sole version authority. The marketplace entry deliberately carries no version — do not add one.
3. **Add a `## [x.y.z]` section to `CHANGELOG.md`** with the date. `validate_evidence.py` fails if the version has no matching heading.
4. **Update documentation** wherever behavior, coverage, snapshot date, or limits changed. The snapshot date appears in the README, [Home](Home.md), [The Knowledge Base](The-Knowledge-Base.md), and [Coverage and Limits](Coverage-and-Limits.md) — all four, or none.
5. **Run everything:**

   ```bash
   python3 scripts/validate_docs_db.py
   python3 scripts/validate_evidence.py
   claude plugin validate .claude-plugin/marketplace.json --strict
   claude plugin validate plugins/skills-for-langchain/.claude-plugin/plugin.json --strict
   git diff --check
   ```

   CI covers all of these except `validate_docs_db.py`. Run that one locally, every time.

6. **Check the identifiers** still match what the documentation tells users to type:

   | Thing | Value |
   |---|---|
   | Marketplace | `skills-for-langchain` |
   | Plugin | `skills-for-langchain` |
   | Skill | `langchain` |
   | Invocation | `/skills-for-langchain:langchain` |

7. **Open a pull request.** Recent releases went through PRs rather than direct pushes to `main`.
8. **Tag** an annotated `vMAJOR.MINOR.PATCH` after merge, and push it.
9. **Publish a GitHub Release** — not a draft — with install commands, what changed, and the honest validation state.
10. **Smoke-test from a clean configuration:** add the tagged marketplace, install, and confirm the skill queries the database.

Steps 8 through 10 are the ones that get skipped under time pressure, and skipping them is visible to users: an untagged version means nobody can pin to it, and the documentation ends up pointing at a tag older than the shipped version.

## Behavioral spot-check

Mechanical validation cannot show that the skill *uses* the database. After a substantive change, run a real session from outside the repository and confirm three things:

```bash
PLUGIN_DIR="$PWD/plugins/skills-for-langchain"
(cd "$(mktemp -d)" && claude --plugin-dir "$PLUGIN_DIR")
```

1. A `sqlite3` query runs **before** any code is written.
2. The result contains no stale reflexes — `instructions=`, `create_react_agent`, `.with_fallbacks()`, a `supervisor` import.
3. A goal stated with no code enters the consultant and writes nothing before you agree.

## Versioning policy

| Bump | When |
|---|---|
| **MAJOR** | Plugin identity, invocation, or behavior changes incompatibly. |
| **MINOR** | New user-visible capability, or a refreshed documentation snapshot. |
| **PATCH** | Corrections, documentation, or evidence fixes that preserve the contract. |

The version in `plugin.json` is the cache key for installed plugins. Pushing content without bumping it means installed clients keep serving the cached copy — the change effectively does not ship.

Historical precedent: v1.1.0 added the consultant behavior; v1.2.0 replaced the knowledge substrate. Both were minor bumps despite being large changes, because neither broke the public contract.

## Marketplace compatibility

The marketplace entry uses a relative source, `./plugins/skills-for-langchain`. Supported installation sources are the GitHub repository shorthand, a git URL, or a local checkout.

Never document a raw `marketplace.json` URL. A bare JSON file cannot supply the relative path it points at, and the install fails in a way that looks like a broken plugin rather than a wrong command.

## The historical refresh procedure

Before v1.2.0, refreshing meant re-fetching the docs, re-running the novelty survey, re-running both blind probe sets against the consumer model, crossing the axes, updating the deltas that changed, and re-running the after-probes plus the regression guards.

That process is retired. It is described here only so a reader of the older plan documents knows it is no longer in force — the expense of it is precisely why the substrate changed. See [Validation and Evidence](Validation-and-Evidence.md) for what it measured, and `docs/plans/docs-db/` for why it was replaced.

## Brand asset

The artwork under `assets/` is **not** covered by the MIT License and has a separate rights notice in [assets/README.md](../../assets/README.md). It contains third-party visual elements. Confirm rights before using it in a derivative distribution or a community marketplace submission.

---

**Next:** [Validation and Evidence](Validation-and-Evidence.md) for what the checks prove, or [Contributing](../../CONTRIBUTING.md).

Back to the [documentation index](README.md).
