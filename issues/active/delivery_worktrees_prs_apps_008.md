# ISSUE: Worktree, Pull Request, App, and Feature Delivery Workflow

Status: `in_review`
Owner: Codex
Created: 2026-08-13
Updated: 2026-08-13
Related files: `playbooks/worktrees-and-prs.md`, `playbooks/app-development.md`, `playbooks/feature-intake.md`, `issues/templates/feature-request.md`, `issues/README.md`, `AGENT.md`, `CLAUDE.md`

## Roles

- Execution DRI: Codex
- Product / System Steward: Codex
- Engineering DRI: Codex
- Data / ML reviewer: not required
- Safety / Privacy reviewer: not required
- QA / Review approver: unassigned
- Contributors: none

## Goal

Establish a safe, repeatable workflow for feature requests, isolated worktrees,
GitHub pull requests, and local-application delivery without disrupting work
owned by another agent.

## Scope

- Add playbooks for worktrees/PRs, feature intake, and app delivery.
- Add a feature-request issue template.
- Update repository governance to require issue-to-branch/worktree/PR linkage.

## Non-goals

- Do not create or modify a product feature or application implementation.
- Do not alter another agent's uncommitted files, issue files, or branches.
- Do not automate merge, deployment, or external publishing.

## Acceptance criteria

- [ ] Worktree and PR naming, lifecycle, review, cleanup, and conflict rules are documented.
- [ ] New app and feature request workflows require issue scope, ownership, tests, privacy review, and catalog documentation.
- [ ] New feature request template contains product, technical, data/privacy, and release questions.
- [ ] AGENT.md and CLAUDE.md require these playbooks when applicable.

## Work plan

- [x] 1. Create issue and identify PM-owned files to avoid.
- [x] 2. Add worktree/PR, app-development, and feature-intake playbooks.
- [x] 3. Add feature template and issue workflow cross-references.
- [x] 4. Update agent onboarding rules and validate links.

## Progress log

| Date | Status | Update | Evidence |
| --- | --- | --- | --- |
| 2026-08-13 | in_progress | Created delivery-governance issue. Detected and excluded PM-owned `README.md`, `apps/`, and issues `004`/`005` from this work. | `git status --short`, `issues/active/` |
| 2026-08-13 | in_progress | Added isolated worktree/PR, feature intake, and app-delivery playbooks plus a feature-request template. | `playbooks/`, `issues/templates/feature-request.md` |
| 2026-08-13 | in_review | Added role-aware workflow cross-references and verified policy links without touching PM-owned files. | `issues/README.md`, `AGENT.md`, `CLAUDE.md` |

## Review / PR record

- Implementation: delivery/governance documents and feature template complete
- Validation: pending independent documentation review
- Data/privacy impact: governance-only documentation; no data access change
- Reviewer: unassigned
- Decision: pending
- Follow-up issue IDs: none

## Changelog

- 2026-08-13: Opened isolated-delivery workflow issue; explicitly excluded active PM-owned files.
- 2026-08-13: Added worktree/PR, app-development, and feature-intake governance; awaiting review.
