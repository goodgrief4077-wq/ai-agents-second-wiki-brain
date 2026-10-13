# Outward actions

Outward means: create or delete a repo, push, open a PR, publish, send, share, or anything others can see or that is hard to undo.

1. **Card first.** One message to the user: the action, the exact target, the visibility and the files. Wait for a yes. An earlier yes does not cover a new target. If a word is ambiguous ("under", "in"), quote it and state the reading.
2. **Read the destination's rules** (its AGENTS.md, CLAUDE.md, lint config) before acting, and quote the one that matters in the card.
3. **Private first.** New repos start private. Scan for secrets and for personal data (paths, names, IPs, account names) before anything goes public. Public only on the user's word. Never push unsanitized files to a public repo, even on a branch.
4. **Never turn a live folder into a repo** (a tool config folder, a skills folder, a notes vault). Work on a copy or a clone.
5. **Reviewer gate.** For irreversible or outward steps, send the plan to a reviewer first and wait for the OK. With no reviewer, the user is the gate.
6. **Check permission first** (`gh auth status`), put it in the plan, and drop any extra scope after use.
7. **Record after, not before.** Write memory notes and say "done" only after live verification.
8. **Check names first.** Before creating a repo or branch, list existing ones (`gh repo list`, `git ls-remote`) to avoid a collision.
9. **Scripts via a file-write tool**, not heredocs with backslashes. One retry, then simplify.
10. **Long jobs in the background**, never a foreground command that can pass a minute; poll the result.
11. **State assumptions first.** If a reading of the request was assumed, say so at the start of the reply, not after a correction.
