# ISSUE: Require successful CI before merge

Status: `pending`
Owner: System Architect (Codex)
Created: 2026-08-13
Updated: 2026-08-13
Related files: `.github/workflows/ci.yml`, `.github/workflows/governance-human-review.yml`, GitHub branch ruleset for `main`

## Roles

- Execution DRI: Codex
- Product / System Steward: unassigned
- Engineering DRI: unassigned
- System Architect: Codex
- Data / ML reviewer: not required
- Safety / Privacy reviewer: not required
- QA / Review approver: unassigned
- Contributors: none

## Goal

Prevent pull requests from merging into `main` until every required CI check has
completed successfully.

## Scope

- Inventory stable CI check names emitted for pull requests targeting `main`.
- Configure a GitHub branch ruleset or branch protection requiring those checks
  to pass before merge.
- Require the branch to be current with `main` before merging, unless the
  System Architect explicitly documents a safe exception.
- Confirm failed, skipped, pending, cancelled, and timed-out required checks
  block merge.

## Non-goals

- Do not make non-required or informational workflows merge blockers.
- Do not bypass `needs-human-review` or the governance-review gate.
- Do not change application behavior, data processing, or model execution.

## Acceptance criteria

- [ ] PRs targeting `main` cannot merge while a required check is queued or running.
- [ ] PRs targeting `main` cannot merge when any required check fails, is cancelled, or times out.
- [ ] Required checks include the repository's Python syntax, browser tests, and governance gate when those workflows apply.
- [ ] The ruleset requires an up-to-date branch before merge.
- [ ] The configuration and validation evidence are recorded without secrets.

## Work plan

- [ ] 1. Inspect existing branch rules and stable CI check names.
- [ ] 2. Propose the minimum ruleset change and obtain System Architect approval.
- [ ] 3. Apply the ruleset and validate pending/failing/successful PR behavior.
- [ ] 4. Obtain independent human review and archive the issue when accepted.

## Progress log

| Date | Status | Update | Evidence |
| --- | --- | --- | --- |
| 2026-08-13 | pending | Created at user request to make completed successful CI a hard merge prerequisite. | User request |

## Review / PR record

- Implementation: not started
- Validation: not run
- Data/privacy impact: repository metadata and CI status only; no conversation data access
- Reviewer: unassigned
- Decision: pending
- Follow-up issue IDs: 011

## Changelog

- 2026-08-13: Opened a System Architect task to require completed successful CI checks before merging to `main`.
