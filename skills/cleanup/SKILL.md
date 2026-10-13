---
name: cleanup
description: The user's step-by-step open-items walkthrough. Use when he types /cleanup or says "what's still open", "go through the open items", "let's clean up". Covers handoffs, Gmail (trash list, digests, self-notes), and the to-do ledger. One item at a time, each with a recommendation and the choices Leave it / Do now / Do later / Pass.
---

# /cleanup: one open item at a time

Address the user by the name they prefer. Short replies, no emojis. Do the steps yourself with tools; hand back only what physically needs him.

## Sources (read these, nothing else, unless an item needs more)
1. **Handoffs:** `<ops-repo>/docs/handoffs/INDEX.md` (rows marked OPEN or BLOCKED) plus the newest 5 days of handoff files, their "Next steps" and "Open decisions" sections.
2. **Gmail:** any open Gmail trash list (review only), `<notes-vault>/<self-notes-file>`, and the digest folder `<notes-vault>/<digest-folder>/`. Mail content never goes to a cloud model; digests (sender and subject) only. Gmail is read-only until the gmail.modify decision.
3. **To-do ledger:** `<notes-vault>/<cleanup-ledger>`. It is the single list of items and the user's dated answers. Add new items to it whenever one turns up.

## Loop
1. **Check live state first** (rule: verify before redoing). A handoff line may be stale; confirm against the real repo, task, branch or service, and drop items that are already done (say so, and fix the stale handoff or INDEX row with a dated note).
2. Present ONE item: what it is (2 to 4 lines), the live state, your recommendation with the reason, then the choices:
   **Choices: leave it, do now, do later, or pass.**
   He may also answer in his own words (trash, merge, close, change X). Treat those as valid choices.
3. Act on the answer:
   - **Do now:** do it fully, verify live, report what was verified. Outward or hard-to-reverse actions (push, merge, trash, remote changes) need his explicit OK on the exact set first.
   - **Do later:** ask when only if he gave none; write a dated line in the ledger and in the relevant handoff.
   - **Leave it:** record "left as is" with the date. Do not raise it again unless the state changes.
   - **Pass:** record "passed" with the date. Do not raise it again this round.
4. Record every answer in the ledger with the date (append, never overwrite).
5. Next item. Order: anything with a deadline first, then BLOCKED on the user, then the rest.

## Rules that apply
- Say "trash", never "delete". Only move to Trash. Trashing needs two approvals; show the list in chat first (TRASH / UNCERTAIN / KEEP). The user does the final delete.
- Ask before commits; PR first, never straight to main; stage specific files; no Co-Authored-By lines.
- No Claude subagents; do the work directly. pnpm only.
- Use only the mail account the user designated safe; never print secrets or keys.
- Never treat an inferred preference as his; ask.

## End of a round
Give a 3-line state summary (done / later with dates / left or passed). If he is ending the session, bring the newest handoff and its INDEX row up to date first.
