---
name: work-review
description: Cross-repo, cross-project review of actual work done — "review what we did", "review today", "what did we do this week", "work review", "session review". Reads the Daily Activity Log plus git state across every local repo, groups results under the user's active-project list, flags uncommitted/unshipped work, and offers deep-dive review (compound-engineering:ce-code-review, compound-engineering:ce-doc-review, gstack /retro) only on request. Distinct from single-repo PR/commit review tools, which assume one repo and miss the multi-repo, non-code work that makes up most of a day here.
---

# Work Review

The user's actual unit of work is not one git repo — it spans <ops-repo>,
several repos, Obsidian vaults, reference managers, PDFs, `.claude` skills/memory, and
non-git scratch dirs, often several in one day. `/retro`, `ce-code-review`, and
`ce-doc-review` all assume a single repo with committed changes or a PR. This skill
sits above them: answer "what did we actually do" first, across everything —
committed or not — then hand off to those tools for depth only where code or docs
actually changed.

Read-only skill. Never stash, reset, add, or commit anything it finds.

## Dependencies (check once per session)

- **Daily Activity Log** — `<notes-vault>/Daily-Log\YYYY-MM-DD.md`, fed by the
  global git `post-commit` hook (`~/.git-hooks/post-commit`) and the Claude Code
  `PostToolUse` hook (`~/.claude/scripts/activity-log-hook.ps1`, wired in
  `~/.claude/settings.json`). This is the only source that catches uncommitted work
  and non-git files. If either hook file is missing, say so explicitly and fall back
  to git log only for that window — do not silently under-report.
- **`compound-engineering` plugin** (`ce-code-review`, `ce-doc-review`) — for the
  optional deep-dive in Step 7.
- **gstack `/retro`** — for the optional single-repo deep-dive in Step 7.
- **Orca CLI** (`orca-cli` skill) — for Step 4. Resolve the executable per that
  skill's rules (`ORCA_CLI_COMMAND` env var → `orca-dev` in a dev checkout → `orca`
  elsewhere on Windows). If Orca isn't running, `orca open --json` then
  `orca status --json` to confirm before querying.

If a dependency is missing, name exactly which one and continue with whatever still
works — don't block the whole review on one missing piece.

## Step 1 — Parse the window

Default: today. Accept `today`, `Nd` (last N days), `this week` (since local Monday
midnight). If ambiguous, ask rather than guess.

## Step 2 — Read the Daily Activity Log

Read every `<notes-vault>/Daily-Log\YYYY-MM-DD.md` file that falls in the
window. This is ground truth for *what file, what tool, what time* — across every
repo and non-repo directory touched, whether or not it was ever committed.

A missing log file for a date in the window is a gap, not proof nothing happened —
check that date directly against git log in Step 3 before reporting it as idle.

## Step 3 — Cross-check every local repo

Discover repos dynamically — don't hardcode a list, it rots as repos get added or
archived:

```bash
for d in "$HOME"/*/ ; do
  [ -d "$d/.git" ] && echo "$d"
done
```

Also check any repo path that shows up in the Daily Log but lives outside `$HOME`.
For each repo found:

```bash
git -C "$repo" log --oneline --since="<window-start>"
git -C "$repo" status --short
```

`git status --short` output means uncommitted work — report it. Do not touch it.

## Step 4 — Cross-check Orca CLI (worktrees, terminals, history/logs)

Orca tracks worktree/terminal activity Daily Log + git can miss (agent sessions in
worktrees, commits made in repos not under `$HOME`). Load the `orca-cli` skill for
the exact command surface, then:

```text
ORCA status --json
ORCA repo list --json
ORCA worktree ps --json
```

For every registered repo, cross-check its worktree list against what Step 3
already found, in case a repo lives outside `$HOME` or isn't plain git:

```text
ORCA worktree list --repo id:<repoId> --json
```

For any worktree with `lastActivityAt` inside the window or `liveTerminalCount > 0`,
pull terminal history to see what actually ran there:

```text
ORCA terminal list --worktree id:<repoId>::<worktreePath> --json
ORCA terminal read --terminal <handle> --json
```

If a commit or file from Step 2/3 can't be traced to a known repo path, check it
against `repo list` / `worktree list` here before reporting it as unresolved — do
not give up after one `git -C` failure. If still unresolved after checking Orca,
say so explicitly rather than guessing a path.

## Step 5 — Cross-check memory

Check which files under
`<agent-memory-dir>`
were created or edited in the window (compare mtimes, or diff `MEMORY.md` if under
version control). Surface these explicitly — a new or updated memory is a durable
decision, not just file churn, and is easy to miss inside a long Daily Log.

## Step 6 — Build the report

Group findings under the user's active-project list (keep one in your own notes; mark active versus on hold), plus an "Infra/tooling"
bucket for `.claude/`, `CLAUDE.md`, and scripts work. For each group, state: what
shipped (committed), what's in progress (uncommitted), what got decided (memory).

Call out explicitly, don't bury:

- Uncommitted changes older than the window start — easy to forget, worth a nudge.
- Any `CLAUDE.md` edit not yet mirrored to the Obsidian vault clone
  (`<notes-vault>/<mirror-folder>/`), per the standing sync rule.
- Any health/medical-adjacent file touched outside the `health-context` skill.

## Step 7 — Offer depth, never auto-run it

Each of these is heavier and possibly multi-agent — ask before invoking, never
chain into them automatically:

- A repo has code changes (committed or not) worth a real review → offer
  `compound-engineering:ce-code-review` scoped to that repo's diff.
- A plan/spec/doc file had multiple edit passes in the window → offer
  `compound-engineering:ce-doc-review` on it.
- One repo dominates the window and deserves full commit/quality metrics → offer
  gstack `/retro` scoped to that repo.

## Step 8 — Report status

End with one of: **DONE** (full window covered), **DONE_WITH_CONCERNS** (a repo or
directory was unreachable, or a dependency was missing), **NEEDS_CONTEXT** (window
ambiguous, asked and still unresolved). Never silently skip a repo that had Daily
Log activity — if its git state can't be checked, say so.

## Other agents
- Usable by any agent that can read files and run shell and `git`. Claude Code supplies the `PostToolUse` activity hook; other agents (pi, omp, Codex, opencode, hermes) log to the Daily Log by hand, so also read their entries and `git log` per repo, and say when an agent's day has no log lines.
- The optional deep-dive tools (`ce-code-review`, `ce-doc-review`, `/retro`) are Claude plugins. Any other agent skips Step 7 or does a plain `git diff` read and reports it as a lighter review.
