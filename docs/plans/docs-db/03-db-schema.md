# 03 — Database schema

Single file: `references/docs_official.db` (SQLite 3, FTS5 required — ships with CPython's bundled SQLite on macOS/Linux; the build should assert `sqlite3` has FTS5 via `PRAGMA compile_options`).

## DDL

```sql
-- One row per selected doc file (~187 rows).
CREATE TABLE docs (
    id       INTEGER PRIMARY KEY,
    path     TEXT NOT NULL UNIQUE,   -- e.g. 'deepagents/dynamic-subagents.mdx' (src/oss/ stripped)
    package  TEXT NOT NULL,          -- langchain | langgraph | deepagents | concepts | reference | migrate | releases
    title    TEXT,                   -- frontmatter title
    tag      TEXT,                   -- 'Beta' | 'experimental' | NULL
    url      TEXT,                   -- canonical docs.langchain.com URL
    body     TEXT NOT NULL           -- cleaned Markdown, snippets inlined, :::js stripped
);
CREATE INDEX idx_docs_package ON docs(package);

-- Full-text search over title + body. External-content table → no body duplication.
CREATE VIRTUAL TABLE docs_fts USING fts5(
    title, body,
    content='docs', content_rowid='id',
    tokenize='porter unicode61'
);
-- Triggers to keep FTS in sync (safe even though we build once).
CREATE TRIGGER docs_ai AFTER INSERT ON docs BEGIN
    INSERT INTO docs_fts(rowid, title, body) VALUES (new.id, new.title, new.body);
END;
CREATE TRIGGER docs_ad AFTER DELETE ON docs BEGIN
    INSERT INTO docs_fts(docs_fts, rowid, title, body) VALUES('delete', old.id, old.title, old.body);
END;
CREATE TRIGGER docs_au AFTER UPDATE ON docs BEGIN
    INSERT INTO docs_fts(docs_fts, rowid, title, body) VALUES('delete', old.id, old.title, old.body);
    INSERT INTO docs_fts(rowid, title, body) VALUES (new.id, new.title, new.body);
END;

-- Parsed from releases/changelog.mdx.
CREATE TABLE changelog (
    id       INTEGER PRIMARY KEY,
    date     TEXT,     -- ISO 'YYYY-MM-DD' (convert from 'Mon DD, YYYY')
    package  TEXT,
    version  TEXT,
    summary  TEXT
);
CREATE INDEX idx_changelog_pkg ON changelog(package, date);

-- Provenance / version stamp (single row, or key-value rows).
CREATE TABLE meta (
    key   TEXT PRIMARY KEY,
    value TEXT
);
-- rows: snapshot_date, built_at, source_repo, source_commit, doc_count, schema_version
```

Store the schema-and-examples text where Claude can see it: it lives in `SKILL.md` (05), not only in the DB. Optionally also insert the example queries into `meta` for self-description.

## Canonical queries (these go verbatim into SKILL.md)

```sql
-- 1. Concept search, ranked (FTS5). Prefer this over LIKE.
SELECT d.path, d.title, snippet(docs_fts, 1, '[', ']', ' … ', 12) AS excerpt
FROM docs_fts JOIN docs d ON d.id = docs_fts.rowid
WHERE docs_fts MATCH 'dynamic subagent'
ORDER BY rank
LIMIT 5;

-- 2. Search within a package.
SELECT d.path, d.title
FROM docs_fts JOIN docs d ON d.id = docs_fts.rowid
WHERE d.package = 'deepagents' AND docs_fts MATCH 'interrupt OR human'
ORDER BY rank LIMIT 8;

-- 3. Read a full doc (after a search points you at it).
SELECT body FROM docs WHERE path = 'deepagents/dynamic-subagents.mdx';

-- 4. What changed, most recent first.
SELECT date, package, version, summary
FROM changelog ORDER BY date DESC LIMIT 15;

-- 5. Version/provenance of this DB.
SELECT key, value FROM meta;
```

**FTS5 `MATCH` notes to put in SKILL.md** (the one real ergonomic cost of raw SQL):
- Multi-word `'dynamic subagent'` means "both terms" (implicit AND with proximity via the ranker); use `OR` explicitly for alternatives; `"exact phrase"` in double quotes for phrases.
- A bare hyphen/parenthesis in a query term can be parsed as an operator — wrap odd tokens in double quotes (e.g. `'"with_fallbacks"'`).
- Use `column : term` to scope, e.g. `title : middleware`.

## How Claude invokes it

Through the `sqlite3` CLI in Bash, e.g.:
```bash
sqlite3 -readonly .claude/skills/langchain/references/docs_official.db \
  "SELECT d.path, d.title FROM docs_fts JOIN docs d ON d.id=docs_fts.rowid WHERE docs_fts MATCH 'model fallback' ORDER BY rank LIMIT 5;"
```
Always `-readonly`. Path is relative to the repo the skill runs in; SKILL.md gives the exact relative path (it resolves inside the plugin install too, since the DB is mirrored into the plugin copy).
