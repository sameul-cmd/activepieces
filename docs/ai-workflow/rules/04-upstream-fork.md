# Upstream fork rules

- Upstream `AGENTS.md`/`CLAUDE.md` govern upstream code; follow them if an approved patch touches upstream files.
- `main` = pinned release tag + our commits; `upstream` remote fetch-only; never merge upstream automatically; sync only via `docs/UPSTREAM_SYNC.md` when the owner asks.
- Upstream GitHub Actions stay disabled in the fork; our CI lives in `.github/workflows/opskit-*.yml`.
- Changing any upstream file needs approval + ledger row in `docs/UPSTREAM_CHANGES.md` + test, in one commit.
- Items marked *(verify)* in SPEC must be verified against the pinned version (source, docs, running instance) and recorded in `docs/ASSUMPTIONS.md` before code depends on them.
