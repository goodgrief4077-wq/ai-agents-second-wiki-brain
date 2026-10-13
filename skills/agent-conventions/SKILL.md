---
name: agent-conventions
description: Operating conventions for an AI coding agent working for one person. Use when about to do something outward-facing or hard to undo (create or delete a repo, push, open a PR, publish, send), when asked to delete or clean up files, when a task needs root privileges the agent cannot get, when a token or login keeps failing after a fix, or when looking up papers and books. Each topic is a sibling file; read only the one that matches.
---

# agent-conventions

Short, agent-neutral rules learned from real mistakes. Read the one sibling file that matches the task; do not load them all.

| Situation | Read |
|---|---|
| Push, PR, publish, send, create or delete a repo, anything others can see | `outward-actions.md` |
| Delete, prune, clean up, free disk space | `safe-deletion.md` |
| A task needs sudo or another root-only step | `sudo-script.md` |
| A token or login "fixed" but still fails somewhere | `credential-trap.md` |
| Finding academic papers, open-access PDFs or books | `openalex-papers.md` |

Pointers to private notes belong in the user's local instruction file, not here. Use `<placeholders>` for anything personal.
