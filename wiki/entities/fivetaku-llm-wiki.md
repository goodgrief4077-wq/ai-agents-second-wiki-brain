---
title: fivetaku llm-wiki
type: tool
aliases:
  - fivetaku/llm-wiki
sources:
  - 2026-10-11-github-fivetaku-llm-wiki @ README
updated: 2026-10-11T15:15:20+09:00
status: draft
tool_version: unreleased
---
A Korean-language starter workspace (fivetaku/llm-wiki, MIT) that implements the pattern in [[llm-wiki-pattern]] for Claude Code.

## What it does
Four layers in numbered folders (inbox, raw, wiki, schema) and slash commands for ingest, compile, query and lint. The index acts as a router: canonical names and aliases decide which type or shard to open, and large indexes are sharded by the first letter of the canonical name.

## Limits
Written in Korean; Claude Code only. It presents itself as a starter, not a finished answer. No tagged release exists, so the version is recorded as unreleased.

## Disagreements
- [CONFLICT] Files query answers back into a queries folder, which this wiki's own rule declines; see [[llm-wiki-pattern]].
