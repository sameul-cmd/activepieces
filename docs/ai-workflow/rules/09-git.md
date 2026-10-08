# Git rules

- Conventional commits (upstream uses commitlint): `feat(opskit): …`, `fix(opskit): …`, `feat(pieces): …`, `test: …`, `docs: …`, `chore: …`.
- Commit after each completed task; never a broken state. **Push after every commit** (the next session may run on a different agent or machine and only sees what is on GitHub). Branches: `phase-N-name` (or the branch the session was given); upstream syncs on `sync/<tag>`.
- Never commit `.env`, keys, `opskit/clients/`, `opskit/hosts/`, dumps, rclone configs.
- Never push to `upstream`; our pushes go to `origin` only.
- Commit before risky changes so they can be reverted.
