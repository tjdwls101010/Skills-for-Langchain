# LangChain docs snapshot manifest

Source: official LangChain Python documentation pages under `docs.langchain.com/oss/python/`.
Captured state: local planning snapshot described as April 2026; the snapshot contains no Git metadata and is intentionally not vendored.
Recorded on: 2026-07-12
Included files: 1,139 (excluding `.DS_Store`)
Total bytes: 71,832,402
Aggregate SHA-256: `28f5d63f361de2d56b62118524401fa5aca3d08a8c993e7605aedb45f457fbed`

The aggregate is the SHA-256 of the sorted per-file SHA-256 lines, computed from the snapshot root:

```bash
find . -type f ! -name '.DS_Store' -print0 | LC_ALL=C sort -z | xargs -0 shasum -a 256 | shasum -a 256
```

This manifest can verify that a restored snapshot is byte-identical. It does not make the ignored snapshot reconstructible from this repository; fetching the live docs later creates a new source baseline and requires a new novelty survey, probe run, and manifest.
