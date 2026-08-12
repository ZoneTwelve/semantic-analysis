# ISSUE: Application Catalog and `apps/` Layout

Status: `in_review`
Owner: Codex
Created: 2026-08-13
Updated: 2026-08-13
Related files: `README.md`, `apps/README.md`, `apps/conversation-browser/README.md`

## Roles

- Execution DRI: Codex
- Product / System Steward: Codex
- Engineering DRI: not required
- Data / ML reviewer: not required
- Safety / Privacy reviewer: not required
- QA / Review approver: unassigned
- Contributors: none

## Goal

Make the repository's application boundary explicit and establish `apps/` as
the catalog location, while preserving current runnable paths until a reviewed
migration is approved.

## Scope

- Inventory current application(s) and distinguish them from pipeline CLIs.
- Add a top-level `apps/` catalog and a per-app ownership/readme entry.
- Update the repository overview to link the catalog.

## Non-goals

- No movement or rewrite of the reviewed Conversation Browser implementation.
- No behavior, runtime, data-schema, dependency, or network-binding change.
- No claim that pipeline scripts are independently deployed applications.

## Acceptance criteria

- [x] Documentation states the current application count and names it.
- [x] `apps/` contains a discoverable catalog and one entry for the Conversation Browser.
- [x] The entry records current source, test, launch command, data boundary, and local-only access constraint.
- [x] Existing source paths remain valid and no private data is accessed or changed.

## Work plan

- [x] 1. Inventory current runnable components and classify application versus CLI.
- [x] 2. Add the `apps/` catalog and update root documentation.
- [x] 3. Check internal links and request independent documentation review.

## Progress log

| Date | Status | Update | Evidence |
| --- | --- | --- | --- |
| 2026-08-13 | in_progress | PM/System Steward inventory found one local application: Conversation Browser. Transformation, model, reporting, and flagging files remain CLIs. | `README.md`, `src/`, `package.json` |
| 2026-08-13 | in_progress | Added the top-level catalog, per-app entry, and root-document link while retaining the current browser source path because its safety workflow is in review. | `apps/README.md`, `apps/conversation-browser/README.md`, `README.md` |
| 2026-08-13 | in_review | Documentation links and diff whitespace validation passed; no private data was read or changed. Independent documentation review requested. | `rg -n "apps/|one application|Conversation Browser" README.md apps issues/active`; `git diff --check` |

## Review / PR record

- Implementation: application catalog and root documentation complete; source relocation intentionally deferred until the current browser safety-workflow review finishes.
- Validation: catalog references found by `rg`; `git diff --check` passed.
- Data/privacy impact: documentation-only; no data access or application behavior change.
- Reviewer: unassigned
- Decision: pending
- Follow-up issue IDs: `004`

## Changelog

- 2026-08-13: Added an `apps/` catalog documenting the one local application and its current source/test/access boundaries; awaiting independent review.
