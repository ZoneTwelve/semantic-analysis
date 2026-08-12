# Feature Intake Playbook

Use this process whenever someone asks for a new capability, app, workflow, UI,
integration, or material behavior change.

## Intake sequence

1. Search `issues/active/`, `issues/archive/`, `apps/`, and relevant playbooks
   for existing work before creating a duplicate.
2. Create a feature-request issue from `issues/templates/feature-request.md`.
3. Capture the user problem and desired outcome—not a premature implementation
   solution alone.
4. Identify impact on data, privacy, safety, runtime, dependencies, operations,
   and existing apps.
5. Assign the required roles and reviewers. Keep status `pending` until scope
   and owner are ready.
6. Split discovery, implementation, and follow-up work into separate linked
   issues when they have different owners or acceptance criteria.

## Feature triage outcomes

| Outcome | Action |
| --- | --- |
| Ready | Define acceptance criteria, assign DRI, move to `in_progress`. |
| Needs discovery | Create a bounded research/design issue; keep implementation pending. |
| Duplicate | Link to the existing issue and close as `cancelled` with rationale. |
| Unsafe/out of scope | Document constraints; do not implement without required authorization. |
| Blocked | Record the exact decision/dependency needed and set `blocked`. |

## Product-quality requirements

- Define a measurable user outcome and non-goals.
- State what should not change, including privacy/safety boundaries.
- Include empty, error, unavailable-runtime, and rollback behavior.
- Do not declare a feature solved until user-facing acceptance criteria and
  independent review evidence exist.
