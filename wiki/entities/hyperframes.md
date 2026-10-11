---
title: HyperFrames
type: tool
sources:
  - 2026-10-11-hyperframes @ page
updated: 2026-10-11T16:07:52+09:00
status: draft
tool_version: v0.8.146
---
HyperFrames is an open-source framework for rendering HTML-based compositions into deterministic MP4 video, built to be driven by coding agents.

## What it does
The README describes HyperFrames as an open-source framework for turning HTML, CSS, media and seekable animations into deterministic MP4 videos, usable locally with the CLI, from AI coding agents with skills, or as the rendering core behind hosted authoring. It ships a Claude Code plugin and a standalone skills install, and says it publishes 21 skills that agents load on demand, with a router skill that picks a workflow for requests such as a video, deck or composition port. It lists agents including Claude Code, Codex, Cursor and Gemini CLI as able to use the skills. The documented production loop is plan the video, write valid HTML, wire seekable animations, add media, lint, preview and render. The repository uses Git LFS.

## Limits
Version taken from the GitHub releases page on 2026-10-11. The README notes that the skills.sh registry copy can lag the main branch by hours, so installed skills may differ from the current repository. This page covers the repository front page and README only.

## Disagreements
None found.
