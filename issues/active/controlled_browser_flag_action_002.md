# ISSUE: Controlled Conversation Browser Flag Action

Status: `in_review`
Owner: codex
Created: 2026-08-13
Updated: 2026-08-13
Related files: `src/conversation_browser.py`, `src/flag_chat_case.py`, `tests/conversation-browser.spec.mjs`, `README.md`, `AGENT.md`

## Goal

Provide an authorized local reviewer with a narrowly scoped, human-confirmed
way to create a text-free flag from a selected conversation in the local
Conversation Browser.

## Scope

- Local-only browser form for creating one new human-review flag.
- Fixed allowlists for category, priority, and assessment source.
- Required human confirmation and a 1–500 character operational note.
- Server-side validation, duplicate-open-case protection, and text-free audit
  records under `data/processed/flagged-cases/`.
- Synthetic Playwright coverage only; no real conversation data in tests.

## Non-goals

- No automatic flagging from message content, emotion labels, or model scores.
- No diagnosis, risk scoring, counselling, notification, or external outreach.
- No public binding, tunnel, arbitrary shell command, arbitrary paths, or
  arbitrary CLI arguments exposed through the browser.
- No displaying or storing raw conversation text in a flag record.

## Acceptance criteria

- [x] The form is local-only and is available only after a reviewer opens a
  specific conversation.
- [x] The form requires category, priority, assessment source, operational
  note, and explicit human-confirmation checkbox.
- [x] The server accepts only allowlisted values, validates the chat using the
  local index, and rejects unknown chats and duplicate open cases.
- [x] Created flag records contain no raw user-message text.
- [x] Synthetic Playwright tests verify explicit confirmation is required for
  the flag action and all browser tests pass.
- [x] README and AGENT documentation describe the local-only human-review
  workflow and privacy restrictions.

## Work plan

- [x] 1. Extract shared flag-case creation validation from the CLI tool.
- [x] 2. Add a fixed-field local browser API and confirmation form.
- [x] 3. Add synthetic browser test coverage for manual flag creation.
- [x] 4. Update workflow documentation and prepare review evidence.

## Progress log

| Date | Status | Update | Evidence |
| --- | --- | --- | --- |
| 2026-08-13 | in_progress | Extracted reusable case creation logic with allowlisted inputs, no-text validation, duplicate-open-case check, and existing JSONL audit schema. | `src/flag_chat_case.py` |
| 2026-08-13 | in_progress | Added local `/api/flags` endpoint and human-confirmed browser form; no automatic flagging path exists. | `src/conversation_browser.py` |
| 2026-08-13 | in_progress | Added synthetic browser flag test and isolated test output directory. | `tests/conversation-browser.spec.mjs`, `playwright.config.mjs` |
| 2026-08-13 | in_review | Validation passed. | `python3 -m py_compile src/conversation_browser.py src/flag_chat_case.py`; `npm run test:browser` → 4 passed |

## Review / PR record

- Implementation: fixed-field human-confirmed browser flag form and local API;
  shared validation in `src/flag_chat_case.py`.
- Validation: Python compilation passed; `npm run test:browser` passed 4/4 using
  `tests/fixtures/conversations.jsonl` only.
- Data/privacy impact: browser reads conversations locally; the only write path
  creates the existing text-free flagged-case record. No raw conversation text,
  screenshots, IDs, or PII are included in this issue.
- Reviewer: unassigned
- Decision: pending approval
- Follow-up issue IDs: `issues/active/browser_go_emotions_001.md` remains separate;
  precomputed GoEmotions browser integration is not implemented by this issue.

## Changelog

- 2026-08-13: Added a local-only, human-confirmed browser action for creating
  text-free flag records, with synthetic test coverage; awaiting review.
