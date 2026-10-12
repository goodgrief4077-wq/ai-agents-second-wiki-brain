---
title: Machine Payments Protocol
type: tool
sources:
  - 2026-10-11-mpp @ page
  - 2026-10-12-mpp-releases @ releases
updated: 2026-10-12T09:11:31+09:00
status: draft
tool_version: unreleased
---
The Machine Payments Protocol (MPP) is an open protocol for machine-to-machine payments over an HTTP 402 flow; this repository is its documentation site.

## What it does
The README describes MPP as an open standard for machine-to-machine payments, co-authored by Tempo and Stripe, with its core published as an IETF specification. It lets agents, apps and people pay inline with a request through an HTTP 402 Payment Required flow, instead of setting up API keys, billing accounts or checkout flows first. Named use cases are agentic payments, usage-based billing and machine-to-machine commerce. This repository is the source of the mpp.dev site: documentation, protocol explainers, SDK references and a curated directory of live MPP-enabled services. SDKs are listed in separate repositories for Go, Python, Ruby, Rust and TypeScript; the normative specification source is in a separate mpp-specs repository.

## Limits
The GitHub releases page had no releases on 2026-10-12, so tool_version is `unreleased`. The repository is the documentation site, not the protocol implementation or the specification text, so this page describes the project, not protocol details. This page covers the repository front page and README only.

## Disagreements
None found.
