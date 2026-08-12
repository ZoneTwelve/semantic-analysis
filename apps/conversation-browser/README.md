# Conversation Browser

## Status

The Conversation Browser is the repository's only application. It is a
local-only review tool, not a hosted web service.

## Canonical implementation

- Source: `src/conversation_browser.py`
- Synthetic browser test: `tests/conversation-browser.spec.mjs`
- Test command: `pnpm run test:browser`
- Launch command: `python src/conversation_browser.py`
- Local address: `http://127.0.0.1:8765`

## Data and safety boundary

The app reads private interim conversation data locally and binds only to
`127.0.0.1`. Its ordinary review path is read-only. The sole write path is an
explicit, human-confirmed creation of a minimal, text-free review flag; it must
never auto-flag, diagnose, or send conversation data to an external service.

Do not use synthetic fixtures as a reason to point tests at real data, and do
not expose this app through a public interface or tunnel without explicit user
approval.

## Planned work

The proposed local, per-turn translation feature is tracked in
[`issues/active/chat_translation_004.md`](../../issues/active/chat_translation_004.md).
It is not implemented, and it requires approved language-pair and local-runtime
decisions plus Data/ML, Safety/Privacy, and QA review.
