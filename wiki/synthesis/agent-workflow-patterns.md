---
title: Agent workflow patterns
type: synthesis
sources:
  - 2026-10-11-building-effective-agents @ page
  - 2026-10-11-claude-cookbooks-agent-patterns @ page
updated: 2026-10-11T16:04:03+09:00
status: draft
---
Anthropic's guidance on agentic systems separates fixed workflows from model-directed agents and names a small set of workflow patterns, with minimal notebook implementations in its cookbook.

## Findings
- The post distinguishes workflows, where LLMs and tools are orchestrated through predefined code paths, from agents, where the LLM directs its own process and tool use. (2026-10-11-building-effective-agents @ page)
- It recommends the simplest solution that works, increasing complexity only when needed, and says optimising single LLM calls with retrieval and examples is usually enough. (2026-10-11-building-effective-agents @ page)
- It advises starting with LLM APIs directly and understanding any framework's underlying code, because framework abstractions can obscure prompts and responses. (2026-10-11-building-effective-agents @ page)
- Building block: an LLM augmented with retrieval, tools and memory. (2026-10-11-building-effective-agents @ page)
- Workflow patterns named: prompt chaining, routing, parallelization (sectioning and voting), orchestrator-workers, evaluator-optimizer. (2026-10-11-building-effective-agents @ page)
- Agents are described as LLMs using tools based on environmental feedback in a loop, suited to open-ended problems and trusted environments, with higher cost and compounding-error risk; testing in sandboxes and guardrails are recommended. (2026-10-11-building-effective-agents @ page)
- Three stated principles: keep the design simple, show the agent's planning steps, and craft the agent-computer interface with thorough tool documentation and testing. (2026-10-11-building-effective-agents @ page)
- The cookbook directory holds minimal implementations of prompt chaining, routing, parallelization, orchestrator-subagents and evaluator-optimizer, as notebooks. (2026-10-11-claude-cookbooks-agent-patterns @ page)

## Disagreements
The post carries a note that much of the tooling it describes has changed since December 2024 and points readers to Anthropic's Managed Agents material for its current approach. This page records the 2024 patterns only.
