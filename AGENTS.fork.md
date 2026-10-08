# AGENTS.fork.md — Automation Ops Kit (fork of activepieces/activepieces)

> **Any AI coding agent (Claude Code, Kilo Code, Cursor, Codex, Cline, Roo, Windsurf, Copilot, Factory…) starts here.** This project is built across several agents and sessions; the repo — not the chat — is the memory. Read this file, then `docs/PROGRESS.md` → **Handoff**, then continue.

This repo is the owner's fork of Activepieces (open-source Zapier alternative, MIT Community Edition) plus **opskit**: tooling to deploy, back up, monitor, upgrade, document and report on one Activepieces stack per client, a flow template library, and custom pieces built into the owner's own Docker image.

**Two instruction sets apply.** Upstream's root `AGENTS.md`/`CLAUDE.md`, `.claude/rules/*` (except `opskit.md`), `.agents/` and `brain/` govern upstream code. This file, `docs/SPEC.md` and `docs/ai-workflow/rules/` govern opskit. On conflict: upstream conventions for how to edit upstream files; SPEC for what opskit does.

## Session start (every agent, every time)
1. Read `docs/PROGRESS.md` — **Current status** and **Handoff** tell you the branch, environment, last step and exact next step.
2. Read all rules in `docs/ai-workflow/rules/` (short; always apply).
3. Read the current `docs/tasks/phase-N.md` and only the SPEC sections it references.
4. `git status`, `git log --oneline -10`; make sure you are on the branch named in Handoff.
5. State: phase, task, files to touch (flag any upstream file). Then continue — ask the owner only when blocked or unclear.

## Workflows (slash commands)
Single source: `docs/ai-workflow/workflows/<name>.md`. Wrappers: Kilo `/<name>` (`.kilo/commands/`), Claude Code `/ops-<name>` (`.claude/commands/`). Agents without commands: open the file and follow it.
| Workflow | When |
|---|---|
| `explore` | Phase 0: install & explore Activepieces as it is, fill `docs/EXPLORATION_REPORT.md` |
| `start-phase` | Break the next phase into `docs/tasks/phase-N.md` |
| `next-task` | Implement the next unchecked task |
| `verify-phase` / `security-review` | End of every phase |
| `fix-bug` | Methodical bug fix |
| `resume` | New session / new agent: rebuild context |
| `handoff` | Before the session ends, credits run low, or switching agents: save state, commit, **push** |

## Document map
| File | Use it for | Authority |
|---|---|---|
| `docs/SPEC.md` | Requirements, phases (Section 17) | **Source of truth** |
| `docs/PROGRESS.md` | Status, **Handoff**, task log, known issues | Update every task |
| `docs/ai-workflow/rules/*.md` | Always-on rules (workflow, architecture, security, fork, scripts, reliability, pieces/flows, testing, git) | Must follow |
| `docs/EXPLORATION_REPORT.md` | Phase 0 findings (CE feature matrix, verify answers, RAM) | Informs later phases; blockers go to the owner |
| `docs/DECISIONS.md` | ADRs | Binding unless superseded |
| `docs/TECH_ARCHITECTURE.md` | Stack layout, repo structure, command pattern, sizing | Must follow |
| `docs/USER_FLOWS.md` | Operator flows and edge cases | Derived from SPEC |
| `docs/ENVIRONMENT.md` | Tools, accounts, variables, where work runs | Must follow |
| `docs/UPSTREAM_CHANGES.md` / `docs/UPSTREAM_SYNC.md` | Pinned tag, patch ledger, sync procedure | Must follow |
| `docs/RESEARCH.md` | Facts behind the SPEC | Background |
| `docs/tasks/phase-N.md`, `docs/ASSUMPTIONS.md` | Current tasks, assumptions | Update every task |

**Conflict order:** SPEC > DECISIONS > TECH_ARCHITECTURE > other docs.

## Golden rules
- **Phase 0 = install & explore Activepieces as it is** (`explore`): no opskit code, no upstream changes. Then continue; ask the owner only when blocked or unclear.
- ONE task at a time; never jump ahead. SPEC silent → simplest option consistent with SPEC 3, log in ASSUMPTIONS.
- Never invent Activepieces env vars, tables, APIs or piece CLI commands: check the pinned source/docs/running instance first; *(verify)* items must be verified and recorded.
- **Community Edition only**: never `AP_EDITION=ee`, never touch `packages/ee/`.
- **Client safety**: no secrets in git; destructive actions need `--yes`, typed client id, and owner approval.
- Never mark done unless `opskit/bin/check` passes (and `opskit/bin/opskit selftest` from Phase 2).
- Never remove or weaken a test. Don't edit SPEC, this file, `kilo.jsonc`, `.kilo/`, `.claude/commands/`, `.claude/rules/opskit.md` or `docs/ai-workflow/` without owner approval.
- Stop and ask before: new dependencies, upstream file edits, anything touching a real client host, spending money.
- **The chat is not memory.** Commit + push after every task; run `handoff` before stopping.

## Stack
Upstream: TypeScript monorepo (bun, turbo), Docker app/worker, Postgres, Redis. Opskit: Bash (shellcheck, bats), JSON schema, envsubst/yq/jq, Caddy, ufw, age, rclone, Uptime Kuma; GitHub Actions + GHCR. Work runs in a Linux shell: the owner's Windows laptop (WSL2 Ubuntu, Docker Desktop, 12 GB RAM) or a cloud agent container (Ubuntu + Docker) — see `docs/ENVIRONMENT.md`.

## Repo layout (ours)
`opskit/bin` · `opskit/lib` · `opskit/schema` · `opskit/templates` · `opskit/agent` (host scripts) · `opskit/flows` · `opskit/hub` · `opskit/tests` · `opskit/clients` + `opskit/hosts` (git-ignored) · `packages/pieces/custom/` · `.github/workflows/opskit-*.yml` · `explore/` (Phase 0 scratch, git-ignored) · `docs/` (our files listed above; the rest of `docs/` is upstream's Mintlify site) · agent config: `AGENTS.fork.md`, `kilo.jsonc`, `.kilo/`, `.kilocodeignore`, `.claude/commands/ops-*.md`, `.claude/rules/opskit.md`

## Commands
`opskit/bin/check` · `opskit/bin/check --quick` · `opskit/bin/opskit doctor` · `opskit/bin/opskit selftest` · `docker compose -p <id> ps` (opskit commands exist from Phase 1)

## End of every task
Update PROGRESS; ADR for architectural choices; ledger for upstream edits; conventional commit; **push**.
