# ISSUE: Agent Roles and Governance Framework

Status: `in_review`
Owner: Codex
Created: 2026-08-13
Updated: 2026-08-13
Related files: `playbooks/roles-and-governance.md`, `playbooks/README.md`, `issues/README.md`, `issues/templates/issue.md`, `AGENT.md`, `CLAUDE.md`

## Goal

Define reusable agent roles, authority boundaries, onboarding requirements, and
multi-agent coordination rules for repository development and upgrades.

## Scope

- Add an agent roles/governance playbook.
- Require role and review ownership in new issues.
- Add onboarding and change-control rules to the repository entry policies.

## Roles

- Execution DRI: Codex
- Product / System Steward: Codex
- Engineering DRI: Codex
- Data / ML reviewer: not required
- Safety / Privacy reviewer: not required
- QA / Review approver: unassigned
- Contributors: none

## Non-goals

- No autonomous production deployment or external outreach.
- No change to data/safety access controls beyond documenting ownership.

## Acceptance criteria

- [ ] Defined roles cover product, engineering, data/ML, safety/privacy, QA,
  release/maintenance, and reviewer responsibilities.
- [ ] PM agent authority to maintain playbooks and review standards is scoped
  and auditable.
- [ ] New issue template supports multiple roles while retaining one execution
  DRI.
- [ ] README, AGENT.md, CLAUDE.md, and playbook routing require role-aware
  onboarding and collaboration.

## Work plan

- [x] 1. Create the governance issue and set one execution owner.
- [x] 2. Define roles, authority boundaries, and escalation rules.
- [x] 3. Update issue workflow/template for multi-role work.
- [x] 4. Update entry policies and validate cross-references.

## Progress log

| Date | Status | Update | Evidence |
| --- | --- | --- | --- |
| 2026-08-13 | in_progress | Created governance issue and began role-framework design. | This issue |
| 2026-08-13 | in_progress | Added role-based onboarding, authority boundaries, safety stop-the-line rules, and multi-agent handoff protocol. | `playbooks/roles-and-governance.md` |
| 2026-08-13 | in_review | Updated issue template/workflow and repository entry policies; cross-references verified. | `issues/README.md`, `issues/templates/issue.md`, `AGENT.md`, `CLAUDE.md` |

## Review / PR record

- Implementation: role/governance playbook, issue roles metadata, and onboarding policy updates complete
- Validation: Markdown cross-reference and legacy tracker-reference checks passed
- Data/privacy impact: governance-only documentation; no data access change
- Reviewer: unassigned
- Decision: pending
- Follow-up issue IDs: none

## Changelog

- 2026-08-13: Opened governance framework issue for role-based agent onboarding and review.
- 2026-08-13: Added role governance, multi-agent coordination, and onboarding rules; awaiting independent review.
