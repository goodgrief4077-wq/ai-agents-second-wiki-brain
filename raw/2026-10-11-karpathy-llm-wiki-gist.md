---
source_kind: web
url: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
retrieved: 2026-10-11T15:13:22+09:00
licence_note: unknown (no licence stated on the gist)
archive_status: saved
archive_url: http://web.archive.org/web/20261009173323/https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
archive_timestamp: 2026-10-09T17:33:23+00:00
body_sha256: a23c3b0aa152924ad73054e70dcc0a3c5206ff3b8067d76906d86c3e28b8ea00
read_via: raw
verify_by: hash
---
Karpathy's idea file "LLM Wiki", created 2026-04-04. It argues that an LLM should incrementally build and maintain a persistent, interlinked markdown wiki between the user and raw sources, instead of re-deriving answers from raw documents on every query as RAG does. It describes three layers (immutable raw sources, an LLM-owned wiki, a schema file) and three operations (ingest, query, lint), plus a content-oriented index file and an append-only log file. It suggests good query answers can be filed back as wiki pages and names qmd as an optional search tool once the index file is no longer enough. The text says it is deliberately abstract and leaves the implementation to the user and their agent.
