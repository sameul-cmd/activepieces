# Workflow rules

## Task loop
1. Plan: list files to create/modify and the approach (max ~10 bullets). Wait for approval if the task touches upstream (non-opskit) files, dependencies, secret generation, backup/restore/upgrade logic, anything destructive, or any real client host.
2. Implement in small steps. After each meaningful step, run `opskit/bin/check --quick`.
3. Verify: `opskit/bin/check`, plus the manual check described in the task file.
4. Record: update `docs/PROGRESS.md`; add an ADR to `docs/DECISIONS.md` if an architectural choice was made.

## Scope control
- Only work on the current task in `docs/tasks/phase-N.md`.
- If you notice a bug outside scope, log it in PROGRESS.md "Known issues". Don't fix it silently.
- Features marked V2/Future in the spec: do not implement. Only keep the data model/interfaces ready.

## Anti-hallucination
- Before using a library function, confirm it exists in the installed version (read the installed package's types/source or the official docs for that version).
- Before calling an internal function, search the codebase to confirm its name and signature. Don't assume.
- Don't claim something works unless you ran it. Say "not verified" otherwise.
- If a command fails, read the actual error output before changing code. Don't guess-and-retry repeatedly; after 3 failed attempts, stop and report.

## Context hygiene
- When the conversation gets long, or the session/credits may end soon, run the `handoff` workflow (`docs/ai-workflow/workflows/handoff.md`): update PROGRESS.md "Handoff" with exact next steps, commit and push.
- Another AI agent may continue this work at any time. Never leave knowledge only in the chat: decisions → DECISIONS/ASSUMPTIONS, status → PROGRESS, findings → EXPLORATION_REPORT.
- Keep files under ~300 lines; split by responsibility.
