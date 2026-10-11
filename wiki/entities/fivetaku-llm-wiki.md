---
title: fivetaku llm-wiki
type: tool
aliases:
  - fivetaku/llm-wiki
sources:
  - 2026-10-11-github-fivetaku-llm-wiki @ README
updated: 2026-10-11T15:21:00+09:00
status: draft
tool_version: unreleased
---
A Korean-language starter workspace (fivetaku/llm-wiki, MIT) that implements the pattern in [[llm-wiki-pattern]] for Claude Code.

## What it does
Four layers (inbox, raw, wiki and a schema of CLAUDE.md plus a system folder), with numbered folders for the first three and slash commands for ingest, compile, query and lint. The index acts as a router: canonical names and aliases decide which type or shard to open, and large indexes are sharded by the first letter of the canonical name.

## Limits
Written in Korean; built for Claude Code. It presents itself as a starter, not a finished answer. No tagged release exists, so the version is recorded as unreleased (GitHub shows no releases, checked 2026-10-11).

## Disagreements
None found.
