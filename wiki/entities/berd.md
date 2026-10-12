---
title: Berd
type: tool
sources:
  - 2026-10-11-berd @ page
  - 2026-10-12-berd-releases @ releases
updated: 2026-10-12T09:09:03+09:00
status: draft
tool_version: v0.6.4
---
Berd is Block's open-source desktop app for working with AI agents, built with Tauri and React on top of the Goose backend.

## What it does
The README describes Berd as an open-source desktop app for working with AI agents, built with Tauri 2 and React 19, talking to the upstream Goose backend over an ACP WebSocket served by a goose serve sidecar. Setup uses just and pnpm and a Goose backend pinned by a lockfile. The repository builds a public distribution and has distribution seams so organisations can supply managed provider settings, private resources and release infrastructure for their own builds. It publishes portable Agent Skills under skills/, the first being buzz-handoff, which brings Buzz channel or thread context into a private agent conversation. The README says it is built by a small team at Block in the open and that pull requests from outside authorised collaborators are closed automatically; the way to participate is a well-formed issue.

## Limits
Version taken from the GitHub releases page on 2026-10-12. Outside pull requests are not accepted. The README is mostly build and distribution guidance, so user-facing features are thinly described. This page covers the repository front page and README only.

## Disagreements
None found.
