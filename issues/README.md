# Issue Workflow

`issues/` is the local, file-based GitHub Issue / PR workflow for this
repository. Use it when work needs durable scope, progress, review, handoff,
or a changelog—not for one-line, immediately completed edits.

## Directory layout

```text
issues/
├── README.md                 # workflow and status rules
├── CHANGELOG.md              # accepted/done issue summaries
├── templates/
│   └── issue.md              # starting point for new issues
├── reviews/                  # independent reviewer artifacts
├── active/                   # pending, in_progress, blocked, in_review, changes_requested
└── archive/
    ├── done/                 # accepted issues; immutable except clerical fixes
    └── cancelled/            # intentionally stopped issues
```

Move an issue—not copy it—between `active/` and `archive/` when its terminal
status changes. Its filename and numeric ID remain unchanged.

## Development stack in issues

Use `pnpm` for JavaScript commands and `python` for Python commands in every
issue, progress log, validation record, and review/PR record. Do not document
or recommend `npm`, `npx`, `python3`, or `package-lock.json` as active project
commands. Historical records are preserved as evidence and need not be edited.

## File naming

Create one issue file per work item under `issues/active/`:

```text
issues/active/<issue>_<id>.md
```

Examples:

```text
issues/active/browser_go_emotions_001.md
issues/active/negative_review_export_002.md
```

Use lowercase `snake_case` for `<issue>` and a three-digit, monotonically
increasing `<id>`. Never rename an existing issue file after work begins,
because the path is its stable local identifier.

For a new user-facing capability, start from
`issues/templates/feature-request.md` and follow
[feature-intake.md](../playbooks/feature-intake.md). For implementation, use
one issue branch/worktree and one pull request as defined in
[worktrees-and-prs.md](../playbooks/worktrees-and-prs.md).

## Required issue format

Every issue starts with this metadata block:

```markdown
# ISSUE: Short title

Status: `pending`
Owner: unassigned
Created: YYYY-MM-DD
Updated: YYYY-MM-DD
Related files: `path/one`, `path/two`

## Roles

- Execution DRI: unassigned
- Product / System Steward: unassigned
- Engineering DRI: unassigned
- System Architect: not required
- Data / ML reviewer: not required
- Safety / Privacy reviewer: not required
- QA / Review approver: unassigned
- Contributors: none

## Goal

## Scope

## Non-goals

## Acceptance criteria

- [ ] Criterion that can be verified.

## Work plan

- [ ] 1. First bounded task.

## Progress log

| Date | Status | Update | Evidence |
| --- | --- | --- | --- |
| YYYY-MM-DD | pending | Issue created. | — |

## Review / PR record

- Implementation: not started
- Validation: not run
- Reviewer: unassigned
- Decision: pending

## Changelog

- Unreleased: issue created.
```

## Status lifecycle

| Status | Meaning | Who/when changes it |
| --- | --- | --- |
| `pending` | Scoped but no active work. | Default on creation. |
| `in_progress` | One owner is actively implementing. | Set immediately before meaningful work begins. |
| `blocked` | Progress cannot continue due to a concrete dependency or required decision. | State the blocker and next required input in the progress log. |
| `in_review` | Implementation is complete and validation evidence is ready for review. | Do not use when tests are still pending. |
| `changes_requested` | Review found required changes. | Add exact requested changes and return to `in_progress`. |
| `done` | Acceptance criteria met, validation passed, and review accepted. | Add final evidence and completion date. |
| `cancelled` | Intentionally stopped; no further work expected. | Record why and any replacement issue. |

Only one issue owner may actively modify an `in_progress` issue at a time.
For role responsibilities, approval independence, and multi-agent handoffs,
follow [roles-and-governance.md](../playbooks/roles-and-governance.md).
For independent review artifacts and CI ownership, follow
[reviews-and-ci-governance.md](../playbooks/reviews-and-ci-governance.md).

## Working an issue

1. Create or read the issue file before implementation.
2. Set `Status: in_progress`, assign the owner, update `Updated`, and append a
   progress-log row before changing code or data.
3. Keep the work plan as small, ordered checkboxes. Check an item only with
   evidence in the progress log.
4. Add changed files, commands/tests run, output locations, and known
   limitations to the log. Never paste private conversation content or IDs into
   an issue unless the issue is itself an authorized no-text flag record.
5. When implementation is ready, set `in_review` and complete the Review / PR
   record.
6. A reviewer records `approved` or `changes_requested`. Set `done` only after
   approval and all acceptance criteria are checked.
7. Before moving a done issue to `issues/archive/done/`, add a concise entry to
   its `## Changelog` and to `issues/CHANGELOG.md`.

## File-based PR record

This repository may not have a hosted PR service. The `Review / PR record`
section is the local equivalent and must state:

- implementation summary and changed files;
- validation commands and outcome;
- data/privacy impact;
- reviewer and decision;
- follow-up issue IDs, if any.

Do not mark an issue `done` merely because code was written. It requires
verifiable acceptance criteria and review evidence.

## Changelog rules

Every issue must have a `## Changelog` section. Add entries when a meaningful
implementation, interface, data contract, safety rule, or documentation change
is completed. Entries must be concise and include the date, for example:

```markdown
- 2026-08-13: Added a local-only browser flag form with human confirmation.
```

When an issue moves to `done`, add a de-identified summary to
`issues/CHANGELOG.md` under `Unreleased`, including the stable issue ID. Do not
copy raw user content, credentials, PII, or safety-case details into either
changelog.

## Dependencies and handoff

- Put dependencies in `## Scope` or a `## Dependencies` section, linking the
  relevant `issues/<directory>/<issue>_<id>.md` file.
- If blocked, leave status as `blocked`; do not silently start unrelated scope.
- A new agent must read the issue, progress log, and linked manifests before
  resuming work.
- Use a new issue for a material scope expansion; do not rewrite history to
  make an old issue mean something different.

## Privacy and safety

- Do not include raw user messages, screenshots, credentials, or PII.
- Reference datasets by path, schema, aggregate count, or de-identified alias.
- Safety flags remain under `data/processed/flagged-cases/` and follow the
  human-review workflow in `AGENT.md`; do not manage them as ordinary todos.
