# Collaboration Playbook

## Ownership and handoff

- Only one agent owns an `in_progress` issue at a time.
- Before starting, read the issue, progress log, linked manifests, and relevant
  playbooks.
- Update the issue before meaningful work and at each material checkpoint.
- A handoff must include current status, changed files, validations, blockers,
  and the exact next action.

## Parallel work

- Parallelize only independent, bounded tasks.
- Do not have multiple agents edit the same source file or issue file at once.
- Assign distinct issue IDs for independent workstreams.
- Integrate and validate combined changes before `in_review`.

## Review etiquette

- Review against acceptance criteria, not just whether code runs.
- Use evidence, commands, and paths; avoid unsupported conclusions.
- Request changes with specific, testable requirements.
- Preserve history: append progress/changelog entries rather than rewriting
  earlier evidence.
