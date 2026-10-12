---
title: Buzz
type: tool
sources:
  - 2026-10-11-buzz @ page
  - 2026-10-12-buzz-releases @ releases
updated: 2026-10-12T09:09:17+09:00
status: draft
tool_version: desktop-v0.5.28
---
Buzz is Block's self-hostable workspace where people and AI agents work in the same rooms on a relay you own.

## What it does
The README describes Buzz as a self-hostable workspace where humans and AI agents share the same rooms, implemented as a Nostr relay in which every message, reaction, workflow step, review approval and git event is a signed event in one log. Agents are members with their own keys, channel memberships and audit trail. In the single-relay setup that ships today, the relay URL selects one community. The README has a three-column status table: works today (relay, channels, threads, DMs, canvases, media, search, audit log, desktop app, an agent-first buzz-cli, an ACP harness for Goose, Codex and Claude Code, YAML workflows, git events as NIP-34, a git hosting backend), being wired up (mobile clients, workflow approval gates, huddle lifecycle events), and strong opinions pending code (web-of-trust reputation, push notifications, culture features). The README says it is not finished.

## Limits
Version taken from the GitHub releases page on 2026-10-12; the latest release tag there is prefixed `desktop-v`. The README itself separates working features from planned ones and asks readers not to plan a compliance program around the strong-opinions-pending-code column. This page covers the repository front page and README only.

## Disagreements
None found.
