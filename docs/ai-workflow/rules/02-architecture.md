# Architecture rules (mirror of SPEC Section 3)

- Our code lives only in `opskit/`, `packages/pieces/custom/`, `.github/workflows/opskit-*.yml`, `docs/`, IDE config. Everything else is upstream (`04-upstream-fork.md`).
- One client = one stack: own compose project (`-p <client_id>`), `.env`, volumes `<id>_postgres`/`<id>_redis`, domain, backups. Never share data between stacks.
- `client.yaml` (validated by `opskit/schema/client.schema.json`) drives rendering; never hand-edit compose/.env on servers — change config, re-render, redeploy.
- Rendered stacks always: pinned image tag, `AP_EDITION=ce`, worker `AP_FRONTEND_URL=http://app`, worker replicas from config (default 1), memory limits, healthchecks, only Caddy publishing ports.
- Hosts talk to the owner only through the ops-hub (heartbeats, alerts, reports); fallback email if the hub is unreachable.
- Scripts are Bash, `set -euo pipefail`, idempotent; host agent scripts in `opskit/agent/` are standalone (no repo needed on hosts).
- Custom pieces follow upstream piece conventions and ship only via our CI image.
- Follow `docs/TECH_ARCHITECTURE.md` Section 3 layout and command pattern.
