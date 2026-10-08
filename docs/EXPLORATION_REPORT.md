# Exploration report — Automation Ops Kit (Activepieces fork)

> Filled during Phase 0 (clone, set up & explore). Facts only — what actually happened on this machine. Blockers or mismatches with the SPEC go to the owner before continuing.

## 1. Setup
| Item | Value |
|---|---|
| Repo + commit/version explored | `activepieces/activepieces` tag `0.92.2` (`d125d34e`), image `activepieces/activepieces:0.92.2` digest `sha256:87295caa…e5ee` (identical on Docker Hub and GHCR) |
| How it was installed/cloned | Official **manual** Docker Compose path (`tools/deploy.sh` + compose) in `explore/stack/`; `AP_EDITION=ce`; worker `AP_FRONTEND_URL=http://app`; worker `replicas: 1`. The recommended one-liner (`get.activepieces.com`) was blocked by the cloud sandbox network policy. Steps: `docs/tasks/phase-0.md` |
| Machine (CPU/RAM/GPU/OS) | Claude Code cloud sandbox: 4 vCPU, 15.7 GB RAM, no GPU, Linux 6.18, Docker 29.8.2, **no IPv6 in kernel** |
| Free path used (keys, free tiers, local models) | No keys yet |
| Setup time + problems hit (and fixes) | Image pull ~2 min (2.15 GB app image). Health OK 8 s after start once fixed. Problems: (1) GHCR blob storage blocked → pulled same digest from Docker Hub; Docker Hub 429 on `redis` → pulled from `mirror.gcr.io`. (2) App crash `listen EAFNOSUPPORT :::80` — `packages/server/api/src/main.ts` hard-codes `host: '::'`; on a kernel without IPv6 the app cannot start. Sandbox fix: `NODE_OPTIONS=--require ipv4-listen.cjs` shim (`docs/exploration/cloud-sandbox/`). (3) Containers' TLS is intercepted by the sandbox → `NODE_EXTRA_CA_CERTS`. (4) `cloud.activepieces.com` blocked → **0 pieces** in `piece_metadata`, builder unusable until allowed. (1)–(3) are sandbox-only; WSL/VPS should not need them *(to confirm on laptop)* |

## 2a. CE feature matrix (platform plan on 0.92.2, `GET /api/v1/platforms/<id>` → `plan`, and `/api/v1/flags`)
| Feature | CE | Notes |
|---|---|---|
| Unlimited flows/runs, builder, webhooks, schedules, branches, loops, code, HTTP | ✅ | |
| Tables (built-in database) | ✅ `tablesEnabled` | 10,000 records / 100 fields per table |
| AI providers (incl. **Custom OpenAI-compatible**) | ✅ `aiProvidersEnabled` | `AIProviderName.CUSTOM` exists |
| Analytics | ✅ `analyticsEnabled` | |
| Templates gallery (use) | ✅ | 420 official templates |
| Run retention | 30 days (`EXECUTION_DATA_RETENTION_DAYS`) | |
| Concurrency | 5 jobs default (`DEFAULT_CONCURRENT_JOBS_LIMIT`) | |
| API keys | ❌ `apiKeysEnabled=false` | Automation must use a user JWT (sign-in) |
| Built-in alerts UI | ❌ `SHOW_ALERTS=false` | → ops-hub + SQL detector is required (ADR-006/007 confirmed) |
| Audit logs, SSO, SCIM, custom roles, project roles | ❌ | |
| Branding/appearance, custom domains, "powered by" removal | ❌ | `SHOW_POWERED_BY_IN_FORM=true` |
| Manage pieces / private pieces | ❌ `managePiecesEnabled=false`, `PRIVATE_PIECES_ENABLED=false` | → own image (Phase 8) is the route |
| Manage templates | ❌ | |
| Environments / Git Sync, secret managers, global connections, event streaming, embedding, agents, chat | ❌ | |
| Team projects | ❌ (`billedTeamProjectsLimit=1`) | One stack per client (ADR-004 confirmed) |

