# opskit — operations kit (our code)

- Follow `docs/ai-workflow/rules/02-architecture.md`, `05-ops-scripts.md`, `06-reliability.md`.
- `bin/` entry points; `lib/` shared Bash functions; `schema/` JSON schemas; `templates/` render sources; `agent/` standalone host scripts; `flows/` templates; `hub/` ops-hub flows; `tests/` bats.
- `clients/` and `hosts/` are git-ignored registries with real data — never print their secrets, never commit them.
- Every command validates `client.yaml` first and exits non-zero on failure.
