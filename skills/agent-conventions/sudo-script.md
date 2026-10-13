# Root-only steps: write a script, the user runs it

The agent usually has no terminal for a password prompt, and long inline `sudo bash -c '...'` blocks pasted into a shell break on line continuations and chained operators.

## Pattern
1. Write the full command sequence to a script file in the user's home, named for the job (`<job-name>.sh`). Start with `set -euo pipefail` so it stops at the first error.
2. End the reply with one fenced block telling the user the single command to run, for example `sudo bash <script-path>`. If the harness can run a user-typed shell command and return its output, say so; otherwise ask the user to paste the output back.
3. After the user has run it, verify the resulting state with read-only commands that need no root (service status, package query, log search). Do not call the job done on the script's exit alone.

## Use it for
Package installs, service unit edits, file ownership changes and any other root-only operation.
