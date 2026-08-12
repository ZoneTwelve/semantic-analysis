# ISSUE: Governance Human-Review CI Gate

Status: `in_progress`
Owner: System Architect (Codex)
Created: 2026-08-13
Updated: 2026-08-13
Related files: `.github/workflows/governance-human-review.yml`, `playbooks/reviews-and-ci-governance.md`, `issues/README.md`

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

Block pull requests that change repository governance guidance or CI-controlled
paths until they carry the `needs-human-review` label and have an independent
GitHub PR approval.

## Scope

- Add a GitHub Actions pull-request gate for governed guidance and CI-controlled
  paths.
- Require `needs-human-review` and a non-author, non-bot `APPROVED` review for
  those PRs.
- Document that GitHub branch rules must require this check before the CI gate
  becomes an enforced merge block.

## Non-goals

- Do not classify a GitHub account as a real human; GitHub approval is the
  technical proxy, and owner/team identity must be enforced by GitHub rules.
- Do not alter branch rulesets, CODEOWNERS, secrets, deployments, or any other
  CI workflow in this issue.
- Do not auto-apply, remove, or bypass the `needs-human-review` label.

## Acceptance criteria

- [ ] A PR changing governed guidance or CI-controlled paths fails when it lacks
  `needs-human-review`.
- [ ] A labeled governed-guidance PR fails until a non-author, non-bot approval
  exists; it re-evaluates on review events.
- [ ] A PR outside governed guidance paths passes without requiring the label.
- [ ] The workflow has least-privilege read permissions and does not read
  repository data or execute PR code.
- [ ] Documentation states the GitHub branch-ruleset follow-up required to make
  this a hard merge block.

## Work plan

- [x] 1. Define gated paths and review signal.
- [x] 2. Implement the pull-request status check.
- [x] 3. Add test/validation plan and enforcement documentation.
- [ ] 4. Obtain independent System Architect/QA review before merge.

## Progress log

| Date | Status | Update | Evidence |
| --- | --- | --- | --- |
| 2026-08-13 | in_progress | Created System Architect CI issue after user assigned CI ownership. GitHub label `needs-human-review` already exists. | GitHub repository labels |
| 2026-08-13 | in_progress | Added a metadata-only PR gate: governed guidance changes require `needs-human-review` plus an independent, non-author, non-bot GitHub approval. | `.github/workflows/governance-human-review.yml` |
| 2026-08-13 | in_review | Workflow YAML and issue structure checks passed. Branch ruleset enforcement remains a follow-up; this PR itself requires independent review. | `python` YAML parse, issue structure check |
| 2026-08-13 | in_progress | Corrected governed-path coverage to include CI workflow/action/Dependabot files, so CI changes cannot bypass the human-review gate. | `.github/workflows/governance-human-review.yml` |

## Review / PR record

- Implementation: governance human-review workflow updated to gate CI-controlled paths
- Validation: workflow YAML parse passed; logic reviewed against GitHub pull-request and review event payloads
- Data/privacy impact: workflow reads PR metadata and changed paths only; it does not read conversation data or execute PR code
- Reviewer: unassigned
- Decision: pending
- Follow-up issue IDs: branch-ruleset/CODEOWNERS enforcement to be created after policy owner identity is supplied

## Changelog

- 2026-08-13: Opened CI gate issue requiring labeled, independent review for governance guidance changes.
- 2026-08-13: Added metadata-only CI gate; awaiting independent architecture/QA review.
- 2026-08-13: Added CI-controlled paths to the gate after validating that the initial workflow did not gate its own CI change.
