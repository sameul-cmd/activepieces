# Phase 0 — Fork, set up & explore Activepieces (as it is)

## Open questions for the owner
- Cloud sandbox: owner set network to Full (2026-10-08); containers still need the relay in `docs/exploration/cloud-sandbox/` (sandbox-only).
- AI: owner's OpenAI-compatible endpoint — needs `OPSKIT_AI_BASE_URL`, `OPSKIT_AI_API_KEY`, `OPSKIT_AI_MODEL` in the agent environment.
- Third-party accounts: owner approved built-in pieces for Phase 0 (ADR-015).

## Reproduce the install (any Linux shell with Docker)
```bash
mkdir -p explore/stack/tools && cd explore/stack            # explore/ is git-ignored
cp ../../docker-compose.yml ../../.env.example . && cp ../../tools/deploy.sh tools/
bash tools/deploy.sh                                          # generates secrets (needs openssl)
grep -E '^(AP_ENCRYPTION_KEY|AP_JWT_SECRET|AP_POSTGRES_PASSWORD)=.+' .env | wc -l   # must print 3
printf '\nAP_EDITION=ce\n' >> .env && chmod 600 .env
patch docker-compose.yml < ../../docs/exploration/compose-changes.diff   # worker AP_FRONTEND_URL=http://app, replicas 1 (+ Docker Hub image)
docker compose -p activepieces up -d
# Cloud sandbox only: add  -f docker-compose.cloud.yml  (files in docs/exploration/cloud-sandbox/, copy them + CA to ./cloud/)
curl http://localhost:8080/api/v1/health                      # {"status":"Healthy"}
```

## Tasks

### [x] 0.1 — Fork, pin, agent setup
- Fork `sameul-cmd/activepieces`, branch `opskit-main` from tag `0.92.2`; ledger + ADR-011/012/013.

### [x] 0.2 — Official install (CE) with worker fix, 1 replica, health OK
- Done in cloud sandbox 2026-10-08 (see report §1). Worker connects via Socket.IO.

### [x] 0.3 — Admin account, builder basics, CE feature matrix (Platform Admin)
- Record available vs locked: projects, API keys, piece management, alerts, branding, audit logs, Git Sync, templates, import/export.

### [x] 0.4 — Triggers & logic: webhook (local curl; ngrok only on laptop), schedule, branch, loop, delay, code step, HTTP piece; run logs, retries, failure display
- Done via API (`docs/exploration/ap_api.py`, flow `explore/flows/p0-logic.json`); UI walkthrough not done (API-only in cloud).

### [ ] 0.5 — AI step with the owner's OpenAI-compatible endpoint (Custom provider; practice data)

### [~] 0.6 — Build the 6 starter flows as far as free/built-in pieces allow; export each flow JSON to `explore/flows/`
- 1,3,4,5 ✅ tested; 2,6 built, waiting for AI endpoint env vars. Generator `docs/exploration/starter_flows.py`.
- 1 lead capture · 2 AI email sorter · 3 review request · 4 invoice reminder · 5 social lead alert · 6 generic monthly report (ADR-014)

### [x] 0.7 — Backup → restore into a fresh local stack (pg_dump + .env), confirm a stored connection still decrypts

### [x] 0.8 — Measure RAM/CPU idle and under 20 test runs

### [x] 0.9 — Inspect run tables read-only for the failed-run detector (SPEC 10.3); Redis durability question (SPEC 9.7)

### [ ] 0.10 — Custom piece dev: hello-world piece in dev mode; how CE loads custom pieces (SPEC 14)

### [ ] 0.11 — Answer every *(verify)* item, finish `docs/EXPLORATION_REPORT.md`, owner review
