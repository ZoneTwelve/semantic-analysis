# ISSUE: PM Clarification of System Architect Scope and Change Gates

Status: `pending`
Owner: unassigned
Created: 2026-08-13
Updated: 2026-08-13
Related files: `playbooks/roles-and-governance.md`, `playbooks/reviews-and-ci-governance.md`, `playbooks/worktrees-and-prs.md`, `issues/README.md`

## Roles

- Execution DRI: unassigned
- Product / System Steward: PM agent (assign before work starts)
- Engineering DRI: not required
- System Architect: unassigned
- Data / ML reviewer: not required
- Safety / Privacy reviewer: required for policy affecting safety/data paths
- QA / Review approver: unassigned
- Contributors: none

## Goal

Define an unambiguous repository policy for System Architect responsibility and
change gates: classify file-only/documentation work versus engineering changes,
state when CI is required, and state when explicit human review/`LGTM` is
required before a PR may merge.

## Scope

- Produce a change-classification matrix with examples from this repository.
- Define minimum CI/test requirements per change class.
- Define review requirements: automated checks, independent agent review, and
  explicit human `LGTM`/approval.
- Define merge authority, including when auto-merge is permitted, prohibited,
  or requires a named System Architect.
- Clarify System Architect responsibilities, handoffs, and overlap with PM,
  Engineer, QA, Safety/Privacy, and Release/Maintenance roles.
- Propose GitHub enforcement requirements (CODEOWNERS/rulesets/checks) without
  implementing them until a GitHub System Architect identity is designated.

## Non-goals

- Do not modify CI workflows, branch rulesets, CODEOWNERS, or GitHub settings.
- Do not rewrite current role policy while this discovery issue is pending.
- Do not grant autonomous merge authority for safety/data/CI changes.

## Required policy decisions

### 1. Change classification

Define at least these classes and their boundary cases:

| Class | Examples to decide | Required result |
| --- | --- | --- |
| Documentation-only | README, playbook, issue templates, app catalog | Specify when link/format checks suffice and when review is needed. |
| Tooling / test-only | test fixtures, test config, developer scripts | Specify CI and reviewer expectations. |
| Engineering | source, APIs, browser UI, dependencies, runtime behavior | Specify mandatory tests and independent approval. |
| Data / ML | schemas, preprocessing, models, manifests, evaluation | Specify data/ML and privacy review gates. |
| Safety / privacy | flagging, access, sensitive-data handling, review queues | Specify mandatory human approval and merge prohibition. |
| CI / architecture | `.github/**`, CI-invoked build/test configuration, permissions, rulesets | Specify System Architect ownership and approval. |

### 2. CI gates

Decide for each class:

- whether CI is required, recommended, or not applicable;
- minimum required checks (format, unit, browser, integration, security, etc.);
- who may waive a failing/non-applicable check and what evidence is required;
- whether CI configuration itself can be changed only by System Architect.

### 3. Human-in-the-loop merge gates

Define the exact meaning of `LGTM` / approval:

- acceptable evidence: GitHub review, signed issue-review artifact, or both;
- required reviewer role(s) by change class;
- when independent agent approval is enough;
- when explicit human owner approval is mandatory;
- whether author self-merge is allowed after approval;
- auto-merge policy and hard prohibitions.

At minimum, document that explicit human approval is mandatory for safety,
privacy, CI/architecture, external exposure, production deployment, destructive
operations, and changes involving sensitive data access or retention.

## Acceptance criteria

- [ ] A documented classification matrix maps every common repository change to
  CI, reviewer, human-approval, and merge requirements.
- [ ] System Architect scope, decision rights, and prohibited actions are clear.
- [ ] `LGTM`/approval and reviewer-artifact requirements are unambiguous and
  auditable.
- [ ] Policy distinguishes documentation-only changes from engineering changes
  without allowing safety-sensitive work to be misclassified.
- [ ] Required updates to playbooks, issue templates, GitHub settings, and
  branch rules are listed as follow-up implementation issues.

## Work plan

- [ ] 1. Assign PM/System Steward and System Architect participants.
- [ ] 2. Inventory repository change types and propose classification matrix.
- [ ] 3. Decide CI and human-approval gates with Safety/Privacy and QA input.
- [ ] 4. Record merge/auto-merge policy and GitHub enforcement backlog.
- [ ] 5. Open separate implementation issues for accepted policy changes.

## Dependencies

- `issues/active/review_artifacts_and_ci_architect_009.md` provides a draft
  review-artifact and CI-governance baseline; this issue decides the final
  policy boundaries before any live GitHub enforcement change.
- A GitHub System Architect user/team identity is required before creating
  CODEOWNERS or branch ruleset implementation work.

## Progress log

| Date | Status | Update | Evidence |
| --- | --- | --- | --- |
| 2026-08-13 | pending | Created at user request for PM-led clarification of change classification, CI, human `LGTM`, and System Architect merge authority. | `playbooks/roles-and-governance.md`, `playbooks/reviews-and-ci-governance.md` |

## Review / PR record

- Implementation: policy discovery not started
- Validation: not run
- Data/privacy impact: policy will govern sensitive-data and safety changes; Safety/Privacy review required before acceptance
- Reviewer: unassigned
- Decision: pending
- Follow-up issue IDs: to be created after policy decisions

## Changelog

- 2026-08-13: Created PM-led System Architect scope and change-gate clarification issue.
