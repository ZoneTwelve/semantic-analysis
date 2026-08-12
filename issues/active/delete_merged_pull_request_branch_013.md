# ISSUE: Delete merged pull-request source branches

Status: `in_review`
Owner: System Architect (Codex)
Created: 2026-08-13
Updated: 2026-08-13
Related files: `.github/workflows/delete-merged-pr-branch.yml`

## Roles

- Execution DRI: Codex
- Product / System Steward: unassigned
- Engineering DRI: Codex
- System Architect: Codex
- Data / ML reviewer: not required
- Safety / Privacy reviewer: not required
- QA / Review approver: unassigned
- Contributors: none

## Goal

Delete a same-repository pull request's source branch only after that pull
request has been successfully merged.

## Scope

- Run on the `pull_request` closed event.
- Delete the source ref only when the PR is merged and originates in this
  repository.
- Never delete the repository default branch.

## Non-goals

- Do not delete unmerged or closed-without-merge PR branches.
- Do not delete fork branches.
- Do not modify branch-protection rules or PR review policy.

## Acceptance criteria

- [x] The workflow runs only after a pull request closes.
- [x] A merged same-repository PR deletes its non-default source branch.
- [x] Unmerged PRs, fork PRs, and the default branch are excluded.
- [x] The workflow has only the permissions necessary to remove the ref.

## Work plan

- [x] 1. Add guarded branch-deletion workflow.
- [x] 2. Validate workflow structure and guard conditions.
- [ ] 3. Obtain independent human review before merge.

## Progress log

| Date | Status | Update | Evidence |
| --- | --- | --- | --- |
| 2026-08-13 | in_progress | Created isolated System Architect branch for source-branch cleanup automation. | `issue/013-delete-merged-branches` |
| 2026-08-13 | in_review | Added metadata-only workflow that deletes only merged, same-repository, non-default source branches. | `.github/workflows/delete-merged-pr-branch.yml` |

## Review / PR record

- Implementation: guarded `pull_request.closed` branch-deletion workflow
- Validation: static YAML and condition review pending command verification
- Data/privacy impact: uses PR metadata and Git ref deletion only; it does not access conversation data
- Reviewer: unassigned
- Decision: pending independent human review
- Follow-up issue IDs: 011 (governance review gate)

## Changelog

- 2026-08-13: Added a guarded CI workflow to remove source branches after successful PR merges.
