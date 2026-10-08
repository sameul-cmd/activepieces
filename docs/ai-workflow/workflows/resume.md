---
description: Rebuild context in a fresh session (any agent) and continue
---

# Resume

1. Read `AGENTS.fork.md`, then `docs/PROGRESS.md` (especially **Handoff**), the current `docs/tasks/phase-N.md`, and the last 10 entries of `git log --oneline`.
2. Run `git status` and `git fetch origin` to check for uncommitted or unpulled work. Confirm you are on the branch named in PROGRESS **Handoff**.
3. Check the environment you are in (WSL laptop or cloud container) against `docs/ENVIRONMENT.md`; run `opskit/bin/opskit doctor` once it exists (Phase 1+).
4. Summarize in 5 bullets: current phase, last completed task, uncommitted changes, known issues, next task.
5. Wait for the owner to confirm before continuing.
