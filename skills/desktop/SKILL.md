---
name: desktop
description: Turn whatever we just did (research, guide, doc, PDF, build) into a Markdown file on the Desktop. Use when the user types /desktop.
---

Capture whatever we just did as one self-contained Markdown file at `~/Desktop/<Topic>-YYYY-MM-DD.md` (topic/source: the text after the command, or infer from the conversation; hyphenated Title-Case name; today's date).

- Works for any output: research, a guide, a doc, a PDF, a build, a setup, a decision. If the work was a PDF/doc/other file, convert its content to Markdown (pandoc or direct extraction) rather than summarizing it away.
- Structure: what was done/found first, then how to use it, sources linked, decisions or asks for the user last.
- No emojis, no filler; readable on its own without this conversation.
- If a same-day file with that name exists, append a dated section instead of overwriting.
- No extra research. Reply with the file path only.
