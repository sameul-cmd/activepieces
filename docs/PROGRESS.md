# Progress

## Current status
- **Current phase:** Phase 0 — Fork, set up & explore Activepieces
- **Current task:** none yet → next step is the `explore` workflow (see Handoff)
- **Last updated:** 2026-10-08

## Handoff
<!-- Overwritten by the `handoff` workflow at the end of every session. The next agent starts here. -->
- **Agent / environment:** Claude Code, cloud sandbox (Ubuntu, Docker 29, 4 CPU, 15 GB RAM, no IPv6, egress policy-filtered)
- **Repo / branch:** `sameul-cmd/activepieces`, branch `opskit-main` (= tag `0.92.2` + our commits)
- **Done:** Phase 0 tasks 0.1–0.2 (see `docs/tasks/phase-0.md`): CE 0.92.2 running via the official manual compose path, worker fix + 1 replica, health OK, idle RAM measured. Report §1, §3, §5 started.
- **Blocker:** `cloud.activepieces.com` is blocked by the cloud sandbox network policy → no pieces → builder can't be explored. Owner asked to allow it (environment settings → Network access → Allowed domains). On the WSL laptop this is not an issue.
- **Exact next step:** task 0.3 (admin account + CE feature matrix), then 0.4+ once pieces sync. Re-create the stack with the steps at the top of `docs/tasks/phase-0.md` (cloud: also `-f docker-compose.cloud.yml`).
- **Not carried over (temporary):** the local Docker stack in `explore/stack/` (git-ignored; secrets only there). A new session must re-create it.
- **Owner confirmed (2026-10-08):** the 8 improvements in SPEC 2.1 as written; flow #6 replaced by a generic monthly report (ADR-014).
- **Open questions for the owner:** see `docs/tasks/phase-0.md` top + SPEC Appendix B (needed from Phase 2).
- **Owner to-dos:** optionally make `opskit-main` the fork's default branch.

## Phases
| Phase | Name | Status | Verified |
|---|---|---|---|
| 0 | Fork, set up & explore Activepieces | In progress (0.1–0.2 done; blocked on pieces sync in cloud) | — |
| 1 | Opskit foundation | Not started | — |
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
- **2026-10-08 — 0.2 Official CE install (cloud).** Files: `docs/tasks/phase-0.md`, `docs/EXPLORATION_REPORT.md`, `docs/exploration/**`. Verify: follow the install block in `docs/tasks/phase-0.md`; `curl localhost:8080/api/v1/health` → Healthy; worker log shows "Connected to API server via Socket.IO".
- **2026-10-08 — Agent-neutral setup (Claude Code, cloud).** Forked upstream, branch `opskit-main` from tag `0.92.2` (`d125d34e59ac57ea4d0df57af4b917344027f06b`). Added the ops-kit package, adapted for any agent (ADR-011). Files: `AGENTS.fork.md`, `README-START-HERE.md`, `kilo.jsonc`, `.kilo/`, `.kilocodeignore`, `.claude/commands/ops-*.md`, `.claude/rules/opskit.md`, `docs/ai-workflow/**`, our `docs/*.md`, `docs/tasks/_TEMPLATE.md`, `opskit/` (AGENTS + .gitignore), `explore/.gitignore`, `packages/pieces/custom/AGENTS.md`; one-line pointer added to upstream `AGENTS.md` + `CLAUDE.md` (ledger #1). Verify: `git diff 0.92.2 --stat` shows only these paths.

## Known issues
<!-- Bugs or gaps found outside current task scope. -->
- The roadmap `05-activepieces-roadmap.md` is not in the repo; its starter list contained an unrelated "Elmo" flow, now replaced (ADR-014). If the roadmap turns up, check it for other mixed-in items.
- Upstream already ships `packages/pieces/custom/` (empty `README.md`) and a `.claude/` folder; the original package assumed neither existed. We only add files there (no upstream edits).

## Phase verification reports
<!-- Output of /verify-phase goes here. -->