## 2. Feature walkthrough
| Feature | Tried with (sample data) | Result (works / partly / broken) | Notes, screenshots/log paths |
|---|---|---|---|
| Admin sign-up (first user = platform admin) | `POST /api/v1/authentication/sign-up` | works | Returns JWT + `platformId` + `projectId`; no default user |
| Pieces catalogue | auto-sync from `cloud.activepieces.com` | works (after network fix) | 766 pieces; core pieces e.g. webhook 0.1.42, schedule 0.1.22, http 0.12.2, delay 0.3.35, tables 0.5.2, smtp 0.5.0, ai 0.11.0, gmail 0.17.4, google-sheets 0.17.1, slack 0.21.1, telegram-bot 0.8.1 |
| Templates gallery | `GET /api/v1/templates` | works (read-only) | 420 official templates served from cloud; *managing* own templates is paid (`manageTemplatesEnabled=false`) |
| Flow import via API | `POST /flows` + `IMPORT_FLOW` op, then `LOCK_AND_PUBLISH`, `CHANGE_STATUS ENABLED` | works | Helper `docs/exploration/ap_api.py`; uses the user JWT (CE has no API keys). Flow JSON = template `flows[0]` shape (`schemaVersion` "16") |
| Webhook trigger (async + `/sync`) | `explore/flows/p0-logic.json` | works | `/api/v1/webhooks/<flowId>` (async 200), `/sync` returns the `return_response` body |
| Code step | sum/throw | works | Throwing marks the run FAILED with message in `failedStep` |
| Router (branch) | total > 10 → Big / Otherwise | works | `EXECUTE_FIRST_MATCH`, numeric operator |
| Loop on items | 2–3 items | works | Iterations visible in run steps |
| Delay | 2 s | works | |
| HTTP piece | GET httpbin.org | works | In the sandbox needed `AP_SANDBOX_PROPAGATED_ENV_VARS` to pass proxy env to the engine (sandbox-only) |
| Schedule trigger | every 1 min (`p0-schedule`) | works | Ticks recorded as runs |
| Long delay (pause/resume) | 3 min delay (`p0-delay`) | works | Run is `PAUSED` in DB (`waitpoint` table), resumes on time |
| Stored connection | SECRET_TEXT for sendgrid/telegram-bot via `POST /api/v1/app-connections` | works | Referenced in steps as `{{connections['<externalId>']}}`; run logs show `**REDACTED**` |
| Run log / failure display | API `GET /flow-runs/<id>` | works | Per-step status, input/output, `failedStep {name,message,displayName}` |

## 3. Performance on this machine
| Task | Input size | Time | Notes |
|---|---|---|---|
| `pg_dump -Fc` of the DB | 5 flows, 766 pieces | 14.7 s, **90 MB** | `piece_metadata` = 240 MB of 240.5 MB DB size; flows/runs tiny |
| Restore into a fresh stack (new volumes, port 8081) → healthy | 90 MB dump | ~51 s total (dump + new stack + restore + start) | Same `.env` (`AP_ENCRYPTION_KEY`) |
| Cold start → `/api/v1/health` 200 | fresh DB (migrations) | ~8 s after containers up (cloud) | |
| Idle RAM, whole stack | 0 flows | ≈ 870 MB | app 539 MB, worker 273 MB, postgres 51 MB, redis 5 MB; CPU ≈ 0.4% total |
| 20 concurrent webhook runs (code + branch + loop + 2 s delay + HTTP) | 20 runs | all 20 SUCCEEDED within ~10 s | Peaks: worker 969 MiB / 361% CPU, app 900 MiB / 48%, postgres 105 MiB, redis 6 MiB → **≈ 2 GB total**. 4 GB per client is enough; worker is CPU-bound in bursts (1 replica used all 4 cores) |

## 4. Output quality
What looked client-ready, what didn't, with examples.

## 5. Limits & risks found
Licenses, paid dependencies, data/privacy, stability, update pace.

