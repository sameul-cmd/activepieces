# Security & client-data rules

## Never read, print, or commit
- `.env` files, `opskit/clients/**`, `opskit/hosts/**`, private keys (age, SSH), DB dumps, rclone configs, tokens.

## Always
- Generate secrets with `openssl rand`; abort if any required secret is empty.
- Destructive actions (delete volume/stack, restore over data, drop DB, prune remote backups early) need `--yes` + typed client id + owner approval in chat.
- Hosts: SSH keys only, root login disabled, ufw 22/80/443, Postgres/Redis never published, `.env` mode 600.
- Encrypt `.env` escrow with the owner's age public key; never store the private key in the repo or on hosts.
- Detectors/reports use a read-only DB role and read-only SQL.
- Alert/report payloads: no secrets, no full personal data; error excerpts ≤ 300 chars.
- The owner's AI endpoint (BYOK) only with practice data; client AI steps use client-owned keys. Never print or commit AI keys.
- Never set `AP_EDITION=ee`, never touch `packages/ee/`, never add a license key.
