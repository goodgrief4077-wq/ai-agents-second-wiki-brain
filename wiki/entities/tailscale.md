---
title: Tailscale
type: tool
sources:
  - 2026-10-11-tailscale-docs-what-is-tailscale @ page
  - 2026-10-11-github-tailscale-tailscale @ page
updated: 2026-10-11T16:19:09+09:00
status: draft
tool_version: v1.104.1
---
Tailscale is a WireGuard-based connectivity service that links devices into a private peer-to-peer network called a tailnet.

## What it does
The "What is Tailscale?" page describes an identity-based, zero-trust connectivity platform that uses the open-source WireGuard protocol for encrypted point-to-point connections. Devices form a mesh tailnet, and traffic can still be routed through an exit node like a traditional VPN. The page highlights setup in minutes without port forwarding, working across firewalls and NAT, a security model of end-to-end encryption and access control policies, and uses from developers and homelabs to enterprises. The repository README says the open-source repo holds the tailscaled daemon and the tailscale CLI, runs on Linux, Windows and macOS (with varying support on FreeBSD and OpenBSD), and that the GUI wrappers on some platforms are not open source.

## Limits
Version taken from the GitHub releases page on 2026-10-11. The docs page carries a "Last validated" date of 2025-09-30. The repo covers client code only; some clients and GUI wrappers are not open source. This page covers the overview page and repository front page only.

## Disagreements
None found.
