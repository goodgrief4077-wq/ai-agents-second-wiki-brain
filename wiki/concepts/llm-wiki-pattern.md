---
title: LLM Wiki pattern
type: method
aliases:
  - Karpathy LLM Wiki
  - compiled knowledge wiki
sources:
  - 2026-10-11-karpathy-llm-wiki-gist @ The core idea
  - 2026-10-11-karpathy-llm-wiki-gist @ Operations
  - 2026-10-11-karpathy-llm-wiki-gist @ Indexing and logging
  - 2026-10-11-github-fivetaku-llm-wiki @ README
updated: 2026-10-11T15:15:20+09:00
status: draft
---
A way to keep knowledge in a persistent, LLM-maintained markdown wiki that sits between the user and raw sources, so knowledge is compiled once and kept current instead of being re-derived from raw documents on every question.

## When it applies
Accumulating knowledge over weeks or months (research, a book, a team wiki) where RAG would rediscover the same facts each time. The source itself calls the idea deliberately abstract; the folder layout and schema are left to the user and agent.

## Steps
1. Keep three layers: immutable raw sources, an LLM-owned wiki, and a schema file that tells the agent the conventions. (src: 2026-10-11-karpathy-llm-wiki-gist @ Architecture)
2. Ingest one source at a time: read it, summarise, update related pages, update the index, add a log entry. (src: 2026-10-11-karpathy-llm-wiki-gist @ Operations)
3. Maintain an index as the entry point and an append-only log with a consistent entry prefix. (src: 2026-10-11-karpathy-llm-wiki-gist @ Indexing and logging)
4. Lint periodically for contradictions, stale claims, orphans and missing pages. (src: 2026-10-11-karpathy-llm-wiki-gist @ Operations)

## Disagreements
- [CONFLICT] Index design. The gist describes an index as a catalogue of every page, enough up to roughly 100 sources. The fivetaku starter uses the index as a router that picks a type or shard from canonical names, so the tokens read per question stay constant as the wiki grows. See [[fivetaku-llm-wiki]].
- [CONFLICT] Filing answers back. The gist suggests good query answers be filed back as pages; the fivetaku starter files them in a queries folder. This wiki's own rule is that queries never write (poisoning risk); that is a local choice, not a claim by either source.
