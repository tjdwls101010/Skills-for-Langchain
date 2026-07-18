# 04 — `scripts/build_docs_db.py`

Stdlib-only Python 3.10+ (match the harness scripts). No third-party deps, no network at build time (the clone is a separate manual/scripted step). Deterministic and idempotent: running it twice on the same clone yields the same DB.

## CLI

```
python scripts/build_docs_db.py \
    --src .tmp/docs_langchain \
    --out .claude/skills/langchain/references/docs_official.db \
    [--commit <sha>]          # source_commit for meta; else read from .tmp/.../.git
    [--mirror plugins/skills-for-langchain/skills/langchain/references/docs_official.db]
```

Behavior: build to a temp path, validate (see 06 checks), then atomically move to `--out`. If `--mirror` is given, copy the finished file there too (or leave mirroring to the release step — see 06/07).

## Pipeline

1. **Preflight.** Assert `--src` exists and contains `src/oss/`. Assert the running `sqlite3` has FTS5 (`PRAGMA compile_options` contains `ENABLE_FTS5`); if not, fail with a clear message.

2. **Collect files.** Apply the include globs from `02-corpus-and-clone.md`; skip excluded trees. Build a list of `(abs_path, rel_path, package)` where `rel_path` strips the leading `src/oss/` and `package` is derived from the first path segment (with `python/migrate` → `migrate`, `python/releases` → `releases`).

3. **Build a snippet index.** Walk `src/snippets/` once into a dict: `'/snippets/<...>' -> file content`. Import statements reference the `/snippets/...` absolute-from-site path; normalize both sides to compare.

4. **Process each file** (per `02` §"Per-file processing"):
   a. Split frontmatter; extract `title`, `tag`.
   b. Collect `import NAME from '/snippets/....mdx';` lines into a local map `NAME -> resolved content` (via the snippet index). Missing target → raise, abort build.
   c. Remove the import lines; replace each `<NAME />` (and `<NAME/>`) with the resolved content.
   d. Strip `:::js ... :::` spans; unwrap `:::python ... :::`.
   e. Assert no residual `<CapitalizedName />` snippet-style render tags remain that correspond to a dropped import (a targeted check, not a blanket "no JSX" — real prose may contain `<Note>` etc.). Concretely: after substitution, none of the imported `NAME`s may still appear as a tag.
   f. Compute `url`.
   g. Insert into `docs`.

5. **Parse changelog** from `releases/changelog.mdx` into `changelog` rows (per `02` §"Changelog extraction"). Convert `'Mon DD, YYYY'` → ISO date.

6. **Write `meta`:** `snapshot_date` (max changelog date, or clone date), `built_at` (pass in or derive — note: the harness workflow tools forbid `Date.now()`, but this is a normal Python CLI run by the user, so `datetime.now()` is fine here), `source_repo`, `source_commit`, `doc_count`, `schema_version='1'`.

7. **Finalize FTS.** With the triggers in place, inserts populate `docs_fts` automatically; run `INSERT INTO docs_fts(docs_fts) VALUES('optimize');` at the end. `PRAGMA optimize;` and `VACUUM;` to keep the file compact.

8. **Self-validate** (fail non-zero on any): `doc_count` within a sane band (e.g. 150–250), zero unresolved snippet tags (tracked during step 4), `changelog` non-empty, `SELECT count(*) FROM docs_fts WHERE docs_fts MATCH 'agent'` > 0, `meta` fully populated.

9. **Report.** Print per-package counts, total rows, snippet substitutions made, changelog rows, final file size. Anything the user should eyeball on a refresh.

## Notes for the implementer

- Keep the MDX cleaning **conservative**. The goal is faithful, snippet-complete Markdown, not a perfect MDX→MD compiler. Over-aggressive stripping risks deleting real content; the only *mandatory* transforms are snippet inlining and `:::js` removal.
- The two `code-samples` locations (`src/code-samples` and `src/snippets/code-samples`) both exist; imports in the core docs use the `/snippets/...` form, so index `src/snippets/`. If any core import resolves to `src/code-samples/` instead, index both and prefer an exact path match.
- Size expectation: core body text ≈ 3.4 MB pre-snippet; with snippets inlined and FTS index, expect a `.db` in the ~4–8 MB range. Flag in the report if it balloons past ~20 MB (a sign integrations leaked in).
