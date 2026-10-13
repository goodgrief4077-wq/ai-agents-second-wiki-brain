---
name: skill-shelf
description: Use when the user says "don't we have a skill for this", "is there a skill", "use a skill", or the task may match a specialised skill, or when asked "is there a skill for X" / "use a skill". Skills are stored on a shelf and are NOT auto-loaded; this finds and loads the one needed. Works with any agent.
---

# Skill shelf (any agent)

About 650 skills sit in `~/.agents/skill-shelf/`. They are deliberately not auto-loaded, to save context.

1. Search the index, never read it whole: `grep -i "<keyword>" ~/.agents/skill-shelf/INDEX.md` (try 2-3 keywords).
2. Pick the best match, then read `~/.agents/skill-shelf/<name>/SKILL.md` and follow it. Resolve its relative file references against that folder.
3. Load only what the task needs. Several matches: read the descriptions, load one.
4. Never copy or move a skill into `~/.agents/skills/` or any agent's own skills folder; that re-enables auto-loading. Add new skills to the shelf and re-run the index generation (the python block recorded in `~/.agents/skill-shelf/README.md`).
