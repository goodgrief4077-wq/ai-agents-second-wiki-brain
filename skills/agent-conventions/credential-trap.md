# A token "fixed" but still failing

A stale token can survive in six or more places. Fixing one or two leaves a "fixed but keeps breaking" state.

## Where a stale token survives
1. Shell-level saved variables (universal or exported variables in the shell's own config).
2. The service manager's user environment cache. It survives shell restarts and needs an explicit unset.
3. The git credential store file.
4. The CLI's own keyring. The CLI may prefer an environment variable over the keyring, so a stale variable hides a good login.
5. Per-tool config files (`<agent-auth-file>`, MCP server configs, backups).
6. Shell history (`<shell-history-file>`). Autosuggest can silently re-run an old export.

## The verification trap
`git push` reads the credential store, so it can succeed while the CLI, CI scripts and MCP tools fail with 401. Never call the fix done on a push alone. Check the CLI auth status, a direct API call with the current token, and each per-tool config.

## Fix checklist (all steps)
1. Unset the variable in the service manager's user environment.
2. Erase the saved variable in the shell and unset it in the current session.
3. Update the git credential store with the valid token.
4. Log the CLI in again with the new token.
5. Sweep per-tool configs for the old value with a recursive search that skips caches. Report only file names, never the value.
6. Scrub stale lines from `<shell-history-file>`.

The same pattern applies to any API key across shells and tools. Never write the secret into a file, a chat message or a commit; mention that it exists, not what it is.