- **Pieces catalogue depends on `cloud.activepieces.com`** (`PIECES_SYNC_MODE` default `OFFICIAL_AUTO`, values `OFFICIAL_AUTO|NONE`; `packages/server/api/src/app/pieces/piece-sync-service.ts`). A client host that cannot reach it has no pieces. Phase 2 must check outbound access to `cloud.activepieces.com` and `registry.npmjs.org` in `host bootstrap`/`deploy`.
- **IPv6 must exist in the kernel**: the app listens on `::` (hard-coded). VPS images with `ipv6.disable=1` would crash-loop. Phase 2 `host bootstrap` should check this.
- `.env.example` ships `AP_TELEMETRY_ENABLED=true` and `AP_TEMPLATES_SOURCE_URL=https://cloud.activepieces.com/...` (outbound calls to Activepieces from client stacks).
- `AP_EDITION` valid values `ce|ee|cloud` (`packages/core/shared/src/lib/core/flag/flag.ts`); default is `ce` (`system.ts`). `ee`/`cloud` in production reject `AP_EXECUTION_MODE=UNSANDBOXED`; CE accepts it. Modes: `UNSANDBOXED`, `SANDBOX_CODE_ONLY`, `SANDBOX_PROCESS`, `SANDBOX_CODE_AND_PROCESS` *(which are usable on CE: to test in 0.4)*.
- **Worker downloads piece bundles from the app's PUBLIC URL** (`AP_FRONTEND_URL` of the app, sent to the worker as `PUBLIC_URL`; `packages/server/sandbox/src/lib/cache/pieces/piece-installer.ts`, `worker.ts`). With `AP_FRONTEND_URL=http://localhost:8080` the worker can't reach it → publish fails with `TRIGGER_UPDATE_STATUS … fetch failed`. Local fix: `AP_FRONTEND_URL=http://host.docker.internal:8080` (+ hosts entry). **Phase 2:** render `extra_hosts: ["<domain>:host-gateway"]` on the worker so it reaches Caddy on the same host without hairpin NAT.
- Failed-run detection (SPEC 10.3) verified: table `flow_run`, columns `id, status, "flowId", "flowVersionId", "projectId", environment ('PRODUCTION'), "failedStep" jsonb {name, message, displayName}, "startTime", "finishTime", created`; flow name from `flow_version."displayName"`. Statuses (`FlowRunStatus`): `FAILED, QUOTA_EXCEEDED, INTERNAL_ERROR, PAUSED, QUEUED, RUNNING, SUCCEEDED, MEMORY_LIMIT_EXCEEDED, TIMEOUT, CANCELED, LOG_SIZE_EXCEEDED`. Detector should treat `FAILED, INTERNAL_ERROR, TIMEOUT, MEMORY_LIMIT_EXCEEDED, QUOTA_EXCEEDED, LOG_SIZE_EXCEEDED` as failures. Index `idx_run_project_id_environment_status_created_archived_at` supports the query. Query:
  ```sql
  SELECT r.id, r.status, v."displayName" AS flow_name, r."flowId", r."failedStep"->>'name' AS step,
         left(r."failedStep"->>'message', 300) AS error, r."finishTime"
  FROM flow_run r JOIN flow_version v ON v.id = r."flowVersionId"
  WHERE r.status IN ('FAILED','INTERNAL_ERROR','TIMEOUT','MEMORY_LIMIT_EXCEEDED','QUOTA_EXCEEDED','LOG_SIZE_EXCEEDED')
    AND r."finishTime" > $since ORDER BY r."finishTime";
  ```
  Run link: `<AP_FRONTEND_URL>/runs/<id>` *(UI path to confirm)*.
- **Backup → restore verified (SPEC 9, Phase 3 acceptance shape):** `pg_dump -Fc` via the postgres container + `.env` copy → fresh stack (`postgres`+`redis` up, `pg_restore --no-owner`, then app+worker) → same admin login works, all 5 flows present and ENABLED, the stored connection decrypts (fingerprint check flow `docs/exploration/p0-conn.flow.json` returns identical hash). Without the same `AP_ENCRYPTION_KEY` this would fail.
- **Restored copies run scheduled flows immediately** (both stacks fired `P0 schedule`). Staging/restore-test stacks (Phases 3, 6) must disable flows after restore (e.g. `UPDATE flow SET status='DISABLED'` before app start *(to verify that triggers are then not registered)*) and/or block outbound mail, or clients get duplicate actions.
- **Backup size is dominated by `piece_metadata`** (re-downloadable from cloud). Phase 3 can test `pg_dump --exclude-table-data=piece_metadata` + re-sync on start, but custom/private piece metadata (Phase 8) also lives there → keep full dumps unless proven safe.
- **Redis is not a source of truth (SPEC 9.7 answered):** after wiping Redis completely, schedules stopped and a due delayed run stayed `PAUSED`; after `restart app worker` the app's queue migrations (`packages/server/api/src/app/workers/migrations/refill-*.ts`, gated by Redis keys like `refill_paused_runs_v7`) re-created polling/schedule jobs and re-queued the paused run, which then SUCCEEDED. → Don't back up Redis; **after any Redis data loss, restart app+worker**; Phase 4 health check should detect "redis newer than app" and restart. Redis 7 image persists RDB to the `redis_data` volume on normal restarts.
- Upstream `docker-compose.yml` hard-codes `container_name` (`activepieces-app`, `postgres`, `redis`) → two stacks on one host collide. Our rendered compose (Phase 2) must not set `container_name` (use `-p <client_id>`).
- Database has 70+ tables incl. `flow_run`, `trigger_run`, `alert`, `api_key`, `platform_plan`, `project` (detector + feature-matrix work in 0.3/0.9).

## 6. Matches the SPEC? (agent's view)
Does the app behave as the SPEC assumes? List any mismatches that affect later phases; if none, say "no blockers — continuing".

## 7. Questions for the owner (only if blocked or unclear)
