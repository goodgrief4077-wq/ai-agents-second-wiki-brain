---
title: GBrain
type: tool
sources:
  - 2026-10-11-gbrain @ page
  - 2026-10-12-gbrain-releases @ releases
updated: 2026-10-12T09:10:13+09:00
status: draft
tool_version: 0.60.175.0
---
GBrain is a memory layer for AI agents, published by Garry Tan, that stores sourced facts and shares them across agents.

## What it does
The README describes GBrain as memory you control for the agent you already use: explicit facts stored with sources, with support for corrections and withdrawal, shared across agents. It starts keyless with keyword retrieval; semantic search, synthesis and background enrichment are optional additions. Setup paths named are: add it to an existing agent (guides for Grok Bot, Muse and Codex / Claude Code), expose your own brain over MCP with `gbrain mcp expose` (optionally on a Tailscale tailnet), or connect an existing hosted brain. It also offers a synthesis layer that answers with citations and notes what the brain does not know, and a typed knowledge graph. The README states one benchmark result (BrainBench relationship questions, graph adapter P@5 0.3421, R@5 0.9791 against 0.1917 / 0.6874 for plain hybrid, 2026-09-09 refresh) and says it is not a general guarantee. The author states it is the production brain behind their OpenClaw and Hermes deployments. Install requires Bun 1.4.0 or newer; the README says GBrain is NOT distributed on npm and that the npm package named gbrain is unrelated.

## Limits
Version taken from the GitHub releases page on 2026-10-12. Benchmark and size figures are the author's own, as printed on the README. The README says configured cloud providers can receive text and that Markdown export is not a full database backup. This page covers the repository front page and README only.

## Disagreements
None found.
