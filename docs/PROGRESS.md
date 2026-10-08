# Progress

## Current status
- **Current phase:** Phase 1 — Opskit foundation
- **Current task:** task file `docs/tasks/phase-1.md` created; next: 1.1
- **Last updated:** 2026-10-08

## Handoff
<!-- Overwritten by the `handoff` workflow at the end of every session. The next agent starts here. -->
- **Agent / environment:** Claude Code, cloud sandbox (Ubuntu, Docker 29, 4 CPU, 15 GB RAM, no IPv6; network "Full" but containers need the relay — `docs/exploration/cloud-sandbox/`)
- **Repo / branch:** `sameul-cmd/activepieces`, branch `opskit-main` (= tag `0.92.2` + our commits)
- **Done:** Phase 0 (report accepted; AI deferred). Phase 8 switched to piece uploads (ADR-016). Phase 1 task file written.
- **Exact next step:** Phase 1 task 1.1 in `docs/tasks/phase-1.md` (owner asked to review the 3 open questions at its top; defaults apply if no answer).
- **Not carried over (temporary):** local stack in `explore/stack/` (admin creds in `explore/stack/admin.txt`, JWT in `.token`), tables `opskit_leads`/`opskit_invoices`, custom piece `packages/pieces/custom/p0-hello/` (git-excluded scratch; source copy in `docs/exploration/p0-hello-piece/`), `node_modules` (2.8 GB). A new session must re-create the stack (`docs/tasks/phase-0.md`).
- **Owner confirmed (2026-10-08):** 8 improvements as written; flow #6 = generic monthly report (ADR-014); answers in ADR-015.
- **Owner to-dos:** optionally make `opskit-main` the fork's default branch.

## Phases
| Phase | Name | Status | Verified |
|---|---|---|---|
| 0 | Fork, set up & explore Activepieces | Done (AI step + flows 2/6 deferred by owner) | 2026-10-08 (owner accepted report) |
| 1 | Opskit foundation | In progress | — |
| 2 | Client deployment kit | Not started | — |
| 3 | Backups & restore | Not started | — |
| 4 | Monitoring & alerts | Not started | — |
| 5 | Flow template library | Not started | — |
| 6 | Safe upgrades | Not started | — |
| 7 | Handover docs & care report | Not started | — |
| 8 | Custom pieces & own image | Not started | — |
| 9 | Field readiness | Not started | — |

## Task log
<!-- Newest first. For each task: date, task, files changed, how to verify manually, notes. -->
- **2026-10-08 — 0.3–0.10 exploration (cloud).** CE feature matrix, logic/trigger tests, load test, run-table detector query, Redis-loss recovery, backup→restore with connection decrypt, 6 starter flows (4 tested), custom piece upload on CE. Files: `docs/EXPLORATION_REPORT.md`, `docs/ASSUMPTIONS.md`, `docs/exploration/**`. Verify: re-create stack, run `docs/exploration/ap_api.py` steps in the report.
- **2026-10-08 — 0.2 Official CE install (cloud).** Files: `docs/tasks/phase-0.md`, `docs/EXPLORATION_REPORT.md`, `docs/exploration/**`. Verify: follow the install block in `docs/tasks/phase-0.md`; `curl localhost:8080/api/v1/health` → Healthy; worker log shows "Connected to API server via Socket.IO".
- **2026-10-08 — Agent-neutral setup (Claude Code, cloud).** Forked upstream, branch `opskit-main` from tag `0.92.2` (`d125d34e59ac57ea4d0df57af4b917344027f06b`). Added the ops-kit package, adapted for any agent (ADR-011). Files: `AGENTS.fork.md`, `README-START-HERE.md`, `kilo.jsonc`, `.kilo/`, `.kilocodeignore`, `.claude/commands/ops-*.md`, `.claude/rules/opskit.md`, `docs/ai-workflow/**`, our `docs/*.md`, `docs/tasks/_TEMPLATE.md`, `opskit/` (AGENTS + .gitignore), `explore/.gitignore`, `packages/pieces/custom/AGENTS.md`; one-line pointer added to upstream `AGENTS.md` + `CLAUDE.md` (ledger #1). Verify: `git diff 0.92.2 --stat` shows only these paths.

## Known issues
<!-- Bugs or gaps found outside current task scope. -->
- **Deferred by owner (2026-10-08):** Phase 0 task 0.5 (AI step) and starter flows 2 + 6 tests — need `OPSKIT_AI_BASE_URL/API_KEY/MODEL`; pick up in Phase 5 at the latest.
- The roadmap `05-activepieces-roadmap.md` is not in the repo; its starter list contained an unrelated "Elmo" flow, now replaced (ADR-014). If the roadmap turns up, check it for other mixed-in items.
- Upstream already ships `packages/pieces/custom/` (empty `README.md`) and a `.claude/` folder; the original package assumed neither existed. We only add files there (no upstream edits).

## Phase verification reports
<!-- Output of /verify-phase goes here. -->
