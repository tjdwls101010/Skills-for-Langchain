# Customization

Adapting a fork to your organization. Read [How It Works](How-It-Works.md) and [The Knowledge Base](The-Knowledge-Base.md) first — the customization surfaces map directly onto that architecture.

## Where the levers are

There are four places worth changing, and one that is almost never the answer.

| Lever | File | Change it when |
|---|---|---|
| **Corpus selection** | `scripts/build_docs_db.py` | You need documentation the shipped database excludes, or want it smaller. |
| **The gotchas list** | `.claude/skills/langchain/SKILL.md` | Your team hits a removed or renamed API the list misses. |
| **The trigger boundary** | `SKILL.md` frontmatter `description` | The skill should load on your internal packages, or should stop over-triggering. |
| **Organization policy** | A new reference file | You have rules that are yours, not upstream's. |
| ~~Hand-written API prose~~ | — | Almost never. See below. |

## Corpus selection — the main lever

The most likely thing you want is different documentation. That is one list in `scripts/build_docs_db.py`:

```python
INCLUDE = [
    ("langchain", "langchain"),
    ("langgraph", "langgraph"),
    ("deepagents", "deepagents"),
    ("concepts", "concepts"),
    ("reference", "reference"),
    ("python/migrate", "migrate"),
    ("python/releases", "releases"),
]
```

Each tuple is `(directory under src/oss, package label)`, recursed for `.mdx` files.

**To add the integrations catalog** — 579 files on providers, vector stores, and connectors, excluded from the shipped build for size:

```python
    ("python/integrations", "integrations"),
```

Expect the database to grow several times over. Also raise the sanity band in both `build_docs_db.py` and `scripts/validate_docs_db.py`, which currently assert a document count between 150 and 250 — a check that exists to catch a glob matching nothing or everything, and that will now fire on a legitimate build.

**To trim it**, drop entries you do not use. A team that never touches Deep Agents can remove that line and cut the database roughly in half.

**Do not add the JavaScript directories.** The exclusion is not about size. A Python-only skill whose database contains JavaScript can retrieve JavaScript and present it as Python, and no amount of prompt wording reliably prevents that. If you want JavaScript coverage, build a separate database and a separate skill.

After any corpus change:

```bash
python3 scripts/build_docs_db.py --src .tmp/docs_langchain --out <your-db-path>
python3 scripts/validate_docs_db.py --db <your-db-path>
```

## The gotchas list

The gotchas exist for one reason: a search over current documentation cannot reveal what was **removed**. Adding to that list is justified when — and only when — all three hold:

1. Your team's model reaches for something that no longer exists, or has been renamed.
2. The database structurally cannot correct it, because the removed thing has no current page to find.
3. You can show it is genuinely gone, not merely undocumented.

Anything that fails the second test belongs in the corpus, not the list. If the model gets something wrong and the correct answer *is* in the official docs, the fix is a better search or a fresher snapshot — not another line of prose that will silently rot.

Keep the list short. It loads on every single trigger, including one-line corrections, and every line spends context that the code path pays for.

## The trigger boundary

The `description` frontmatter in `SKILL.md` is what Claude Code matches against a request. Widen it for concrete, discoverable things:

- An internal wrapper package your team imports instead of `langchain` directly.
- A constructor your codebase standardized on.
- A recurring task category that keeps producing version-sensitive failures.

Avoid vague widening — "all AI work," "anything about agents." A description that broad steals unrelated tasks and spends context on requests it cannot help with.

Narrowing is legitimate too. The shipped description over-triggers on purpose, because a missed load means confidently deprecated code. If your team finds that trade wrong for them, tighten it — but understand what you are trading away.

## Organization policy

Keep your rules separate from upstream fact, in their own reference file, and label the distinction explicitly:

```text
Upstream API   — what the official package supports.
Our policy     — what this team requires.
```

Policy that belongs here: approved model providers, minimum package versions, mandatory sandbox providers, logging and audit requirements, deployment boundaries, which APIs are banned regardless of what the docs say.

Do not fold policy into the gotchas list. Gotchas are claims about the world that anyone can verify; policy is a choice your organization made. Merging them makes both harder to maintain, and makes it impossible to tell which lines survive a database refresh.

Point `SKILL.md` at the new file with a one-line pointer describing when to read it.

## Why hand-written API prose is the wrong answer

The strongest temptation when forking is to write down what your team keeps getting wrong. Resist it.

That is exactly what v1.0.0 did, and it failed in a specific, non-obvious way: distillation drops content silently. A 369-line official page on subagent orchestration was compressed to a single heading and lost ten working code samples, and nothing about the process ever flagged it — because a summary that loses content looks identical to one that does not.

If the answer is in the official docs, it is already in the database. If it is *not* in the database, the fix is corpus selection or a refresh. The only durable exception is the removed-API case above, and that one exists because of a structural property of search rather than a preference.

## Changing the package baseline

If you are pinned to older packages, do not blur the shipped guidance into version-ambiguous statements. Either add explicit version gates in your policy reference, or build your database from an older documentation commit:

```bash
git clone https://github.com/langchain-ai/docs .tmp/docs_langchain
git -C .tmp/docs_langchain checkout <the commit matching your baseline>
python3 scripts/build_docs_db.py --src .tmp/docs_langchain --out <your-db-path>
```

The build stamps that commit into `meta.source_commit`, so your fork's database says which baseline it represents. That is the whole point of the stamp.

## The rule you cannot skip

Whatever you change, the two skill trees must stay byte-identical:

```bash
diff -rq .claude/skills/langchain plugins/skills-for-langchain/skills/langchain
```

`scripts/validate_evidence.py` enforces this by SHA-256 across every file, including the database. `build_docs_db.py` has a `--mirror` flag so a rebuild can write both copies in one pass:

```bash
python3 scripts/build_docs_db.py \
  --src .tmp/docs_langchain \
  --out .claude/skills/langchain/references/docs_official.db \
  --mirror plugins/skills-for-langchain/skills/langchain/references/docs_official.db
```

If you publish your fork, also change the plugin and marketplace `name` fields so your build does not collide with this one in a user's Claude Code installation.

## After any customization

```bash
python3 scripts/validate_docs_db.py
python3 scripts/validate_evidence.py
claude plugin validate .claude-plugin/marketplace.json --strict
claude plugin validate plugins/skills-for-langchain/.claude-plugin/plugin.json --strict
```

Then test it for real, in a session started outside the repository, and confirm the skill actually queries your database — see [Getting Started](Getting-Started.md).

---

**Next:** [Maintenance and Release](Maintenance-and-Release.md) for the refresh procedure, or [Validation and Evidence](Validation-and-Evidence.md) for what the checks prove.

Back to the [documentation index](README.md).
