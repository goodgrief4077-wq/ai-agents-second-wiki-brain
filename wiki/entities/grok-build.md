---
title: Grok Build
type: tool
sources:
  - 2026-10-11-grok-build @ page
updated: 2026-10-11T15:57:30+09:00
status: draft
tool_version: unreleased
---
Grok Build is SpaceXAI's terminal-based AI coding agent, installed as the `grok` command.

## What it does
The README describes Grok Build (the `grok` command) as SpaceXAI's terminal-based AI coding agent. It runs as a full-screen TUI that understands your codebase, edits files, runs shell commands, searches the web and manages long-running tasks, interactively, headlessly for scripting and CI, or embedded in editors through the Agent Client Protocol (ACP). Prebuilt binaries are published for macOS, Linux and Windows through install scripts. The repository holds the Rust source for the CLI/TUI and agent runtime, synced periodically from the SpaceXAI monorepo, with a SOURCE_REV file recording the monorepo commit. Building from source needs Rust, DotSlash and protoc; macOS and Linux are supported build hosts and Windows builds are best-effort and not currently tested from this tree. The user guide in the repository lists MCP servers, skills, plugins, hooks, headless mode and sandboxing. The README says external contributions are not accepted.

## Limits
The GitHub releases page had no releases on 2026-10-11, so tool_version is `unreleased`; the README points to a changelog for released binaries. This page covers the repository front page and README only.

## Disagreements
None found.
