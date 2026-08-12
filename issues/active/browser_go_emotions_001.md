# ISSUE: Conversation Browser + GoEmotions Review Integration

Status: `pending`
Owner: unassigned
Created: 2026-08-13
Updated: 2026-08-13
Related files: `src/conversation_browser.py`, `src/run_go_emotions.py`
Scope: local-only Conversation Browser; no hosted inference or data upload.

## Goal

Let an authorized reviewer see **existing, precomputed** GoEmotions results for
a chat in `src/conversation_browser.py`, alongside the conversation review
view. This is a review aid only: it must not infer new results in the browser,
auto-flag a chat, or expose private content beyond the local authorized session.

## Scope

- Optional local index/API/UI support in Conversation Browser for precomputed
  GoEmotions results.
- Human-confirmed integration with the existing text-free flag tools.

## Non-goals

- Do not run model inference from the browser request handler.
- Do not send conversation text or emotion results to external services.
- Do not use emotion labels as a diagnosis, risk score, or automatic flagging
  decision.
- Do not add a public network binding, tunnel, or unauthenticated remote API.

## Completion order

Complete the items in order. Check an item only after its acceptance criteria
and tests pass.

- [ ] 1. Define an emotion-result contract.

  - Input: `data/processed/go-emotions-english/message-emotions.jsonl` and
    `conversation-emotion-summary.jsonl`.
  - Define a stable browser-facing record with `chatId`, classification scope,
    model ID, model-run timestamp, top labels/scores, and source-result path.
  - Explicitly distinguish `not_classified` from `no_emotion_signal`.
  - Acceptance: add the contract to `docs/data-contract.md`; no raw message
    text is introduced to the browser index.

- [ ] 2. Add an optional, precomputed emotion index.

  - Add `--emotion-summary` and `--emotion-message-results` CLI options to
    `src/conversation_browser.py`; defaults must be disabled/no results.
  - Build a local SQLite table keyed by `chat_id`, containing only aggregate
    results and provenance, not user text.
  - Track input file signatures in the browser metadata and rebuild this table
    when supplied emotion files change.
  - Acceptance: a chat with no result displays `Not classified`; re-indexing is
    deterministic and does not duplicate rows.

- [ ] 3. Expose a narrow local API.

  - Extend `GET /api/conversations/<chatId>` with an `emotionReview` object,
    or add `GET /api/conversations/<chatId>/emotion-review`.
  - Return only precomputed labels, scores, model/provenance, and a limitation
    notice. Do not return model inputs or any additional message text.
  - Acceptance: unknown chat IDs return 404; chats without results return an
    explicit non-error unclassified state.

- [ ] 4. Add a clearly scoped Browser UI panel.

  - Show model name, run timestamp, classification scope, chat-level dominant
    label, message count, and top-3 scores when present.
  - Display: “Probabilistic model signal; not a diagnosis or safety decision.”
  - Visually separate emotion review metadata from source conversation content.
  - Acceptance: no UI control claims that a model label confirms user emotion
    or a safety issue.

- [ ] 5. Add negative-signal and image-generation context.

  - Optionally read the no-text negative review queue and image-generation
    exclusion queue by `chatId`.
  - If image-generation-like, show a suppression warning: creative/fictitious
    content can cause false affect signals.
  - If a manual flag exists, show its status/priority only; do not show raw
    flag-event notes unless the reviewer is explicitly authorized.
  - Acceptance: a flagged chat remains human-review-only; no model score can
    create, upgrade, downgrade, or close a flag.

- [ ] 6. Design the controlled browser-to-flag action.

  - Add a local-only, disabled-by-default action behind explicit human
    confirmation.
  - Allow only `src/flag_chat_case.py` and `src/add_flag_case_note.py` with
    fixed allowlisted fields: category, priority, assessment source, and a
    short text-free operational note.
  - Reject raw conversation text, URLs, arbitrary CLI arguments, duplicate
    open cases, and any automatic suggestion that creates a flag.
  - Acceptance: manual flag creation/update has an audit event and cannot
    execute arbitrary commands.

- [ ] 7. Add synthetic-data tests.

  - Extend the browser fixture with: classified chat, unclassified chat,
    image-generation exclusion, and existing urgent manual flag.
  - Test API, UI rendering, stale-index rebuild, missing result files, and
    flag-action validation using synthetic data only.
  - Acceptance: `pnpm run test:browser` passes without reading real `data/`.

- [ ] 8. Document and release safely.

  - Update `README.md`, `AGENT.md`, `CLAUDE.md`, and `docs/data-contract.md`.
  - Include local-only access, result limitations, reviewer authorization,
    privacy constraints, and rollback/removal steps for the emotion index.
  - Acceptance: documentation has an end-to-end command example and never
    instructs agents to expose the browser publicly or auto-flag a user.

## Definition of done

The browser can display precomputed GoEmotions review metadata for an
authorized local reviewer, reliably distinguishes absent results, preserves
privacy, passes synthetic tests, and requires an explicit human decision before
any flag tool runs.

## Progress log

| Date | Status | Update | Evidence |
| --- | --- | --- | --- |
| 2026-08-13 | pending | Issue normalized to the repository issue workflow. | `issues/README.md` |

## Review / PR record

- Implementation: not started
- Validation: not run
- Reviewer: unassigned
- Decision: pending

## Changelog

- 2026-08-13: Created the browser GoEmotions integration issue and defined its
  local-only, precomputed-results scope.
