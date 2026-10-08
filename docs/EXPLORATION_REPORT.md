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
| Worker registered check | `GET /api/v1/worker-machines` (admin JWT) | works | Returns workers with `status: ONLINE` → use in `deploy`/smoke tests (SPEC 7.4 answered). Also `GET /api/v1/worker-machines/queue-metrics` |
| Web UI served | `GET /` | works (200 HTML) | Interactive UI walkthrough not done in the cloud session (API-driven exploration); do a short click-through on the laptop |
| **Custom piece on CE** | scaffold (`createPiece` from `packages/cli`) → `npm run build-piece` → `POST /api/v1/pieces` multipart `packageType=ARCHIVE, scope=PLATFORM` (admin JWT) | **works** | Piece `@activepieces/piece-p0-hello@0.0.1` listed as `CUSTOM/ARCHIVE`, used in a flow → `Hello Autonyx from a custom piece`. Archive stored in DB `file` table (`PACKAGE_ARCHIVE`) → included in `pg_dump`. Endpoint is CE code (`packages/server/api/src/app/pieces/community-piece-module.ts`, MIT), registered only for `ApEdition.COMMUNITY` |
| Run log / failure display | API `GET /flow-runs/<id>` | works | Per-step status, input/output, `failedStep {name,message,displayName}` |

