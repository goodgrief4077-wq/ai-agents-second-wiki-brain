---
title: LLM wiki maintenance
type: method
aliases:
  - knowledge drift review
sources:
  - 2026-10-11-glukhov-llm-wiki-maintenance @ A Simple Maintenance Loop
  - 2026-10-11-glukhov-llm-wiki-maintenance @ Types of Drift in an LLM Wiki
  - 2026-10-11-glukhov-llm-wiki-maintenance @ Source Drift
  - 2026-10-11-glukhov-llm-wiki-maintenance @ Decision Drift
  - 2026-10-11-glukhov-llm-wiki-maintenance @ Archive, Supersede, or Delete
  - 2026-10-11-glukhov-llm-wiki-maintenance @ What an LLM Wiki Linter Should Check
updated: 2026-10-11T15:21:00+09:00
status: draft
---
How to keep a compiled LLM wiki trustworthy over time. The article's thesis is that such a wiki can look clean while being wrong, so maintenance has to check both structure and meaning. It builds on [[llm-wiki-pattern]].

## When it applies
Any wiki where an agent rewrites pages across many ingests, so old facts stay plausible and summaries can drift from their sources.

## Steps
1. Record source dates and last-reviewed dates, and mark version-specific pages. (src: 2026-10-11-glukhov-llm-wiki-maintenance @ Source Drift)
2. Name the drift types you check for: source, concept, terminology, decision, citation, structure. (src: 2026-10-11-glukhov-llm-wiki-maintenance @ Types of Drift in an LLM Wiki)
3. Run structural lint, then semantic review, then human review of risky changes, then commit. (src: 2026-10-11-glukhov-llm-wiki-maintenance @ A Simple Maintenance Loop)
4. Keep superseded pages linked to their replacements instead of deleting them. (src: 2026-10-11-glukhov-llm-wiki-maintenance @ Archive, Supersede, or Delete)
5. Schedule a stale-page review. (src: 2026-10-11-glukhov-llm-wiki-maintenance @ A Simple Maintenance Loop)

## Disagreements
None found.
