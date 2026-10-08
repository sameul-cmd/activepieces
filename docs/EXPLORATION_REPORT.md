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

## 2. Feature walkthrough
| Feature | Tried with (sample data) | Result (works / partly / broken) | Notes, screenshots/log paths |
|---|---|---|---|

## 3. Performance on this machine
| Task | Input size | Time | Notes |
|---|---|---|---|
| Cold start → `/api/v1/health` 200 | fresh DB (migrations) | ~8 s after containers up (cloud) | |
| Idle RAM, whole stack | 0 flows | ≈ 870 MB | app 539 MB, worker 273 MB, postgres 51 MB, redis 5 MB; CPU ≈ 0.4% total |

## 4. Output quality
What looked client-ready, what didn't, with examples.

## 5. Limits & risks found
Licenses, paid dependencies, data/privacy, stability, update pace.

- **Pieces catalogue depends on `cloud.activepieces.com`** (`PIECES_SYNC_MODE` default `OFFICIAL_AUTO`, values `OFFICIAL_AUTO|NONE`; `packages/server/api/src/app/pieces/piece-sync-service.ts`). A client host that cannot reach it has no pieces. Phase 2 must check outbound access to `cloud.activepieces.com` and `registry.npmjs.org` in `host bootstrap`/`deploy`.
- **IPv6 must exist in the kernel**: the app listens on `::` (hard-coded). VPS images with `ipv6.disable=1` would crash-loop. Phase 2 `host bootstrap` should check this.
- `.env.example` ships `AP_TELEMETRY_ENABLED=true` and `AP_TEMPLATES_SOURCE_URL=https://cloud.activepieces.com/...` (outbound calls to Activepieces from client stacks).
- `AP_EDITION` valid values `ce|ee|cloud` (`packages/core/shared/src/lib/core/flag/flag.ts`); default is `ce` (`system.ts`). `ee`/`cloud` in production reject `AP_EXECUTION_MODE=UNSANDBOXED`; CE accepts it. Modes: `UNSANDBOXED`, `SANDBOX_CODE_ONLY`, `SANDBOX_PROCESS`, `SANDBOX_CODE_AND_PROCESS` *(which are usable on CE: to test in 0.4)*.
- Database has 70+ tables incl. `flow_run`, `trigger_run`, `alert`, `api_key`, `platform_plan`, `project` (detector + feature-matrix work in 0.3/0.9).

## 6. Matches the SPEC? (agent's view)
Does the app behave as the SPEC assumes? List any mismatches that affect later phases; if none, say "no blockers — continuing".

## 7. Questions for the owner (only if blocked or unclear)
