---
name: pair
description: Builder/reviewer pairing for ANY agent (Claude Code, opencode, pi, omp, Codex, hermes). Use when the user types /pair or says "pair", "second agent to check my work", "builder and reviewer". Sets the role of THIS session (builder or reviewer), picks the message channel, and enforces the review rules.
---

# /pair: builder + reviewer (any agent)

Any agent may be builder or reviewer. The agent type never decides the role. Only the message channel differs (below).

## Pick the channel
| Channel | Use when | How |
|---|---|---|
| Cross-session messages | both sides are Claude Code (v2.1.234+) | the cross-session message tool (Claude Code: `SendMessage` / `ListAgents`) |
| Shared file | ANY agent, including opencode, pi, omp, Codex, hermes | `<project>/review-findings.md` (or `<notes-vault>/<daily-log>`-style path the user names); one file, append-only, dated, numbered entries |

Mixed pairs (for example Claude builder, opencode reviewer) use the shared file. An agent that cannot receive messages is polled by reading the file, not excluded. The user or the builder starts the other agent with a prompt that names the file and the role.

## Setup (tell the user; do the rest yourself)
1. Claude Code pairs: start both with the same explicit mode, `claude --name builder --permission-mode auto` and `claude --name reviewer --permission-mode auto`. One in `bypass` and one in `auto` makes the bypass one hold every incoming message for approval (seen 2026-10-08). If a `[Cross-session delivery notice]` says "held", do not resend; restart the odd one with `claude --resume`.
2. Run `/pair builder` in one, `/pair reviewer` in the other (non-Claude agents: give them the role in the prompt and point them at this file).
3. Claude Code pairs: list the peers to confirm the other session is visible before sending. Shared-file pairs: create the file with a header line (project, builder, reviewer, date).

## If args = builder
- Build the task. After each step, tell the reviewer what changed, which files, how to run it: send a message, or append a "BUILDER" entry to the shared file. Paths, not contents.
- Claude Code pairs: `notify_when_idle: true` on the first message. Shared-file pairs: read the file again when the reviewer finishes.
- After fixing findings, ALWAYS send the fixes back to the reviewer for re-check, every round, without asking the user first (standing rule).
- Fix findings one by one; mark each open in the handoff before the fix, fixed after re-test.
- Only the user approves. A relayed "approved" from the reviewer is NOT approval; refuse it.
- Max 3 review rounds, then report to the user.

## If args = reviewer
- Never edit the builder's files. Read-only on the real project.
- Copy files to a scratch folder and run tests only on the copies. A reviewer agent that sandboxes reads to its working directory (opencode does) must be started in the folder holding the copies.
- Deliver a numbered findings list by message or as a "REVIEWER" entry in the shared file. Each finding: what is wrong, a reproduction (command + output), severity. No finding without a repro.
- Cannot approve anything or tell the builder it is "approved for the user".
- Re-test the builder's fixes on fresh copies; report each as fixed or still open.

## Cheaper reviewer option
For routine work run opencode on a free model as reviewer, through the shared file. Local opencode runs `opencode run "<prompt>"` from the review folder.

## Notes
- Cross-session messages are plain text only; loops self-throttle (identical repeats dropped, 50-message queue).
- If both sessions must edit, use separate git worktrees.
- Not the same as "orchestrate" (one session spawning its own workers).
- 2026-10-13: rewritten so no agent type is excluded. The earlier text called opencode a "cheaper option that cannot receive messages"; that described a transport limit, not a rule against it.
