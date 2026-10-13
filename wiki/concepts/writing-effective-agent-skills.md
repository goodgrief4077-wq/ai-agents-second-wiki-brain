---
title: Writing effective agent skills
type: method
aliases:
  - agent skills best practices
  - SKILL.md authoring
sources:
  - 2026-10-13-webdev-simplified-ai-skills @ 00:57
  - 2026-10-13-webdev-simplified-ai-skills @ 02:17
  - 2026-10-13-webdev-simplified-ai-skills @ 04:19
  - 2026-10-13-webdev-simplified-ai-skills @ 06:59
  - 2026-10-13-webdev-simplified-ai-skills @ 07:11
  - 2026-10-13-webdev-simplified-ai-skills @ 09:44
  - 2026-10-13-webdev-simplified-ai-skills @ 10:00
  - 2026-10-13-webdev-simplified-ai-skills @ 11:27
  - 2026-10-13-webdev-simplified-ai-skills @ 13:01
  - 2026-10-13-webdev-simplified-ai-skills @ 16:22
  - 2026-10-13-webdev-simplified-ai-skills @ 18:02
  - 2026-10-13-webdev-simplified-ai-skills @ 20:27
  - 2026-10-13-webdev-simplified-ai-skills @ 21:41
  - 2026-10-13-webdev-simplified-ai-skills @ 22:07
  - 2026-10-13-webdev-simplified-ai-skills @ 22:18
  - 2026-10-13-webdev-simplified-ai-skills @ 22:34
  - 2026-10-13-webdev-simplified-ai-skills @ 26:58
updated: 2026-10-13T11:34:00+09:00
status: draft
---
How to write and maintain an agent skill, as taught in one developer's video guide. A skill is a markdown file with a name and description in front matter; its body is loaded into the agent's context when the skill is invoked or auto-selected. The video argues that quality comes from your hands-on knowledge, a small body, and refining the skill over time, not from downloading many skills. Related: [[matt-pocock-skills]], [[claude-code]], [[pi-coding-agent]].

## When it applies
Any coding agent or editor that loads skills from a folder, when the agent keeps doing a task in a generic or wrong way and you want it to follow your own conventions. Also when judging a third-party skill before installing it.

## Steps
1. Know the format: a markdown file whose front matter requires a name and a description; everything else is optional. (src: 2026-10-13-webdev-simplified-ai-skills @ 00:57)
2. Know the loading model: invoking a skill pulls the whole body into context, and the name and description alone can let the agent pick it automatically. (src: 2026-10-13-webdev-simplified-ai-skills @ 02:17)
3. Before installing a third-party skill, read its markdown and scripts, because a skill can carry prompts that make the agent do unwanted things. (src: 2026-10-13-webdev-simplified-ai-skills @ 04:19)
4. Prefer project-level installs, which sit in the repo and can be locked to a version; use global installs only for skills needed everywhere. (src: 2026-10-13-webdev-simplified-ai-skills @ 06:59)
5. Check the security audit shown for a skill in its directory listing and read why a risk was flagged before deciding. (src: 2026-10-13-webdev-simplified-ai-skills @ 07:11)
6. Give the built-in skill generator a very detailed description of the task, since the AI does not know your use case. (src: 2026-10-13-webdev-simplified-ai-skills @ 09:44)
7. Read the generated draft in full and edit it by hand until it is exactly right. (src: 2026-10-13-webdev-simplified-ai-skills @ 10:00)
8. Optionally limit what a skill may do with the allowed-tools field (marked experimental in the specification). (src: 2026-10-13-webdev-simplified-ai-skills @ 11:27)
9. Put runnable code in a scripts folder so the agent gets a known input and output instead of prose instructions. (src: 2026-10-13-webdev-simplified-ai-skills @ 13:01)
10. Keep the main file under about 500 lines and move detail into separate reference files linked from it, one level deep. (src: 2026-10-13-webdev-simplified-ai-skills @ 16:22)
11. Write the description around the user's intent and when to use the skill, not around what the tool is; say when not to use it too. (src: 2026-10-13-webdev-simplified-ai-skills @ 18:02)
12. Base the content on your own hands-on experience and real documents or examples. (src: 2026-10-13-webdev-simplified-ai-skills @ 20:27)
13. Include only what the agent does not already know. (src: 2026-10-13-webdev-simplified-ai-skills @ 21:41)
14. Add a section of what to do and what not to do. (src: 2026-10-13-webdev-simplified-ai-skills @ 22:07)
15. Provide templates for formatted output, and checklists or validation loops for multi-step tasks. (src: 2026-10-13-webdev-simplified-ai-skills @ 22:18)
16. Refine over time: save the agent's first output next to your corrected version, then have a second skill compare them and fold the lasting differences back in for you to review. (src: 2026-10-13-webdev-simplified-ai-skills @ 26:58)

## Disagreements
None found.
