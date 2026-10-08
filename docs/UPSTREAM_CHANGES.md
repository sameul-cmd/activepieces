# Upstream pin & patch ledger

| Field | Value |
|---|---|
| Upstream | https://github.com/activepieces/activepieces |
| Pinned release tag | `0.92.2` |
| Tag SHA | `d125d34e59ac57ea4d0df57af4b917344027f06b` (commit date 2026-10-07) |
| Pinned on | 2026-10-08 |
| Our branch | `opskit-main` |

## Patch ledger (changes to upstream files — approval required)
| # | Date | Upstream file(s) | Why | Change summary | Re-apply steps | Test | Status |
|---|---|---|---|---|---|---|---|
| 1 | 2026-10-08 | `AGENTS.md`, `CLAUDE.md` | Agents that only read root files must find the opskit rules (ADR-011) | One blockquote line added at the very top pointing to `AGENTS.fork.md` | Re-insert the same line as line 1 of both files after a sync | `head -1 AGENTS.md CLAUDE.md` shows the pointer | applied (owner-approved setup) |
