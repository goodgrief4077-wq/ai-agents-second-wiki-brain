---
title: Ollama
type: tool
sources:
  - 2026-10-11-ollama @ page
  - 2026-10-12-ollama-releases @ releases
updated: 2026-10-12T09:11:44+09:00
status: draft
tool_version: v0.40.3
---
Ollama is a tool for running open models locally through a CLI and REST API, with launchers for several coding agents.

## What it does
The README presents Ollama as a way to start building with open models. It installs on macOS, Windows and Linux with scripts or manual download, and ships as an official Docker image. Running the ollama command prompts you to run a model or connect Ollama to existing agents or applications such as Claude Code, OpenClaw, OpenCode, Codex and Copilot, and a launch subcommand starts a named integration. It has a REST API on localhost port 11434 for chat and model management, plus ollama-python and ollama-js libraries. The README names the llama.cpp project as its supported backend. A long community-integrations list covers chat interfaces, desktop apps, package managers and more; the About line says it runs models including Kimi, GLM, MiniMax, DeepSeek, gpt-oss, Qwen and Gemma.

## Limits
Version taken from the GitHub releases page on 2026-10-12. Model names and integration lists in the README change often; the model library lives at ollama.com/library, not in this repository. This page covers the repository front page and README only.

## Disagreements
None found.
