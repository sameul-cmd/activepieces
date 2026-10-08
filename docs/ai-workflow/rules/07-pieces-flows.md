# Custom pieces & flow template rules

- Custom pieces live in `packages/pieces/custom/<name>`; use upstream's piece CLI/framework and naming; each action/trigger has tests; no secrets in code (piece auth props only).
- Pieces are shipped only as CI-built archives (`opskit-pieces.yml`) uploaded with `opskit pieces push` (ADR-016); bump the piece version for every change; clients run the official image.
- Flow templates: `flow.json` (exported, placeholders instead of real IDs/keys), `README.md`, `test/` payloads, `CHECKLIST.md`; every template includes a failure-notification convention.
- Templates must import into a fresh CE stack of the pinned version before they count as done.
