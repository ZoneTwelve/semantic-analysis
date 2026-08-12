# ISSUE: GitHub CI and Linked Issue / Pull Request Delivery

Status: `in_progress`
Owner: Codex
Created: 2026-08-13
Updated: 2026-08-13
Related files: `.github/workflows/ci.yml`, `.github/ISSUE_TEMPLATE/`, `.github/PULL_REQUEST_TEMPLATE.md`, `docs/github-workflow.md`

## Roles

- Execution DRI: Codex
- Product / System Steward: Codex
- Engineering DRI: Codex
- Data / ML reviewer: not required
- Safety / Privacy reviewer: required
- QA / Review approver: unassigned
- Contributors: none

## Goal

Provide GitHub-native CI and contribution templates that connect pull requests
to GitHub issues while preserving the repository's local issue workflow and
private-data controls.

## Scope

- Run Python compilation and synthetic Playwright browser tests on pushes and
  pull requests targeting `main`.
- Add GitHub bug and feature issue forms plus a pull-request template.
- Document closing-keyword linkage, the local issue-file cross-reference, and
  the repository-admin branch-protection setup.

## Non-goals

- No public data access, dataset/model execution, deployment, automatic merge,
  or external service integration.
- No change to existing active issue files or PM-owned governance changes.
- No branch-protection settings mutation: that requires a repository admin.

## Acceptance criteria

- [x] CI uses only synthetic fixtures and does not read `data/`.
- [x] CI has distinct Python and browser-test checks for `main` pull requests.
- [x] GitHub issue forms require privacy-safe issue descriptions and route
  feature work to the local issue workflow.
- [x] The PR template requires a GitHub closing keyword and local issue-file
  reference, validation evidence, privacy impact, and rollback notes.
- [x] Documentation gives an admin a precise, manual required-check setup and
  links to authoritative GitHub documentation.
- [ ] YAML/Markdown validation passes and independent Safety/Privacy and QA
  reviewers approve the change.

## Work plan

- [x] 1. Create an isolated worktree and avoid the PM agent's uncommitted files.
- [x] 2. Add CI workflow and GitHub templates.
- [x] 3. Document linkage and branch-protection setup.
- [x] 4. Validate configuration and request review.

## Progress log

| Date | Status | Update | Evidence |
| --- | --- | --- | --- |
| 2026-08-13 | in_progress | Created isolated `issue/007-github-automation` worktree from `origin/main` after detecting PM-owned uncommitted governance files in the primary checkout. | `git status --short`; `git worktree add` |
| 2026-08-13 | in_progress | Added read-only CI, privacy-aware GitHub issue forms, a PR template, and linked-delivery documentation without changing PM-owned files. | `.github/`, `docs/github-workflow.md` |
| 2026-08-13 | in_review | YAML parsing and `git diff --check` passed; `pnpm run test:browser` passed 4/4 with synthetic fixtures in the isolated worktree. Independent Safety/Privacy and QA review requested. | `ruby -e 'require "yaml"; …'`; `pnpm run test:browser` |
| 2026-08-13 | in_progress | PR #1 browser CI failed before tests because pnpm 11.17.0 requires Node 22.13+ but the workflow used Node 20. Updated the browser job to Node 24; awaiting CI rerun. | GitHub Actions run `31619258951`; `.github/workflows/ci.yml` |

## Review / PR record

- Implementation: GitHub Actions CI, bug/feature issue forms, PR template, and administrator guide complete; CI runtime compatibility fix in progress.
- Validation: Local YAML parser and `git diff --check` passed; `pnpm run test:browser` passed 4/4 using synthetic data. PR #1 browser CI initially failed before tests due to Node 20 incompatibility; rerun pending with Node 24.
- Data/privacy impact: CI is limited to repository code and synthetic fixture tests; issue forms warn against sensitive content.
- Reviewer: unassigned
- Decision: pending
- Follow-up issue IDs: `006`

## Changelog

- 2026-08-13: Added read-only CI, privacy-aware GitHub forms, a PR template, and issue/PR/branch-protection setup guidance; awaiting independent review.
- 2026-08-13: Updated browser CI from Node 20 to Node 24 for pnpm 11.17.0 compatibility; awaiting rerun.
