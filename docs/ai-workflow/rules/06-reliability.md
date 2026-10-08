# Reliability rules (backups, alerts, upgrades)

- A backup counts only if: dump + encrypted `.env` exist locally and remotely, sizes > 0, and a heartbeat reached the ops-hub.
- Restores go into a fresh stack; never over a running stack without `--overwrite --yes`.
- Monthly automated restore test per client; result appears in the care report.
- Failed-run detector: read-only SQL, runs every 5 min, de-duplicates (30 min window), includes flow name + run link.
- Every alert names client, severity (`info|warn|critical`), what happened, first action to take; owner always gets Telegram.
- Upgrades: backup → staging on new image → smoke tests → promote → smoke → rollback on any failure; record history.
- Never lose `AP_ENCRYPTION_KEY`: escrow before first deploy; verify decryption in restore tests.
