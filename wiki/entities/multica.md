---
title: Multica
type: tool
sources:
  - 2026-10-11-multica @ page
updated: 2026-10-11T16:04:03+09:00
status: draft
tool_version: v0.6.1
---
Multica is a source-available workspace for assigning issues to AI coding agents and reviewing their work, self-hostable on your own infrastructure.

## What it does
The README describes Multica as a workspace where you assign issues to AI coding agents like teammates: they pick up the issue, report progress, raise blockers and hand work back for review. It drives agent CLIs you already have (Claude Code, Codex, Cursor, Copilot, Kimi, OpenCode and others) and does not ship them; at least one must be installed and signed in on the machine that runs agents. Features listed: agents as board members, squads with a leader, reusable skills, autopilots on a cron, chat, projects, an execution log, steering a running agent (Claude Code, Codex and Grok per the README), usage analytics, review gates, retries and timeouts. It can be used as a cloud service, a desktop app, or self-hosted with Docker Compose or Helm. The README says a self-hosted server sends one anonymous daily deployment snapshot that can be switched off with DO_NOT_TRACK.

## Limits
Version taken from the GitHub releases page on 2026-10-11. The licence is described by the README as the Apache License 2.0 text plus additional conditions, so the project is source-available rather than plain open source; read the LICENSE before embedding or hosting. The README says the iOS app builds from source and is not yet on the App Store. This page covers the repository front page and README only.

## Disagreements
None found.
