---
title: qmd
type: tool
aliases:
  - tobi/qmd
  - Query Markup Documents
sources:
  - 2026-10-11-github-tobi-qmd @ README
  - "2026-10-11-karpathy-llm-wiki-gist @ Optional: CLI tools"
updated: 2026-10-11T15:21:00+09:00
status: draft
tool_version: 2.8.3
---
A local, on-device search engine for markdown notes and documents (tobi/qmd, MIT). The Karpathy gist names it as an optional search tool once an index file is no longer enough; see [[llm-wiki-pattern]].

## What it does
Combines BM25 full-text search, vector search and LLM re-ranking, run locally through node-llama-cpp with GGUF models. Collections can carry context strings that are returned with matching documents. Exposes JSON and file-list output for agents and an MCP server with query, get, multi-get, status and metadata tools.

## Limits
Runs local models, so it needs disk and compute. The README documents install through npm or bun. Version taken from the GitHub releases page on 2026-10-11.

## Disagreements
None found.
