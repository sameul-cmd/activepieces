# Assumptions

Decisions the agent made where `docs/SPEC.md` was silent or ambiguous. The owner reviews these regularly.

| # | Date | Phase/Task | Spec section | Assumption | Approved? |
|---|---|---|---|---|---|
| A1 | 2026-10-08 | 0 / setup | 17 Phase 0 | "Latest release" = upstream tag `0.92.2` (released 2026-10-07; `release-candidate` tag ignored). | yes (owner chose the fork setup) |
| A2 | 2026-10-08 | 0 / setup | 0.1, 3.1 | Our docs sit at the `docs/` root next to upstream's Mintlify site; they are not in `docs/docs.json` navigation, so the upstream site is unaffected. | |

## Verified facts (Phase 0, pinned 0.92.2) — answers to SPEC *(verify)* items
| SPEC | Item | Answer | Evidence |
|---|---|---|---|
| 3.4 | `AP_EDITION` value | `ce` (also the default) | `packages/core/shared/src/lib/core/flag/flag.ts`, `system.ts` |
| 3.4 | `AP_EXECUTION_MODE` on CE | `UNSANDBOXED` accepted on CE (ee/cloud reject it); other modes exist but untested | `system-validator.ts` |
| 7.2 | Required generated secrets | `AP_API_KEY`, `AP_ENCRYPTION_KEY` (hex 16), `AP_JWT_SECRET`, `AP_POSTGRES_PASSWORD` (per `tools/deploy.sh`) | `tools/deploy.sh`, `.env.example` |
| 7.4 | How to check the worker is registered | `GET /api/v1/worker-machines` → `status: ONLINE` | report §2 |
| 9.7 | Durable state only in Redis? | No — DB is source of truth; after Redis loss restart app+worker to refill jobs | report §5 |
| 10.3 | Run tables/columns/status values | `flow_run` (+ `flow_version."displayName"`), statuses listed in report §5 | report §5 |
| 11 | Flow import/export on CE | API `IMPORT_FLOW` works with admin JWT; templates gallery read-only | report §2 |
| 13 | Report numbers via SQL | `flow_run` per `flowId`/status/time — feasible | report §5 |
| 14 | Piece CLI commands | `createPiece` (interactive `npm run create-piece`), `TS_NODE_TRANSPILE_ONLY=true npm run build-piece <name>` | report §3, §5 |
| 14 | How CE loads custom pieces | Upload `.tgz` via `POST /api/v1/pieces` (ARCHIVE, platform admin); stored in DB | report §2 |
| 14 | Build too heavy for 12 GB laptop? | Dev install 2.8 GB / ~5 min, piece build 30 s on 4 vCPU — fine on laptop; the Docker image build was not tried | report §3 |
| 4, 10.5 | WhatsApp Cloud API setup/cost; Uptime Kuma API | **not verified** (Phase 4) | — |
