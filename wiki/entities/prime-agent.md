---
title: Prime Agent
type: tool
sources:
  - 2026-10-11-prime-agent @ page
  - 2026-10-12-prime-agent-releases @ releases
  - 2026-10-12-prime-agent-licence @ LICENSE
updated: 2026-10-12T09:26:58+09:00
status: draft
tool_version: v0.10.0
---
Prime Agent is Prime Intellect's open-source coding and research agent, built on a Recursive Language Model harness with durable, self-refining state.

## What it does
The README describes an open-source coding and research agent for general and long-running work, built on two ideas: a Recursive Language Model (context as variables, tools and sub-agents as function calls inside a persistent REPL) and a Continual Harness that stores supplemental prompts, memories, skill descriptions and subagent specifications as durable state. Features listed: a persistent Python REPL as the built-in model tool, built-in subagents, a refine command that applies small evidence-backed updates and never rewrites its immutable base prompt, executable skills as Python packages, daemon-backed background sessions that can be reattached, direct agent-to-agent messaging, compaction, persistent goals, heartbeats, schedules and a bounded autonomous mode with quality gates. It starts in the current directory and a login command selects a subscription or API-key provider. The README warns it runs model-generated Python and project commands with your user permissions and that its worker and kernel processes are not a security sandbox.

## Limits
Version taken from the GitHub releases page on 2026-10-12. The README marks the Decision API as experimental. A citation to an arXiv preprint is given in the README; this page does not assess that paper. This page covers the repository front page and README only. The LICENSE file is the MIT licence; GitHub's detector could not identify a licence.

## Disagreements
None found.
