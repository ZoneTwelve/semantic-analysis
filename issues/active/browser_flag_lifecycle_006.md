# ISSUE: Browser Flag Lifecycle and Non-Tracking Decisions

Status: `in_review`
Owner: Codex
Created: 2026-08-13
Updated: 2026-08-13
Related files: `src/flag_chat_case.py`, `src/add_flag_case_note.py`, `src/conversation_browser.py`, `docs/data-contract.md`, `tests/conversation-browser.spec.mjs`, `README.md`, `AGENT.md`, `CLAUDE.md`

## Roles

- Execution DRI: Codex
- Product / System Steward: Codex
- Engineering DRI: Codex
- System Architect: not required
- Data / ML reviewer: not required
- Safety / Privacy reviewer: required
- QA / Review approver: required
- Contributors: none

## Goal

Let an authorized human reviewer withdraw an open flag created in error or
mark it as not tracking after a manual decision, without deleting the original
flag or its audit history.

## Scope

- Append-only lifecycle events: `withdrawn` and `not_tracking`.
- Text-free, allowlisted, explicitly human-confirmed lifecycle actions in the
  local Conversation Browser and corresponding Python CLI.
- A derived current-status resolver for browser display/filtering and review
  queue exclusion; original flag records remain unchanged.
- Backwards-compatible handling of existing `flagged-cases.jsonl` records.
- Synthetic Playwright and Python tests; documentation and contract updates.

## Non-goals

- No deletion or rewriting of existing flag records/events.
- No automatic withdrawal, not-tracking decision, safety escalation, diagnosis,
  outreach, or use of model signals to change a flag.
- No public browser binding, external API, raw conversation text, PII, or
  arbitrary command execution.

## Acceptance criteria

- [x] An authorized reviewer can choose Withdraw flag or Mark not tracking only
  for an open flag, with an explicit confirmation and text-free operational note.
- [x] Lifecycle changes append immutable records and preserve the original flag.
- [x] Current status resolves deterministically from original flag plus events;
  `withdrawn` and `not_tracking` are excluded from open-review filtering.
- [x] API validation rejects missing human confirmation, invalid source/note,
  unknown or non-open flags, and duplicate terminal actions.
- [x] Existing flag files remain readable without a destructive migration; the
  rollback path is to stop consuming lifecycle events.
- [x] Data contract, README, AGENT, and CLAUDE describe the text-free,
  local-only lifecycle and reviewer constraints.
- [x] Synthetic tests pass without reading real `data/`.

## Work plan

- [x] 1. Define append-only lifecycle event contract and current-status resolver.
- [x] 2. Add CLI and local Browser API/UI actions with server-side confirmation.
- [x] 3. Integrate statuses into browser list/filtering and no-text review logic.
- [x] 4. Add synthetic tests, update documentation, and prepare review evidence.

## Migration and rollback

- Migration is additive: existing case records remain the source of creation
  metadata and an absent lifecycle event resolves to `open`.
- Rollback is non-destructive: remove/disable lifecycle controls and ignore
  lifecycle events; existing original flags and events remain auditable.

## Progress log

| Date | Status | Update | Evidence |
| --- | --- | --- | --- |
| 2026-08-13 | in_progress | Issue opened with append-only lifecycle scope, safety/privacy review requirement, and additive rollback plan. | `playbooks/upgrades.md`, `playbooks/data-governance.md` |
| 2026-08-13 | in_review | Added immutable terminal lifecycle events, status resolver, local CLI/API/UI controls, open-flag filter, and status-aware no-text report handling. | `src/flag_chat_case.py`, `src/change_flag_case_status.py`, `src/conversation_browser.py`, `src/report_negative_chat_review.py` |
| 2026-08-13 | in_review | Validated syntax and the local browser with synthetic data only, including confirmation, duplicate-terminal, unknown-case, withdrawal, and not-tracking paths. | `python -m py_compile src/flag_chat_case.py src/change_flag_case_status.py src/add_flag_case_note.py src/conversation_browser.py src/report_negative_chat_review.py`; `pnpm run test:browser` → 6 passed |

## Review / PR record

- Implementation: ready for independent review
- Validation: Python compilation passed; `pnpm run test:browser` passed 6/6 with the synthetic fixture only.
- Data/privacy impact: restricted text-free safety metadata only; no source conversation data is copied into lifecycle records.
- Reviewer: unassigned
- Decision: pending independent Safety / Privacy and QA approval
- Follow-up issue IDs: `issues/active/controlled_browser_flag_action_002.md`, `issues/active/browser_go_emotions_001.md`

## Changelog

- 2026-08-13: Opened additive, auditable flag lifecycle work for manual withdrawal and not-tracking decisions.
- 2026-08-13: Submitted for review; no accepted-work changelog entry written pending independent approval.
