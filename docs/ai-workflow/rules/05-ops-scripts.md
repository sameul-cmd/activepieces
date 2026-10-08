# Ops script rules

- Every script: `#!/usr/bin/env bash`, `set -euo pipefail`, `IFS=$'\n\t'` where lists are parsed, shellcheck clean, `--help`.
- Quote all variables; no `eval`; no parsing `ls`; use `mktemp` + `trap` cleanup.
- Remote actions via `opskit/lib/ssh.sh` helpers only (BatchMode, StrictHostKeyChecking=accept-new, timeouts).
- Docker commands always with `-p <client_id>`; never `docker system prune` or volume removal outside offboard/restore flows.
- Print a one-line summary per step (`[ok]`, `[warn]`, `[fail]`); exit non-zero on failure.
- Templates render with `envsubst`/`yq` from validated config; fail on unresolved `${...}`.
- Keep functions small; shared logic in `opskit/lib/`.
