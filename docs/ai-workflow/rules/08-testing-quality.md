# Testing & quality rules

## Definition of Done
- [ ] `opskit/bin/check` passes (shellcheck + bats; `--quick` skips docker integration)
- [ ] From Phase 2: `opskit/bin/opskit selftest` passes (local Docker stack — WSL laptop or cloud container; no real clients)
- [ ] New logic has tests; bugs get a failing test first
- [ ] PROGRESS.md updated with manual verification steps

## What must have tests
- Secret generation never empty; config/schema validation errors
- Compose/.env/Caddy rendering (worker URL, replicas, limits, CE edition, pinned tag)
- Shared-host port/route allocation and capacity warning
- Backup → restore round trip incl. stored connection decrypting; retention pruning
- Failed-run detector query + de-duplication; alert payload per channel
- Upgrade promote and rollback paths
- Care report numbers vs fixture DB
- Custom piece actions (upstream test runner)

## Tools
shellcheck, bats-core, docker compose (WSL or cloud container) for integration tests, mock ops-hub (small HTTP listener), fixture Postgres data. Never test against real client hosts.
