# 02 — Corpus & clone

## Source

- **Repo:** `https://github.com/langchain-ai/docs`
- **Docs root inside the repo:** `src/oss/`
- **Snippets root:** `src/snippets/` (specifically `src/snippets/code-samples/`, 900 files) — this lives *outside* `src/oss/`, which is why the original `src/oss`-only snapshot lost every imported code sample.

## Clone command (refresh step 1)

```bash
rm -rf .tmp/docs_langchain
git clone --depth 1 https://github.com/langchain-ai/docs .tmp/docs_langchain
```

`.tmp/` is gitignored and throwaway. `--depth 1` skips history (the full repo is ~583 MB; shallow is smaller/faster). Record the resolved commit for the `meta` table:

```bash
git -C .tmp/docs_langchain rev-parse HEAD
```

## Core selection (what goes INTO the db)

Include exactly these, relative to `.tmp/docs_langchain/`:

| Glob | Package tag | Count (2026-07-18) |
|---|---|---|
| `src/oss/langchain/**/*.mdx` | `langchain` | 73 |
| `src/oss/langgraph/**/*.mdx` | `langgraph` | 42 |
| `src/oss/deepagents/**/*.mdx` | `deepagents` | 53 |
| `src/oss/concepts/**/*.mdx` | `concepts` | 4 |
| `src/oss/reference/**/*.mdx` | `reference` | 9 |
| `src/oss/python/migrate/**/*.mdx` | `migrate` | (part of 6) |
| `src/oss/python/releases/**/*.mdx` | `releases` | (part of 6) |

Total ≈ **187**. Counts are a sanity check, not a hard gate — a refresh may legitimately shift them. The build should `log` the per-package counts so drift is visible.

**Explicitly excluded:** `src/oss/javascript/**` (Python skill), `src/oss/python/integrations/**` (parts catalog, 579 files), all `images/`, `*.png/jpg/gif/mp4/svg/mmd`.

## Per-file processing (build, before storing `body`)

For each selected `.mdx`:

1. **Parse frontmatter** (the leading `--- ... ---` block): capture `title`, and `tag` if present (e.g. `Beta`, `experimental`). Frontmatter is YAML — a tiny hand parser is fine, but stdlib has no YAML; either add a minimal key:value reader (frontmatter here is shallow) or vendor nothing and parse the few keys you need with regex. **Do not** add a third-party dep.

2. **Resolve snippet imports (mandatory — D5).** MDX files declare imports like:
   ```
   import DynamicSubagentsQuickstartPy from '/snippets/code-samples/dynamic-subagents-quickstart-py.mdx';
   ```
   and render them later as `<DynamicSubagentsQuickstartPy />`. For every such import:
   - Map the `/snippets/...` path to `.tmp/docs_langchain/src/snippets/...`.
   - Read that file's content and substitute it in place of the `<Name />` tag.
   - Drop the `import ... from ...;` line itself.
   - If a referenced snippet file is missing → **build error** (fail loudly; do not store a doc with an unresolved tag).

3. **Strip JS-only conditional blocks (D11.2).** Docs use `:::python ... :::` and `:::js ... :::` fenced conditionals for language variants. Remove the `:::js ... :::` spans entirely; unwrap `:::python ... :::` to its inner content. This keeps the Python-only skill from ever surfacing JS as if it were Python. (Snippet files themselves may contain a `<CodeGroup>` with multiple *provider* variants — Google/OpenAI/Anthropic — keep those; they are providers, not languages.)

4. **Leave the rest as Markdown.** `<Note>/<Tip>/<Warning>` prose blocks, headings, tables, and inline ```bash```/```python``` fences stay. Claude reads Markdown fine; no need to strip every MDX component. The only hard requirement is: no unresolved snippet render-tags remain.

5. **Compute `url`** (D11.3): `src/oss/<rest>.mdx` → `https://docs.langchain.com/oss/<rest>`. Strip a trailing `/index` if the repo uses index files.

## Changelog extraction

`src/oss/python/releases/changelog.mdx` is a series of `<Update label="Mon DD, YYYY" tags={["deepagents"]}>` blocks, each containing `## \`package\` vX.Y.Z` headings and bullet lists. Parse each `<Update>` into one or more `changelog` rows: `date` (from `label`), `package` (from `tags` and/or the `## \`pkg\`` heading), `version`, `summary` (the bullets, joined). This table powers "what changed when" queries and is a second signal for the `meta` snapshot date. The changelog doc is *also* stored as a normal row in `docs` (it's in the `releases` set).
