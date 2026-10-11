---
title: OpenClaw
type: tool
sources:
  - 2026-10-11-openclaw @ page
updated: 2026-10-11T15:57:30+09:00
status: draft
tool_version: 2026.10.1
---
OpenClaw is an open-source personal AI assistant you run on your own devices and reach through the chat apps you already use.

## What it does
The README describes an open-source AI assistant that runs on your own computer and meets you in chat channels (Discord, iMessage, Slack, Teams, Telegram, WhatsApp and 20+ more) plus native apps for macOS, iOS, Android, Windows and Linux. A single Gateway is the local control plane for sessions, tools, events and channel connections; the Control UI, CLI and TUI connect to it. Models and agent harnesses (Claude, Codex, local models) are plugins that can be swapped. Tools, skills and plugins extend it, and ClawHub is named as the sharing place. The README says state, memory and credentials live on your hardware, and that by default it phones home only for a daily version check. Install is a script or an npm package (Node 24.16+ or 26.1+); onboarding is started with an onboard command. It says to treat inbound messages as untrusted, that unknown senders are paired by default, and that tools run on the host for the main session unless sandboxing is configured. The repository is a pnpm workspace and plain npm install at the root is not supported. It is stewarded by the OpenClaw Foundation, described as an independent 501(c)(3) with no paid tier, hosted service or token.

## Limits
Version taken from the GitHub releases page on 2026-10-11. This page covers the repository front page and README only, not the linked docs site. Install details change quickly; check the README at the pinned commit.

## Disagreements
None found.
