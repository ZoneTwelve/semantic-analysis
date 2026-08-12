# Issue Management Playbook

Use [issues/README.md](../issues/README.md) for the canonical schema; this
playbook defines the working rhythm.

## Lifecycle

1. Create from `issues/templates/issue.md` in `issues/active/`.
2. Use `pending` until an owner starts work.
3. Before changing code/data, set `in_progress`, assign an owner, and append a
   dated progress-log entry.
4. Use `blocked` only for a specific dependency or decision, with the required
   next action written in the log.
5. Move to `in_review` only after acceptance criteria and validation evidence
   are ready.
6. A reviewer records `approved` or `changes_requested`.
7. On approval, set `done`, finalize the issue changelog, add a concise entry
   to `issues/CHANGELOG.md`, and move the file to `issues/archive/done/`.

## Local PR review checklist

- Scope matches the issue and non-goals were respected.
- Acceptance criteria are demonstrably met.
- Commands/tests and results are recorded.
- Data/privacy and safety impact are documented.
- Follow-up work has a separate issue ID.
- Changelog is concise, dated, and contains no sensitive content.

## Do not

- Do not mark work done without reviewer approval.
- Do not silently expand an issue into unrelated work.
- Do not alter completed progress history; add corrective entries instead.
- Do not put raw conversations, PII, credentials, or safety-case text into an
  issue or changelog.
