# packages/pieces/custom — our custom pieces

- Follow upstream piece conventions (see upstream AGENTS.md/docs) and `docs/ai-workflow/rules/07-pieces-flows.md`.
- Tests for every action/trigger; auth via piece props; no secrets in code.
- Shipped only as CI-built archives uploaded with `opskit pieces push` (ADR-016). Build: `TS_NODE_TRANSPILE_ONLY=true npm run build-piece <name>`.
