---
title: MCP for Blender
type: tool
sources:
  - 2026-10-11-mcp-for-blender @ page
  - 2026-10-12-mcp-for-blender-releases @ releases
updated: 2026-10-12T09:11:17+09:00
status: draft
tool_version: unreleased
---
MCP for Blender is a third-party MCP server and Blender addon that lets LLM clients drive Blender for 3D modelling.

## What it does
The README describes MCP for Blender as a way to connect Blender to any LLM through MCP, for prompt-assisted 3D modelling, scene creation and manipulation. It was formerly named blender-mcp, and the PyPI package is now mcp-for-blender with existing setups said to keep working. A setup command finds MCP clients on the machine (it names Claude Desktop, Claude Code, Codex, Cursor, VS Code, OpenCode and others), adds a blender entry to their config while keeping a backup, and installs the Blender addon. Manual setup is uv, an MCP client entry that runs the server through uvx, and the addon enabled in Blender preferences. The addon starts its server when Blender opens. The README says to run only one instance of the MCP server.

## Limits
The GitHub releases page had no releases on 2026-10-12, so tool_version is `unreleased`. The README carries a disclaimer that this is a third-party integration, not made by Blender. The README mentions a premium tier and a long table of contents that were not read in full. This page covers the repository front page and README only.

## Disagreements
None found.
