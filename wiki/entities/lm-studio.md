---
title: LM Studio SDK (lmstudio-js)
type: tool
sources:
  - 2026-10-11-lm-studio @ page
updated: 2026-10-11T16:07:52+09:00
status: draft
tool_version: unreleased
---
lmstudio-js is LM Studio's official TypeScript SDK for driving locally run models from JavaScript and Node code.

## What it does
The README describes lmstudio-js as LM Studio's official JavaScript client SDK, written in TypeScript, for browser and Node-compatible environments. It lets code respond in chats or predict text completions, define functions as tools to build locally run autonomous agents, load, configure and unload models, and generate embeddings. A Python SDK is linked separately. It argues for itself over the OpenAI SDK because that SDK lacks local-model features such as managing model loading, configuring load parameters (context length, GPU offload), speculative decoding and reading model information. It is installed as an npm package.

## Limits
The GitHub releases page had no releases on 2026-10-11, so tool_version is `unreleased`. The repository tags use hash-style names, not version numbers. This page covers the SDK repository, not the LM Studio desktop app, which is a separate product. This page covers the repository front page and README only.

## Disagreements
None found.
