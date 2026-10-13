---
name: slim-agent-instructions
description: Use when the user says "my AGENTS.md / CLAUDE.md is too long", "split the instruction file", "set up AGENTS.md for a new project", or an agent keeps ignoring or misapplying project rules. Slims always-loaded agent instruction files by moving task detail into linked docs. Do not use for writing a skill (use a skill-writing skill) or for auditing over-prompting (use an over-prompting audit).
license: MIT
metadata:
  version: "1.0"
  updated: "2026-10-13"
  source: "Web Dev Simplified video 'Why Your AI Generates Crap Code' (summarised in own words)"
---

# Slim agent instruction files

The instruction file (AGENTS.md, CLAUDE.md, GEMINI.md: same thing under different names) is sent with every request. A long one costs tokens on every task and drowns the rules that matter. Keep it small; put detail where it is read only when needed.

## Steps

1. **Measure first.** Count lines and rough tokens (characters / 4). Note the numbers; they are the before/after proof.
2. **Sort every section** into one of three bins:
   - *Always relevant* (what the project is, package manager, non-standard scripts, high-level layout): stays.
   - *Only for one kind of task* (testing, styling, PRs, a framework, an API): moves to its own doc, e.g. `docs/<topic>.md`.
   - *One-off procedure* (how auth works, how to run a release): becomes a skill, or its own doc if no skill system.
3. **Replace each moved section with one line**: when to read it plus the path. Docs may link to each other.
4. **Cut what an agent does not need**: getting-started and install steps, duplicated rules, file-by-file maps (they go stale; keep layout at folder level).
5. **One file, many names.** Make CLAUDE.md and GEMINI.md point at or link to AGENTS.md so they cannot drift. On Windows a link needs `mklink` (admin) or a PowerShell junction/symlink; the fallback is a one-line "read AGENTS.md" stub.
6. **Monorepos:** put a small AGENTS.md inside each package with only that package's rules. The agent loads the root file plus the file of the folder it was started in, not of the file it edits.
7. **Verify.** Re-count lines and tokens; confirm every moved block exists verbatim at its new path (hash or diff) and every link resolves.

## Growing a file from scratch

Start with two or three sentences: what the project is, the package manager, the layout. Do not ask an agent to "read the repo and write AGENTS.md"; the result is long and generic. Add a rule only after the agent gets something wrong, in the doc for that topic, and describe the actual mistake.

## Gotchas

- Moving text is not deleting it: keep dated notes and move blocks verbatim, then trim in a separate pass.
- A short root file that links to one huge file has only moved the problem; split the big file by topic.
- Never put secrets, personal paths or account names in a file that may be shared or public.
- Back up the original before editing; show the owner the before/after counts.
