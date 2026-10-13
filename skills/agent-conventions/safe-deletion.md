# Safe deletion

Never delete or prune anything permanently. Move to the trash only, and let the user empty it.

## Two approvals
1. **List first.** Show the candidates in chat, grouped by sender or type with counts and examples:
   - TRASH: clearly junk.
   - UNCERTAIN: say why. Never drop an uncertain item silently.
   - KEEP: receipts, orders, private items.
2. The user reviews and may strike items.
3. **Show the exact final set** (counts and items) and get a second approval.
4. Move to the trash. Report what was moved, verified against live state.

## Read-only analysis needs no approval
Disk and size checks (`docker system df`, `docker images`, `du -sh <path>/*`) are safe to run.

## Risk levels for disk cleanup
| Level | Examples | Rule |
|---|---|---|
| High | Running containers, databases, code | Never touch without an explicit yes |
| Medium | Unused images, backups | Ask |
| Low | Build cache, dangling images | Propose, still ask |

For each proposal give the category, items, size, risk, reversibility and recovery path.

## Irreversible commands
`rm -rf` and `docker system prune -a --volumes` are never run by the agent. Use the trash instead. If no trash route exists, stop and report; the user does the final delete.
