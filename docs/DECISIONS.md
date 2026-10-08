# Architecture Decision Records

Format: Context → Decision → Alternatives → Consequences. Never delete; mark superseded.

### ADR-001: Fork Activepieces; clients run images built from the fork
- **Status:** accepted
- **Context:** Owner wants an enhanced repo on GitHub to install clients from; private piece upload is paid, and the custom-piece route assumes a fork.
- **Decision:** Fork, pin release tags, fetch-only upstream; build our CE image with custom pieces via GitHub Actions.
- **Alternatives:** Ops-kit repo with Activepieces cloned inside (can't ship custom pieces on CE); official images only.
- **Consequences:** Must sync releases and rebuild images; heavy builds happen in CI.

### ADR-002: Our code isolated; upstream edits only via ledger
- **Status:** accepted
- **Decision:** `opskit/`, `packages/pieces/custom/`, `.github/workflows/opskit-*.yml`, docs, IDE config. Upstream workflows disabled in the fork.
- **Consequences:** Clean syncs.

### ADR-003: Community Edition only
- **Status:** accepted
- **Context:** Docs' manual path suggests `AP_EDITION=ee`; ee code is commercially licensed.
- **Decision:** Render `AP_EDITION=ce` explicitly; never touch `packages/ee`.
- **Consequences:** No branding/projects/SSO/private-piece upload; one stack per client.

### ADR-004: One stack per client; dedicated or shared hosts
- **Status:** accepted
- **Decision:** Per-client compose project, volumes, `.env`, domain, backups; hosts may carry one or several stacks behind one Caddy.
- **Consequences:** Clean isolation; capacity checks needed on shared hosts.

### ADR-005: Bash ops tooling driven by validated `client.yaml`
- **Status:** accepted
- **Context:** Hosts are plain Ubuntu; minimal dependencies; testable with bats.
- **Decision:** `opskit` dispatcher + libs; JSON-schema validation; templates rendered with envsubst/yq.
- **Alternatives:** Ansible, Terraform, Node CLI.
- **Consequences:** Simple to run anywhere; keep scripts small and tested.

### ADR-006: Ops-hub = our own Activepieces + Uptime Kuma
- **Status:** accepted
- **Context:** CE alerting features may be limited; multi-channel routing needed; dogfooding shows clients the product.
- **Decision:** Hosts push heartbeats/alerts to ops-hub webhooks; ops-hub flows route to Telegram/email/Slack/WhatsApp and send reports.
- **Consequences:** Ops-hub must itself be monitored (UptimeRobot) and backed up.

### ADR-007: Failed-run detection by read-only SQL
- **Status:** accepted (verify schema in Phase 0)
- **Decision:** Cron query on run tables with a read-only role; de-duplicated alerts.
- **Consequences:** Must re-verify table names after each upstream sync.

### ADR-008: Encrypted secrets escrow with age + off-server copies with rclone
- **Status:** accepted
- **Decision:** `.env` encrypted to owner's age key; dumps + escrow copied off-server; tested restores monthly.

### ADR-009: Upgrades through staging with automatic rollback
- **Status:** accepted
- **Decision:** Backup → staging restore on new image → smoke tests → promote → rollback on failure.

### ADR-010: Two IDE packages share docs (superseded by ADR-011)
- **Status:** superseded
- **Decision:** Kilo: `AGENTS.fork.md` + `kilo.jsonc` + `.kilo/`. Factory: `.factory/AGENTS.md` + `.factory/skills/`. Same `docs/`, same nested AGENTS.md in our folders.

### ADR-011: Agent-neutral setup; the repo is the memory (supersedes ADR-010)
- **Status:** accepted (owner, 2026-10-08)
- **Context:** Work starts in Claude Code (limited credits) and may move to Kilo Code or any other agent mid-phase. Upstream already owns root `AGENTS.md`, `CLAUDE.md` and `.claude/`.
- **Decision:** One copy of rules (`docs/ai-workflow/rules/`) and workflows (`docs/ai-workflow/workflows/`). Thin wrappers per agent: `kilo.jsonc` + `.kilo/commands/` (Kilo), `.claude/rules/opskit.md` + `.claude/commands/ops-*.md` (Claude Code). Root `AGENTS.md`/`CLAUDE.md` get one pointer line to `AGENTS.fork.md` (ledger patch #1) so agents that only read the root files find us. Every session ends with the `handoff` workflow (PROGRESS → Handoff, commit, push).
- **Alternatives:** Kilo-only package (original); per-agent copies of rules (drift).
- **Consequences:** Re-apply the pointer line after each upstream sync; never keep state only in chat.

### ADR-012: Fork created on GitHub; work branch `opskit-main` from the pinned tag
- **Status:** accepted (owner, 2026-10-08)
- **Context:** The fork's `main` follows upstream `main` (ahead of any release). SPEC 3.3: our `main` = release tag + our commits.
- **Decision:** Our line of work is branch `opskit-main`, created from tag `0.92.2`. The owner may make it the fork's default branch; upstream's `main` in the fork is not used.
- **Consequences:** Syncs merge newer tags into `opskit-main` (`docs/UPSTREAM_SYNC.md`).

### ADR-013: Phase 0 may run in a cloud agent container
- **Status:** accepted (owner, 2026-10-08)
- **Context:** SPEC assumes a WSL2 laptop; the Claude Code cloud container has Docker (4 CPU / 15 GB RAM) and a headless browser.
- **Decision:** Phase 0 runs in the cloud container first. Every step is written so it can be repeated on the WSL laptop. The report records which environment produced each number.
- **Consequences:** RAM/CPU numbers from the cloud may differ from the 12 GB laptop; laptop-specific checks (Docker Desktop, WSL networking) are re-checked when work moves there. Cloud containers are ephemeral: nothing local survives a session.

### ADR-014: Starter flow #6 is a generic monthly report (not "Elmo")
- **Status:** accepted (owner, 2026-10-08)
- **Context:** The roadmap's starter list included "Elmo monthly report (schedule → Elmo API → email summary)", which doesn't belong to this project (likely mixed in from another plan).
- **Decision:** Flow #6 = generic monthly report: schedule → numbers from a Google Sheet or any HTTP API → AI summary → email to the client.
- **Consequences:** Works for any client; demonstrates the AI step. No Elmo integration anywhere in the kit.

### ADR-015: Owner answers for Phases 0–2 (2026-10-08)
- **Status:** accepted (owner)
- **Decision:** Ops-hub at `automate.autonyxai.shop`; VPS provider-neutral (free tier first); backups to Google Drive via rclone (configurable); 12 h response; AI = owner's OpenAI-compatible endpoint via Activepieces `CUSTOM` provider; Phase 0 flows on built-in pieces; client stacks `AP_TELEMETRY_ENABLED=false`.
- **Consequences:** `client.yaml`/`host.yaml` schemas keep provider and backup remote as free fields; Google Drive needs an rclone OAuth token per host (Phase 3 documents it).

### ADR-016: Custom pieces are uploaded via the CE API, not baked into an own image (amends ADR-001)
- **Status:** accepted (owner, 2026-10-08)
- **Context:** Phase 0 proved CE 0.92.2 accepts private piece archives (`POST /api/v1/pieces`, `ARCHIVE`, platform admin) and runs them; archives are stored in the DB and survive backups. The docs call this a paid feature, but the endpoint is CE (MIT) code.
- **Decision:** Build piece `.tgz` archives in CI; `opskit pieces push` uploads them per client. Clients run the official pinned image. The fork stays (pieces live in it; ADR-001 otherwise unchanged).
- **Alternatives:** own GHCR image with bundled pieces (original plan; kept as fallback).
- **Consequences:** No image builds/registry; must re-test the upload after each upstream sync; each client needs an operator admin account (no API keys on CE).
