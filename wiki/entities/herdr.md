---
title: herdr
type: tool
sources:
  - 2026-10-11-herdr @ page
  - 2026-10-12-herdr-releases @ releases
updated: 2026-10-12T09:26:58+09:00
status: draft
tool_version: 0.9.3
---
herdr is a terminal runtime for coding agents, written in Rust and described as the runtime your coding agents live on.

## What it does
The README describes herdr as a runtime coding agents live on, shipped as one Rust binary with no Electron, running in whatever terminal you already use. It keeps terminals running in a background server so you can detach and reattach, including after losing an SSH connection; after a server or machine restart it restores the saved layout and can resume supported agent sessions, but the original processes do not survive. It can combine local work and saved SSH machines in one window. Each pane is marked working, blocked or idle. Agents can drive herdr through its CLI and socket API to spawn panes, prompt each other and wait until another agent is blocked. It runs agents such as Claude Code, Codex, Cursor, OpenCode and Grok without wrapping or replacing them. It supports tmux-style prefix keys as well as mouse use, and a plugin marketplace. Install is a script, Homebrew, mise, or a PowerShell script on Windows.

## Limits
Version taken from the GitHub releases page on 2026-10-12. This page covers the repository front page and README only, not the docs at herdr.dev.

## Disagreements
None found.
