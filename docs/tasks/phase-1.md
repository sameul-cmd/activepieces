# Phase 1 — Opskit foundation

SPEC refs: §3 (rules), §6 (client registry), §16 (commands), §17 Phase 1. Phase 0 inputs: `docs/EXPLORATION_REPORT.md` §6, `docs/ASSUMPTIONS.md` (verified facts), ADR-015, ADR-016.

**Accept (SPEC):** `opskit/bin/check` passes locally and in CI; `opskit doctor` reports tools; invalid `client.yaml` fixtures fail validation with field-level messages; `git diff 0.92.2 --stat` lists only our paths (+ ledgered upstream files).

## Open questions for the owner (agent's default in brackets)
1. **CI:** Actions are disabled in the fork. Checked 0.92.2's workflows: none trigger on a plain push to `opskit-main`; 22 trigger on pull requests/schedules (schedules stay off in forks by default). [Default: owner re-enables Actions when task 1.11 lands; we push directly to `opskit-main` and don't open PRs inside the fork, so only `opskit-ci.yml` runs.]
2. **Schema validation tool:** [Default: a small JSON-Schema-subset validator written in `jq` (no new dependency; `yq` only converts YAML→JSON). Alternatives: `ajv-cli` (Node) or `check-jsonschema` (Python).]
3. **Dev tools:** [Default: `shellcheck` and `bats` from Ubuntu apt, both on the laptop and in CI. No vendored copies.]

## Conventions decided for this phase
- `yq` flavours differ (Ubuntu apt = Python/jq-style `yq`; Go `yq` from mikefarah). `lib/yaml.sh` detects the flavour and only uses it to convert YAML → JSON; all logic is `jq`.
- Every script: `#!/usr/bin/env bash`, `set -euo pipefail`, `--help`, shellcheck-clean, one-line `[ok]/[warn]/[fail]` output (rules 05).
- Tests live in `opskit/tests/` (`*.bats`, fixtures in `opskit/tests/fixtures/`); tests never need Docker unless tagged `integration` (skipped by `--quick`).

## Tasks

### [ ] 1.1 — Skeleton, dispatcher, logging
- **Goal:** `opskit/{bin,lib,schema,templates,agent,flows,hub,tests}` tree; `bin/opskit` routes `opskit <command> [args]` to `lib/cmd/<command>.sh`; `--help`, `version` (prints opskit version + pinned upstream tag from `docs/UPSTREAM_CHANGES.md`), unknown command → exit 2 with help; `lib/log.sh` (`log_ok/log_warn/log_fail/die`, `NO_COLOR` respected).
- **Files:** `opskit/bin/opskit`, `opskit/lib/log.sh`, `opskit/lib/cmd/version.sh`, `opskit/VERSION`, `opskit/README.md`.
- **Tests:** help output, unknown command exit code, version output.

### [ ] 1.2 — `bin/check` + test tooling
- **Goal:** `opskit/bin/check` runs shellcheck on every opskit shell file and bats on `opskit/tests`; `--quick` skips `integration` tests; clear summary + non-zero exit on failure. Install notes in `docs/ENVIRONMENT.md`.
- **Files:** `opskit/bin/check`, `opskit/tests/test_helper.bash`.
- **Tests:** check fails on a deliberately broken fixture script (run against a temp dir).

### [ ] 1.3 — Confirmation guard for destructive actions
- **Goal:** `lib/confirm.sh`: `confirm_destructive <client_id> <action>` requires `--yes` **and** typing the client id (or `OPSKIT_CONFIRM=<client_id>` for tests/CI); refuses on mismatch or non-interactive without both.
- **Tests:** all accept/refuse paths.

### [ ] 1.4 — YAML loading
- **Goal:** `lib/yaml.sh`: `yaml_to_json <file>` for both yq flavours; clear error on invalid YAML; `cfg_get <json> <jq-path>` helper.
- **Tests:** valid/invalid YAML, both code paths (flavour forced via env in tests).

