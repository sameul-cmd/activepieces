# Progress

## Current status
- **Current phase:** Phase 0 — Fork, set up & explore Activepieces
- **Current task:** none yet → next step is the `explore` workflow (see Handoff)
- **Last updated:** 2026-10-08

## Handoff
<!-- Overwritten by the `handoff` workflow at the end of every session. The next agent starts here. -->
- **Agent / environment:** Claude Code, cloud container (Ubuntu, Docker 29, 4 CPU, 15 GB RAM)
- **Repo / branch:** owner's GitHub fork of `activepieces/activepieces`, branch `opskit-main` (= upstream tag `0.92.2` + our commits)
- **Done this session:** Ops-kit starter package (made for Kilo Code) adapted to be agent-neutral and committed on top of `0.92.2`: rules/workflows moved to `docs/ai-workflow/`, wrappers for Kilo (`.kilo/commands/`) and Claude Code (`.claude/commands/ops-*`, `.claude/rules/opskit.md`), new `handoff` workflow, pointer line at the top of upstream `AGENTS.md`/`CLAUDE.md` (ledger patch #1), pinned tag recorded.
- **Exact next step:** run the `explore` workflow (Phase 0). Start with `docs/tasks/phase-0.md` (create it via `start-phase` if missing), then install Activepieces CE 0.92.2 with Docker Compose the official way.
- **Not carried over (temporary):** nothing running yet.
- **Open questions for the owner:** SPEC Appendix B (business name/ops-hub domain, VPS provider, backup target, response time). Not blocking Phase 0.
- **Owner to-dos:** disable GitHub Actions in the fork (Settings → Actions); optionally make `opskit-main` the default branch.

## Phases
| Phase | Name | Status | Verified |
|---|---|---|---|
| 0 | Fork, set up & explore Activepieces | In progress (fork + pin + agent setup done) | — |
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
- **2026-10-08 — Agent-neutral setup (Claude Code, cloud).** Forked upstream, branch `opskit-main` from tag `0.92.2` (`d125d34e59ac57ea4d0df57af4b917344027f06b`). Added the ops-kit package, adapted for any agent (ADR-011). Files: `AGENTS.fork.md`, `README-START-HERE.md`, `kilo.jsonc`, `.kilo/`, `.kilocodeignore`, `.claude/commands/ops-*.md`, `.claude/rules/opskit.md`, `docs/ai-workflow/**`, our `docs/*.md`, `docs/tasks/_TEMPLATE.md`, `opskit/` (AGENTS + .gitignore), `explore/.gitignore`, `packages/pieces/custom/AGENTS.md`; one-line pointer added to upstream `AGENTS.md` + `CLAUDE.md` (ledger #1). Verify: `git diff 0.92.2 --stat` shows only these paths.

## Known issues
<!-- Bugs or gaps found outside current task scope. -->
- Upstream already ships `packages/pieces/custom/` (empty `README.md`) and a `.claude/` folder; the original package assumed neither existed. We only add files there (no upstream edits).

## Phase verification reports
<!-- Output of /verify-phase goes here. -->
