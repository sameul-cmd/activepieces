# Start here — Automation Ops Kit (works with any AI coding agent)

This repo is **your fork of Activepieces** (Community Edition, MIT) with the **Automation Ops Kit** added on top: specs, rules and workflows that let an AI coding agent build the kit phase by phase. Activepieces' own files (`AGENTS.md`, `CLAUDE.md`, `.claude/rules/*`, `README.md`, the Mintlify `docs/` site) stay theirs. Nothing updates from upstream automatically.

- **Goal and requirements:** `docs/SPEC.md` (source of truth): the 8 agreed improvements, built in Phases 0–9.
- **Where we are right now:** `docs/PROGRESS.md` → *Current status* and *Handoff*.
- **Rules for the agent:** `AGENTS.fork.md` + `docs/ai-workflow/rules/`.
- **Workflows (slash commands):** `docs/ai-workflow/workflows/` (explore, start-phase, next-task, verify-phase, security-review, fix-bug, resume, handoff).

## Continue with another agent (copy, paste, go)
The repo, not the chat, is the memory. Every agent session ends with the `handoff` workflow (state saved in `docs/PROGRESS.md`, committed and pushed), so any agent can pick it up.

1. Get the latest code: `git clone https://github.com/<you>/activepieces.git activepieces-ops` (or `git pull`), then `git switch <branch from PROGRESS Handoff>`.
2. Open the folder in your agent and paste:

> Read `AGENTS.fork.md` and follow it. Then run the `resume` workflow (`docs/ai-workflow/workflows/resume.md`) and continue from `docs/PROGRESS.md` → Handoff. Before you stop, or if I say "wrap up", run the `handoff` workflow.

How each agent picks up the rules:
| Agent | Loads rules via | Commands |
|---|---|---|
| Kilo Code | `kilo.jsonc` (+ root `AGENTS.md`) | `/resume`, `/explore`, `/start-phase`, `/next-task`, `/verify-phase`, `/security-review`, `/fix-bug`, `/handoff` |
| Claude Code | `CLAUDE.md` + `.claude/rules/opskit.md` | same names with `ops-` prefix: `/ops-resume`, `/ops-next-task`, … |
| Cursor, Codex, Cline, Roo, Windsurf, Copilot, Factory, others | root `AGENTS.md` (its first line points to `AGENTS.fork.md`) | say "run the next-task workflow"; the agent opens `docs/ai-workflow/workflows/next-task.md` |

## One-time GitHub settings for the fork (owner)
- **Settings → Actions → General → Disable actions** (or "Allow selected" and allow only `opskit-*` workflows later). Upstream has ~40 workflows that would otherwise run, and fail, on every push.
- Our work lives on the branch named in `docs/PROGRESS.md` → Handoff until you decide to make it `main` (SPEC: `main` = pinned release tag + our commits).

## Working on your laptop (Windows)
All commands run in **WSL2 Ubuntu** (not PowerShell). Open the repo in VS Code via Remote-WSL so the agent runs Bash. Setup steps: `docs/ENVIRONMENT.md`.
```bash
mkdir -p ~/work && cd ~/work
git clone https://github.com/<you>/activepieces.git activepieces-ops && cd activepieces-ops
git remote add upstream https://github.com/activepieces/activepieces.git
git remote set-url --push upstream DISABLED
git fetch upstream --tags
```

## Phase loop
`explore` (Phase 0) → `start-phase` → repeat `next-task` → `verify-phase` + `security-review` → next phase. New session or new agent: `resume`. Ending a session: `handoff`.

Community Edition only: never set `AP_EDITION=ee` or use anything in `packages/ee/`.
