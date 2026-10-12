---
title: Cloudflare OS
type: tool
sources:
  - 2026-10-11-cloudflare-os @ page
  - 2026-10-12-cloudflare-os-releases @ releases
updated: 2026-10-12T09:09:31+09:00
status: draft
tool_version: unreleased
---
Cloudflare OS is an open-source agent workspace on Cloudflare Workers, built around sandboxed per-user apps and a capability-based security layer.

## What it does
The README describes Cloudflare OS as an operating system for AI productivity, originally built for use inside Cloudflare and now open source so other companies can customise it. It provides an agent chat UI preloaded with company knowledge, sandboxed application development where agents build small personal apps called gadgets, and a security framework called Gatekeepers. Each gadget is a private instance in its own sandbox. A Gatekeeper mediates access to one external service: it wraps the service API, handles authorisation, enforces narrow access, logs every action, and gives the human a chance to approve side-effecting actions. It runs locally on wrangler and workerd with one command for trying it out, or deploys to a Cloudflare account; self-hosting on workerd is marked coming soon. The README warns that this is version 2, a rewrite, in early access with rough edges, and that outside contributions are not currently sought beyond small verified fixes.

## Limits
The GitHub releases page had no releases on 2026-10-12, so tool_version is `unreleased`. The README calls the August 2026 release early access. A separate cloudflare-os-starter repository is named for customised deployments; it was not read for this page. This page covers the repository front page and README only.

## Disagreements
None found.
