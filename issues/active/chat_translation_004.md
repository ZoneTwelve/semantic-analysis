# ISSUE: Local Conversation Translation for Authorized Review

Status: `pending`
Owner: unassigned
Created: 2026-08-13
Updated: 2026-08-13
Related files: `apps/conversation-browser/README.md`, `src/conversation_browser.py`, `docs/data-contract.md`

## Roles

- Execution DRI: unassigned
- Product / System Steward: Codex
- Engineering DRI: unassigned
- Data / ML reviewer: required
- Safety / Privacy reviewer: required
- QA / Review approver: unassigned
- Contributors: none

## Goal

Allow an authorized local Conversation Browser reviewer to request a clearly
identified translation of an individual chat turn, without changing source
data, silently persisting user text, or sending private content to an external
service.

## Scope

- Define the supported source and target languages and the local-only
  translation-runtime option.
- Add an explicit, per-turn reviewer action in the Conversation Browser; it
  must be disabled by default until a supported local runtime is configured.
- Display translations separately from source text, with translation provenance
  and a limitation notice.
- Define whether a translation is ephemeral or may be stored as a new,
  auditable derived dataset. The default must be ephemeral.
- Add synthetic-fixture tests and documentation for setup, access restrictions,
  failure states, and rollback/removal.

## Non-goals

- No hosted translation API, browser extension, public service binding, or data
  upload.
- No automatic translation of a dataset or background batch processing.
- No modification of `data/raw/`, `data/interim/`, or existing processed
  outputs.
- No use of translated text for emotion classification, safety decisions, or
  automatic flagging.

## Acceptance criteria

- [ ] Product requirements name supported language pairs, runtime, reviewer
  authorization model, and the default non-persistence behavior.
- [ ] The implementation uses only a locally configured runtime and has no
  external network fallback.
- [ ] A reviewer must explicitly request each translation; the browser does not
  automatically translate source content.
- [ ] Source and translation are visibly distinct, and the UI states that
  translations can be inaccurate and are not safety decisions.
- [ ] Translation requests and errors do not log raw conversation text, IDs, or
  credentials.
- [ ] Synthetic tests cover authorization/confirmation, unavailable runtime,
  successful local translation, and absence of persistent output by default.
- [ ] Data/ML, Safety/Privacy, and independent QA reviewers approve the change.

## Work plan

- [ ] 1. Resolve the required language pairs and approve a local translation
  runtime, model provenance, and download/install process.
- [ ] 2. Define the ephemeral request/response and optional derived-output
  contracts in `docs/data-contract.md`.
- [ ] 3. Implement the local-only browser action and synthetic tests.
- [ ] 4. Validate privacy controls, document rollback, and obtain independent
  review.

## Dependencies

- `issues/active/controlled_browser_flag_action_002.md` must complete review
  before changing the browser's currently reviewed safety workflow.
- `issues/active/app_catalog_and_layout_005.md` establishes the application
  ownership and canonical path before implementation begins.

## Progress log

| Date | Status | Update | Evidence |
| --- | --- | --- | --- |
| 2026-08-13 | pending | Created at user request; implementation is intentionally unstarted pending local-runtime and language-pair decisions. | `playbooks/upgrades.md`, `playbooks/data-governance.md` |

## Review / PR record

- Implementation: not started
- Validation: not run
- Data/privacy impact: translation would process sensitive content locally; persistence is prohibited by default and any exception requires a new derived-data contract.
- Reviewer: unassigned
- Decision: pending
- Follow-up issue IDs: `005`

## Changelog

- 2026-08-13: Created local-only, explicit-translation work item with required privacy and independent-review gates.
