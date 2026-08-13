# ISSUE: Human-review gate enforcement follow-up

Status: `in_review`
Owner: System Architect (Codex)
Created: 2026-08-13
Updated: 2026-08-13
Related files: `.github/workflows/governance-human-review.yml`, GitHub branch ruleset for `main`, `playbooks/reviews-and-ci-governance.md`

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

Make the governance human-review requirement reliable and enforceable after a
PR is rebased, force-pushed, or otherwise updated, so a failed check cannot be
silently bypassed by a merge override.

## Context

PR #9 was force-merged while `governance-review-required` was failing. The
current workflow correctly surfaced missing independent approval, but GitHub
branch settings allowed an administrator override. A rebase or later commit
can also invalidate the practical meaning of an earlier approval.

## Scope

- Define expected approval behavior after synchronize/rebase/force-push events.
- Decide whether the workflow must require an approval submitted after the
  latest source commit, or rely on GitHub's stale-review dismissal setting.
- Inventory whether `main` permits admin bypass, and propose an explicit,
  documented exception process if it does.
- Configure or propose branch rules that make the governance check required
  for `main` and require it to pass before ordinary merge.
- Specify a trusted reviewer policy; a GitHub non-bot account is only a
  technical signal, not proof of a human or authorized reviewer.
- Add a regression validation plan using harmless documentation-only PRs.

## Non-goals

- Do not retroactively rewrite PR #9 or remove its merge history.
- Do not prohibit emergency overrides without first defining incident authority
  and an audit trail.
- Do not grant broad repository-admin permissions to agents.

## Acceptance criteria

- [x] The policy states how approvals are invalidated or re-requested after a source-branch update.
- [ ] `main` branch rules require the governance check when it applies and block ordinary merge until success.
- [ ] Any permitted administrator/emergency bypass is explicitly scoped, logged, and followed by review.
- [ ] The trusted reviewer identity/ownership model is documented.
- [ ] A test PR demonstrates the expected pending, failed, approved, and updated-branch outcomes.

## Work plan

- [x] 1. Audit PR #9 review/check timeline and current GitHub ruleset.
- [x] 2. Write the decision record for stale approvals and bypass authority.
- [x] 3. Implement the minimum workflow change for stale approvals.
- [ ] 4. Validate with a non-production documentation PR.
- [ ] 5. Obtain independent human approval before merge.

## Progress log

| Date | Status | Update | Evidence |
| --- | --- | --- | --- |
| 2026-08-13 | pending | Opened after PR #9 was force-merged while the governance human-review check was failing. | PR #9 status history |
| 2026-08-13 | in_progress | Updated the governance workflow to require a formal GitHub `APPROVED` review attached to the current PR head SHA; earlier approvals no longer satisfy the CI gate after a push or rebase. CI configuration files are now governed paths. | `.github/workflows/governance-human-review.yml` |
| 2026-08-13 | in_review | Static workflow review complete. GitHub branch ruleset configuration and independent review remain required before merge. | `git diff --check`, PR #12 |

## Review / PR record

- Implementation: formal approval must match the latest PR commit; CI configuration joins governed paths
- Validation: `git diff --check`; workflow logic reviewed against GitHub review `commit_id` and PR `head.sha`
- Data/privacy impact: GitHub PR metadata and branch-rule configuration only; no conversation data access
- Reviewer: unassigned
- Decision: pending
- Follow-up issue IDs: 011, 014

## Changelog

- 2026-08-13: Opened enforcement follow-up after a governance review check was bypassed by force merge.
- 2026-08-13: Required a formal GitHub approval on the latest PR commit and made CI configuration a governed path.
