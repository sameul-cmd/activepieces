# Phase 0 — Fork, set up & explore Activepieces (as it is)

## Open questions for the owner
- Cloud sandbox network policy blocks `cloud.activepieces.com` (pieces catalogue) → owner to allow it, or Phase 0 piece-dependent tasks move to the WSL laptop.
- Gemini free-tier API key for the AI step (practice data only) — owner provides, or the AI step is tested later.
- Third-party accounts (Google Sheets/Gmail, Slack…) for starter flows: proposed to use Activepieces' built-in pieces (Tables, Webhook, HTTP, Schedule, Email) in Phase 0 and connect real accounts later.

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

### [ ] 0.3 — Admin account, builder basics, CE feature matrix (Platform Admin)
- Record available vs locked: projects, API keys, piece management, alerts, branding, audit logs, Git Sync, templates, import/export.

### [ ] 0.4 — Triggers & logic: webhook (local curl; ngrok only on laptop), schedule, branch, loop, delay, code step, HTTP piece; run logs, retries, failure display
- Needs pieces catalogue (blocked in cloud until network allowed).

### [ ] 0.5 — AI step with Gemini free key (practice data)

### [ ] 0.6 — Build the 6 starter flows as far as free/built-in pieces allow; export each flow JSON to `explore/flows/`
- 1 lead capture · 2 AI email sorter · 3 review request · 4 invoice reminder · 5 social lead alert · 6 generic monthly report (ADR-014)

### [ ] 0.7 — Backup → restore into a fresh local stack (pg_dump + .env), confirm a stored connection still decrypts

### [ ] 0.8 — Measure RAM/CPU idle and under 20 test runs

### [ ] 0.9 — Inspect run tables read-only for the failed-run detector (SPEC 10.3); Redis durability question (SPEC 9.7)

### [ ] 0.10 — Custom piece dev: hello-world piece in dev mode; how CE loads custom pieces (SPEC 14)

### [ ] 0.11 — Answer every *(verify)* item, finish `docs/EXPLORATION_REPORT.md`, owner review
