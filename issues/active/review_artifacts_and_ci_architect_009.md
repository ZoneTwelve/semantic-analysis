# ISSUE: Independent Review Artifacts and CI Architect Ownership

Status: `in_progress`
Owner: Codex
Created: 2026-08-13
Updated: 2026-08-13
Related files: `playbooks/reviews-and-ci-governance.md`, `playbooks/roles-and-governance.md`, `issues/templates/review.md`, `issues/README.md`

## Roles

- Execution DRI: Codex
- Product / System Steward: Codex
- Engineering DRI: Codex
- System Architect: unassigned
- Data / ML reviewer: not required
- Safety / Privacy reviewer: not required
- QA / Review approver: unassigned
- Contributors: none

## Goal

Add an independent review-artifact workflow and define System Architect
ownership for CI changes, without changing PM-owned source, CI, or entry-policy
files that are currently dirty.

## Scope

- Add a review artifact template and independent-review process.
- Add System Architect role and CI-change ownership/approval constraints.
- Document GitHub enforcement prerequisites without inventing an architect
  identity or changing live CI configuration.

## Non-goals

- Do not modify `.github/`, CI workflows, `AGENT.md`, `CLAUDE.md`, `README.md`,
  or source files while another agent owns uncommitted changes there.
- Do not create CODEOWNERS/rulesets without a designated GitHub architect user
  or team and explicit authorization.

## Acceptance criteria

- [ ] Review agents have a separate artifact/template and do not concurrently edit implementation issues.
- [ ] System Architect role explicitly owns CI configuration changes and required approval.
- [ ] CI-controlled paths, PR requirements, and GitHub enforcement setup are documented.
- [ ] New issue workflow links to the independent review process.

## Work plan

- [x] 1. Create issue and identify PM-owned files to avoid.
- [x] 2. Add review artifact template and review/CI playbook.
- [x] 3. Add System Architect role and issue workflow references.
- [x] 4. Validate links and request independent documentation review.

## Progress log

| Date | Status | Update | Evidence |
| --- | --- | --- | --- |
| 2026-08-13 | in_progress | Created governance issue. Current PM-owned dirty files include entry policies, CI-related files, source, tests, and Issue 006; excluded from scope. | `git status --short` |
| 2026-08-13 | in_progress | Added separate review-artifact template, independent-review process, System Architect role, and CI ownership controls. | `issues/templates/review.md`, `playbooks/reviews-and-ci-governance.md` |
| 2026-08-13 | in_review | Updated clean issue/playbook routing files and validated references. PM-owned entry-policy changes intentionally left untouched for later integration. | `issues/README.md`, `playbooks/README.md`, `playbooks/roles-and-governance.md` |

## Review / PR record

- Implementation: independent review template and CI Architect governance documentation complete
- Validation: Markdown cross-reference check pending independent review
- Data/privacy impact: governance-only documentation; no data access change
- Reviewer: unassigned
- Decision: pending
- Follow-up issue IDs: none

## Changelog

- 2026-08-13: Opened review-artifact and CI-architect governance issue; deferred live CI enforcement pending architect identity.
- 2026-08-13: Added independent review artifacts and CI Architect ownership policy; awaiting review and PM-policy integration.
