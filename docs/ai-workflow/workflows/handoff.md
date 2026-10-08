---
description: Save everything the next session (possibly a different AI agent) needs, then commit and push
---

# Handoff

Run this before the session ends, when credits/context are running low, before switching agents, or when the owner asks.

1. Finish or cleanly pause the current step. Never leave a broken state committed; if the work is half-done, commit it on the branch with a `wip:` prefix and say so.
2. Update `docs/PROGRESS.md`:
   - **Current status** (phase, task, date).
   - **Handoff** section: agent + environment used, branch, last commit, what was just done, the *exact* next step (command or file), open questions for the owner, anything running/temporary (e.g. local Docker stacks, ngrok URLs) that the next session will NOT have.
   - Task log entry for completed work.
3. Move any knowledge that only lives in the chat into the right doc: decisions → `docs/DECISIONS.md`, guesses → `docs/ASSUMPTIONS.md`, Phase 0 facts → `docs/EXPLORATION_REPORT.md`, bugs → PROGRESS "Known issues".
4. Make sure no secrets, `.env`, dumps, or `opskit/clients/` / `opskit/hosts/` content are staged (`git status`, `git diff --cached --stat`).
5. Commit (`docs: handoff …` or the task's conventional commit) and **push to origin**.
6. Tell the owner in 3–5 lines: what's done, what's next, and the one sentence to paste into the next agent (see `README-START-HERE.md` "Continue with another agent").