## 2b. Starter flows (SPEC 11) — built with built-in pieces (ADR-015)
Generator: `docs/exploration/starter_flows.py` → JSON in `docs/exploration/starter-flows/`. Stand-ins: Activepieces Tables (`opskit_leads`, `opskit_invoices`, referenced by **externalId**, so the same JSON works on any stack that has those tables) instead of Sheets/CRM; HTTP POST to a notify URL instead of email/Slack/WhatsApp.
| # | Flow | Pieces | Test | Result |
|---|---|---|---|---|
| 1 | Lead capture | webhook → code (validate) → tables create → HTTP notify → webhook reply | valid lead; lead without email | ✅ saved to table, notified, replied; invalid → FAILED with clear message |
| 2 | AI email sorter | webhook → AI `classifyText` → router (urgent / else) → notify/label → reply | — | ⏳ built; needs AI provider (owner's OpenAI-compatible endpoint) |
| 3 | Review request | webhook → code → delay (7 days; `wait_minutes` override for tests) → notify | wait 1 min | ✅ paused, resumed on time, notified |
| 4 | Invoice reminder | schedule (weekdays 09:00) → tables find → code (unpaid & overdue) → loop → notify | 3 seeded invoices (1-min schedule test copy) | ✅ only the overdue unpaid invoice got a reminder |
| 5 | Social lead alert | webhook (lead-ads shape) → code → tables create → notify | sample lead | ✅ |
| 6 | Generic monthly report (ADR-014) | schedule (monthly) → tables find → code KPIs → AI `summarizeText` → notify | — | ⏳ built; needs AI provider |
Notes: `tables-find-records` returns rows as `{id, cells: {<fieldId>: {fieldName, value}}}`; `tables-create-records` accepts `records` JSON keyed by column name (advanced prop). Expressions inside `{{ }}` were kept to plain references (logic lives in code steps). Error convention: invalid input throws in the first code step → run FAILED → picked up by the SQL detector (no CE alerting). Real Gmail/Sheets/Slack/WhatsApp connections are left for the laptop.

## 3. Performance on this machine
| Task | Input size | Time | Notes |
|---|---|---|---|
| `pg_dump -Fc` of the DB | 5 flows, 766 pieces | 14.7 s, **90 MB** | `piece_metadata` = 240 MB of 240.5 MB DB size; flows/runs tiny |
| Restore into a fresh stack (new volumes, port 8081) → healthy | 90 MB dump | ~51 s total (dump + new stack + restore + start) | Same `.env` (`AP_ENCRYPTION_KEY`) |
| Dev toolchain `bun install --frozen-lockfile` | full monorepo | 288 s, 2.8 GB `node_modules` | 1 git-hosted dep 403 (`@modelcontextprotocol/sdk@github:dust-tt/...`) — not needed for pieces |
| `build-piece` for a hello-world piece | 1 action | 30 s → 78 KB `.tgz` | needs `TS_NODE_TRANSPILE_ONLY=true` (see §5) |
| Cold start → `/api/v1/health` 200 | fresh DB (migrations) | ~8 s after containers up (cloud) | |
| Idle RAM, whole stack | 0 flows | ≈ 870 MB | app 539 MB, worker 273 MB, postgres 51 MB, redis 5 MB; CPU ≈ 0.4% total |
| 20 concurrent webhook runs (code + branch + loop + 2 s delay + HTTP) | 20 runs | all 20 SUCCEEDED within ~10 s | Peaks: worker 969 MiB / 361% CPU, app 900 MiB / 48%, postgres 105 MiB, redis 6 MiB → **≈ 2 GB total**. 4 GB per client is enough; worker is CPU-bound in bursts (1 replica used all 4 cores) |

## 4. Output quality
What looked client-ready, what didn't, with examples.

- Flow engine is solid: every logic feature, delays (incl. pause/resume across restarts), schedules, tables and connections behaved correctly; failures carry clear step names and messages; secrets are redacted in run logs.
- 420 ready templates are a strong sales asset (e.g. "Score and Qualify Inbound Leads", "Store Survey Results in a Table") — our 6 starters can borrow from them.
- Not client-ready out of the box: no failure alerts on CE, no API keys, "Powered by Activepieces" on forms, `localhost` worker/public-URL trap, Redis-loss silently stops schedules until restart. These are exactly what opskit adds.

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
- **Upstream CLI type error (0.92.2):** `npm run build-piece` fails under ts-node with `packages/core/utils/src/lib/deno.ts(58,64): TS2339 Property 'error' does not exist on type 'DenoResultMessage'`. Workaround without touching upstream: `TS_NODE_TRANSPILE_ONLY=true npm run build-piece <name>`. A new piece folder needs `bun install` (updates `bun.lock` → restore it or commit it deliberately with the piece).
- **Docs vs code on private pieces:** docs (`build-pieces/misc/private-fork.mdx`) say private piece installation needs the paid edition, but CE 0.92.2 registers `POST /v1/pieces` (ARCHIVE or REGISTRY) for platform admins and it works. Risk: upstream could restrict it in a later release → re-test after every upstream sync; keep the own-image route (SPEC 14) as fallback.
- **No API keys on CE** → automation (flow import, piece upload, smoke tests, reports) must sign in as a platform admin (`POST /api/v1/authentication/sign-in`) to get a JWT. Implication: each client stack needs an operator admin account whose password lives in the host `.env`/escrow.
- Database has 70+ tables incl. `flow_run`, `trigger_run`, `alert`, `api_key`, `platform_plan`, `project` (detector + feature-matrix work in 0.3/0.9).

## 6. Matches the SPEC? (agent's view)
Does the app behave as the SPEC assumes? List any mismatches that affect later phases; if none, say "no blockers — continuing".

Mostly yes — no blockers. Confirmed: CE value `ce`; worker `AP_FRONTEND_URL=http://app` fix; 4 containers; data only in Postgres; `AP_ENCRYPTION_KEY` needed to decrypt connections; failed runs detectable by SQL; CE lacks alerts → ops-hub design holds; one stack per client.
Mismatches / additions that change later phases:
1. **Phase 8 (custom pieces):** CE can upload private piece archives via API — an own Docker image may be unnecessary. **Owner decision needed** (see §7).
2. **Phase 2:** worker must reach the app's public URL → render `extra_hosts: <domain>:host-gateway` for the worker; check outbound access to `cloud.activepieces.com` + `registry.npmjs.org`; check kernel IPv6; don't use `container_name`; render `AP_TELEMETRY_ENABLED=false` (ADR-015); create an operator admin account (no API keys on CE).
3. **Phases 3/6:** restored/staging stacks must disable flows before start (they fire schedules immediately); restore order = postgres → `pg_restore --no-owner` → app+worker; backup ≈ 90 MB per client mostly piece catalogue.
4. **Phase 4:** add a check "Redis restarted after app → restart app+worker" (schedules/delays otherwise stop); `worker-machines` endpoint for worker health.
5. **Phase 5:** flows import via `IMPORT_FLOW` API with admin JWT; Tables referenced by `externalId` make templates portable; `opskit flows import` can be fully automatic (not only printed instructions).

## 7. Questions for the owner (only if blocked or unclear)
1. **Phase 8:** switch from "build our own Docker image with custom pieces" to "upload custom pieces to each client via the CE API (built in CI, uploaded by `opskit`)", keeping the image route only as a fallback? (Agent recommends: yes — simpler, no GHCR builds, faster.)
2. **AI endpoint:** provide `OPSKIT_AI_BASE_URL`, `OPSKIT_AI_API_KEY`, `OPSKIT_AI_MODEL` as environment variables to finish task 0.5 and starter flows 2 and 6 (can also be finished later on the laptop).
