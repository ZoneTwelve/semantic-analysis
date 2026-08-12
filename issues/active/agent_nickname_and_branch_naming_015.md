# ISSUE: Require Agent Nicknames and Nickname-Based Branches

Status: `in_review`
Owner: Codex
Agent nickname: codex
Created: 2026-08-13
Updated: 2026-08-13
GitHub issue: [#11](https://github.com/ZoneTwelve/semantic-analysis/issues/11)
Related files: `AGENT.md`, `CLAUDE.md`, `playbooks/roles-and-governance.md`, `playbooks/worktrees-and-prs.md`, `issues/README.md`, `issues/templates/issue.md`, `issues/templates/feature-request.md`

## Roles

- Execution DRI: Codex
- Product / System Steward: Codex
- Engineering DRI: not required
- Data / ML reviewer: not required
- Safety / Privacy reviewer: not required
- QA / Review approver: unassigned
- Contributors: none

## Goal

Make agent ownership and branch ownership unambiguous by requiring an agent
nickname during onboarding and using `<nickname>/<feature>` for new work
branches.

## Scope

- Define a stable, lowercase-kebab-case agent nickname.
- Require onboarding and issue records to identify the nickname.
- Replace the issue-number branch convention with `<nickname>/<feature>` and
  document matching worktree/PR examples.

## Non-goals

- No rename or forced migration of existing branches, worktrees, or pull requests.
- No change to data, application, CI, or GitHub administrative settings.

## Acceptance criteria

- [x] Onboarding requires an agent nickname before meaningful work.
- [x] New implementation branches follow `<nickname>/<feature>`.
- [x] The worktree/PR guide includes valid naming examples and preserves the
  existing isolation and ownership safeguards.
- [x] Issue guidance/templates record the nickname without replacing named
  human/agent accountability fields.
- [x] Cross-references and `git diff --check` pass; independent governance
  review is requested.

## Work plan

- [x] 1. Create an isolated worktree and inspect current onboarding and branch rules.
- [x] 2. Add nickname and branch-naming requirements.
- [x] 3. Validate documentation and request independent review.

## Progress log

| Date | Status | Update | Evidence |
| --- | --- | --- | --- |
| 2026-08-13 | in_progress | Created isolated `codex/agent-nickname-policy` worktree from `origin/main`; reviewed onboarding, worktree, issue, and entry policies. | `git worktree add`; `playbooks/roles-and-governance.md`; `playbooks/worktrees-and-prs.md` |
| 2026-08-13 | in_progress | Added mandatory nickname declaration, `<nickname>/<feature>` branch naming, and issue/template traceability while preserving historical branch names. | `AGENT.md`, `CLAUDE.md`, `playbooks/roles-and-governance.md`, `playbooks/worktrees-and-prs.md`, `issues/` |
| 2026-08-13 | in_progress | Created linked GitHub issue #11 with a multiline Markdown body. | https://github.com/ZoneTwelve/semantic-analysis/issues/11 |
| 2026-08-13 | in_review | Documentation cross-references and diff whitespace checks passed; independent governance review requested. | `rg -n "agent nickname|<nickname>/<feature>" …`; `git diff --check` |

## Review / PR record

- Implementation: onboarding, branch naming, issue guidance, and reusable templates updated.
- Validation: cross-reference search and `git diff --check` passed.
- Data/privacy impact: governance-only documentation; no data access or behavioral change.
- Reviewer: unassigned
- Decision: pending
- Follow-up issue IDs: none

## Changelog

- 2026-08-13: Required stable onboarding nicknames and `<nickname>/<feature>` branches for new work; awaiting independent review.
