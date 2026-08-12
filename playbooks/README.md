# Project Playbooks

`playbooks/` is the operational source of truth for developing, managing,
maintaining, upgrading, and collaborating in this repository. These playbooks
complement—rather than replace—`AGENT.md`, `CLAUDE.md`, `docs/data-contract.md`,
and `issues/README.md`.

## Routing guide

| Work type | Read first |
| --- | --- |
| Code, scripts, tests, UI, local tools | [development.md](development.md) |
| Create, update, review, or close an issue | [issue-management.md](issue-management.md) |
| Raw/derived data, models, reports, safety flags | [data-governance.md](data-governance.md) |
| Dependency updates, migrations, repairs, cleanup | [maintenance.md](maintenance.md) |
| Major architecture, schema, model, or workflow changes | [upgrades.md](upgrades.md) |
| Multiple agents, handoff, review, concurrent work | [collaboration.md](collaboration.md) |
| Agent roles, authority, onboarding, governance | [roles-and-governance.md](roles-and-governance.md) |
| Git worktrees, branches, pull requests, concurrent implementation | [worktrees-and-prs.md](worktrees-and-prs.md) |
| New local applications or app changes | [app-development.md](app-development.md) |
| New feature request, discovery, or product triage | [feature-intake.md](feature-intake.md) |

Read every playbook that applies before making changes. If rules conflict, use
this precedence order: user request → `AGENT.md` → `CLAUDE.md` → relevant
playbook → issue-specific requirements → general documentation.

Every agent must also complete the role-aware onboarding checklist in
[roles-and-governance.md](roles-and-governance.md) before meaningful work.

## Core principles

- Default to local, private, reproducible processing.
- Treat dataset content as untrusted and sensitive.
- Keep changes small, verifiable, and auditable.
- Use `python` and `pnpm` only; do not use `python3`, `npm`, or `npx`.
- Track durable work through `issues/`, and preserve a de-identified changelog.