### [ ] 1.5 — Schemas for `client.yaml` and `hosts/<host>.yaml`
- **Goal:** `schema/client.schema.json` with all SPEC §6 fields + Phase 0 additions (`pieces` list, `image.repo` default `activepieces/activepieces`, `status`, `history`), `schema/host.schema.json` (name, ip, ssh_user, ssh_port, mode, ram_mb, ports range, provider). `templates/client.yaml.tmpl` example. Fixtures: 1 valid + ≥ 8 invalid (missing field, bad slug, bad domain, unknown mode, bad email, replicas < 1, unknown alert channel, extra unknown key).
- **Files:** `opskit/schema/*.json`, `opskit/templates/client.yaml.tmpl`, `opskit/tests/fixtures/{clients,hosts}/*.yaml`.

### [ ] 1.6 — Validator + `opskit validate`
- **Goal:** `lib/validate.sh` (jq JSON-Schema subset: `type, required, properties, additionalProperties:false, enum, pattern, minimum, maximum, minLength, items, default`) printing one line per error with the field path (e.g. `[fail] client.yaml: .host.mode: must be one of dedicated, shared`). `opskit validate client <id|path>` and `opskit validate host <name|path>`.
- **Tests:** valid fixture passes; every invalid fixture fails with the expected field path in the message.

### [ ] 1.7 — Template rendering helper
- **Goal:** `lib/render.sh`: `render_template <tmpl> <out> <vars-json>` via `envsubst` with an explicit variable list; fails on any unresolved `${...}`; writes atomically (`mktemp` + `mv`); optional mode (e.g. `600`). Used by Phase 2.
- **Tests:** renders, fails on missing var, file mode honoured.

### [ ] 1.8 — SSH helpers
- **Goal:** `lib/ssh.sh`: `ssh_run <host-json> <cmd...>`, `ssh_copy <host-json> <src> <dst>` with `BatchMode=yes`, `StrictHostKeyChecking=accept-new`, `ConnectTimeout`, port/user from host config; `OPSKIT_DRY_RUN=1` prints instead of running.
- **Tests:** a fake `ssh`/`scp` on `PATH` records the exact arguments.

### [ ] 1.9 — `opskit doctor`
- **Goal:** checks and reports: OS (WSL / Linux / cloud container), docker daemon reachable, compose v2, and tools `git openssl jq yq envsubst curl ssh shellcheck bats age rclone` (age/rclone = warn until Phase 3); prints versions; exit 1 only if a required tool is missing.
- **Tests:** PATH stubs for present/missing tools; exit codes.

### [ ] 1.10 — Fork hygiene check
- **Goal:** `opskit/tests/fork_hygiene.bats` (integration, needs git history): `git diff --name-only 0.92.2` contains only our paths + ledgered upstream files (`AGENTS.md`, `CLAUDE.md`); no `AP_EDITION=ee` and no `packages/ee` references in our files; `opskit/clients`, `opskit/hosts` git-ignored.
- **Tests:** the bats file itself.

### [ ] 1.11 — CI workflow
- **Goal:** `.github/workflows/opskit-ci.yml`: on push/PR touching `opskit/**`, `docs/**`, `.github/workflows/opskit-*`: install shellcheck + bats (apt), run `opskit/bin/check --quick` + fork hygiene (with `fetch-depth: 0` + tag fetch). Runs only when the owner enables Actions (Q1).
- **Tests:** workflow lint with `actionlint` if available (optional), else YAML parse check in bats.

### [ ] 1.12 — Docs and phase verification
- **Goal:** `docs/ENVIRONMENT.md` install commands for dev tools; `docs/UPSTREAM_SYNC.md` adds: re-apply ledger patch #1, re-test CE piece upload (ADR-016), re-check Phase 0 verified facts; `opskit/README.md` usage. Run `verify-phase` + `security-review`.
