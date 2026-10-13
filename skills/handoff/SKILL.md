---
name: handoff
description: Write a handoff so a fresh agent or session can continue the work. Use when the user says "handoff", "hand off", "write a handoff", "before I clear", when the context hook demands one at 65/70%, or when an out-of-scope task or a prototype's learnings must go to another session. Two modes - durable (session end, committed in <ops-repo>) and disposable (slice or return, temp dir, never committed).
argument-hint: "What will the next session be used for?"
---

# handoff

Adapted from Matt Pocock's `handoff` (github.com/mattpocock/skills, 2026-10-06 version) plus the user's records rules. Reviewed by opencode 2026-10-13.

## Rules for every mode
1. **Purpose first.** The argument is what the next session will do; tailor the doc to it. If none was given (hook-triggered or bare), use "continue the current work" and say so in the doc.
2. **Pointers, not copies.** Never repeat what lives in a spec, plan, PR, issue, commit, diff or vault note; give the path, URL or number. Only write what is not captured elsewhere.
3. **Redact.** No keys, tokens, passwords, personal data, Gmail content. Before saving, scan the draft: `grep -n -i -E "sk-|ghp_|github_pat|AIza|Bearer |api[_-]?key|password|token|@gmail\.com|AKIA|xox[bp]-|glpat-|PRIVATE KEY|eyJ[A-Za-z0-9_-]{20,}"` and fix every hit that is a secret. Mention that a secret exists, never its value.
4. **Suggested skills.** Add a `## Suggested skills` section for the next agent. Only name skills that exist in this session's skill list. A skill that is parked: write `skill-shelf: <name>`. Add one line: "if your harness has no skill loader, read ~/.agents/skills/<name>/SKILL.md".
5. **Verify first.** Add a `## Verify before acting` section: 2 to 4 facts or checks that can drift (branch, open PR, running service, file state). State what you checked yourself and when. Mark anything unchecked as unverified.
6. **Plain markdown.** No harness-specific syntax, so Codex, opencode, pi and Claude can all read it.

## Mode A: durable (session end, "before I clear", hook demand)
Use when the work continues later in time. Records live in git. Steps:
1. Write `<ops-repo>/docs/handoffs/HANDOFF-YYYY-MM-DD-HHMM-<topic>.md` (Asia/Seoul time). Sections: Goal, Done (verified, with pointers), In progress, Exact next steps, Gotchas, Open decisions for the user, Suggested skills, Verify before acting, Pointers.
2. Prior handoff on the same work: re-check it against what happened since (PRs merged, decisions, deferrals). Do not edit its history. Mark it SUPERSEDED in INDEX if the new file replaces it.
3. **Fold rule.** If the file you are updating already has 3 or more stacked UPDATE sections, prepend a dated `## Current state` block at the TOP that supersedes them (prepend only), and leave every dated section below it untouched (append-only; nothing is deleted or rewritten).
4. Add the INDEX row in `<ops-repo>/docs/handoffs/INDEX.md` (status OPEN, DONE, BLOCKED or SUPERSEDED; same columns as existing rows).
5. Ship it: in <ops-repo> run `git worktree list` and `gh pr list --state open`. If a docs-only handoff PR is open, add the file and INDEX row to THAT branch and push. Otherwise branch `docs/handoff-YYYY-MM-DD-<topic>` from current origin/master (clean worktree if the checkout is dirty) and `gh pr create`. Never one worktree and PR per handoff. No attribution lines. The user merges.
6. Reply with a 3-line state summary and the PR URL. Do not announce merges or /clear.

## Mode B: disposable (slice or return)
Use when the work moves sideways to another session now, not later. Never committed, no INDEX row.
- **Slice**: an out-of-scope task found mid-session. Doc = Task, Why it is out of scope, Acceptance (how the other session knows it is done), Suggested skills, Pointers. After writing it, tell the current session the question or scope is closed so it stays pure.
- **Return**: a prototype or side session reporting to its parent. Doc = only learnings not already in the prototype, diff or issue; non-obvious decisions; gotchas; pointers. Address it to the parent. Suggested skills are optional.
- **Location**: `<OS temp>/handoffs/handoff-<slice|return>-<topic>-<HHMM>.md` (`$TMPDIR`, else `/tmp`; `%TEMP%` on Windows). Create the folder if missing. Header lines: `from:`, `purpose:`, `created:`, `disposable: yes`.
- **Contract**: the LAST line of your reply is the absolute path alone, so the user can paste it to the next agent.
- Temp handoffs are redacted like any other; do not put them in a repo.

## Never
- Save a disposable handoff in a workspace, or a durable one in temp.
- Rewrite history inside an older handoff.
- Restate the whole conversation; if a section would just repeat a PR or file, point to it.

## Any agent
- Written for every agent (Claude Code, opencode, pi, omp, Codex, hermes). No skill tool: read this file and follow it. No hook: write the handoff when the user asks or when you judge context is heavy.
- Every step is plain shell plus `git` and `gh`; Claude-only items (the context hook, a skill loader) are triggers, not requirements.
- Agents without their own todo or skill list: take names for "Suggested skills" from `~/.agents/skills/` and `~/.claude/skills-parked/INDEX.md`.
