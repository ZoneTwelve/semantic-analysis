# Agent Roles and Governance Playbook

Every agent must complete the onboarding checklist below and declare its role
before it changes code, data, documentation, workflows, or issues. Roles are
responsibilities, not security clearance: all privacy, safety, and user-approval
rules still apply.

## Agent onboarding checklist

1. Read `AGENT.md`, `CLAUDE.md`, `playbooks/README.md`, this playbook, and the
   playbooks routed for the task.
2. Read the assigned issue, its progress log, acceptance criteria, linked
   manifests, and related files.
3. Declare a primary role and confirm the execution DRI and reviewers in the
   issue before meaningful work begins.
4. Verify the scope, non-goals, privacy impact, validation plan, and handoff
   expectations.
5. Update the issue progress log at every material handoff or state change.

## Roles

| Role | Primary responsibility | May decide | Must not decide alone |
| --- | --- | --- | --- |
| **PM / System Steward** | Scope, requirements, workflow quality, playbooks, system standards, cross-team priorities. | Create/update playbooks; review issue scope and acceptance criteria; request standardization work. | Override user intent, safety/privacy rules, or approve their own material implementation without independent review. |
| **Engineer** | Implement code, APIs, CLIs, UI, tests, and migrations. | Technical design within approved issue scope; propose trade-offs. | Change product/safety policy, expose services publicly, or self-approve material code changes. |
| **System Architect** | Architecture boundaries, integrations, runtime/dependency direction, and CI ownership. | Approve or block material architecture/CI changes; define CI standards and rollback expectations. | Bypass user authorization, safety/privacy controls, protected-branch rules, or independent review for material CI changes. |
| **Data / ML Analyst** | Dataset contracts, preprocessing, evaluation, model outputs, analytical validity. | Local analysis design, metrics, and documented limitations. | Treat model outputs as facts, change raw data, or send data to external services without approval. |
| **Safety / Privacy Steward** | Sensitive-data handling, safety-review workflows, access boundaries, and escalation constraints. | Block unsafe flows; require human review and minimal-data handling. | Diagnose users, automate outreach, or lower safety controls without explicit user authorization. |
| **QA / Reviewer** | Validate acceptance criteria, regression risk, documentation, and test evidence. | Approve, reject, or request changes based on evidence. | Review their own material implementation as sole reviewer. |
| **Release / Maintenance Steward** | Dependency hygiene, compatibility, migration/rollback planning, repository health. | Propose release/migration plan and maintenance sequencing. | Delete material data, force-push, or deploy externally without explicit authorization. |
| **Research / UX Analyst** | User needs, usability, workflows, evidence synthesis, and non-sensitive reporting. | Propose experience improvements and research plan. | Claim user intent or issue confirmation without supporting evidence. |

One agent may hold more than one role only when the issue documents the
combination and an independent reviewer remains available for material changes.

## Authority model

### PM / System Steward authority

PM agents are authorized to propose and edit repository governance documents:
`playbooks/`, issue templates, workflow standards, and system-quality checklists.
They may review whether implementation follows those standards.

For material governance changes—new mandatory controls, changes to role
authority, data/safety rules, development stack, issue lifecycle, or release
policy—the PM must:

1. create or update an issue;
2. record rationale, scope, affected files, migration impact, and acceptance
   criteria;
3. add a dated issue changelog entry;
4. request independent QA/Reviewer or Safety/Privacy review where relevant;
5. update `issues/CHANGELOG.md` only after acceptance.

PM authority does not permit bypassing user instructions, external-action
approval, privacy/safety constraints, or independent review of their own
material work.

### Engineering authority

Engineers may implement within a scoped issue and update technical
documentation. Material changes to architecture, schemas, browser exposure,
models, or safety flows require PM/System Steward review and the corresponding
playbooks.

### Safety stop-the-line authority

Safety/Privacy Stewards and QA/Reviewers may set an issue to `blocked` when a
change risks data exposure, unsafe automation, unreviewed safety actions, or
loss of auditability. The issue must state the evidence and required resolution.

## Multi-agent issue protocol

Every new issue must declare:

```text
Execution DRI: one named agent
Product / System Steward: named agent or unassigned
Engineering DRI: named agent or unassigned
System Architect: named agent, `not required`, or `unassigned`
Data / ML reviewer: named agent or not required
Safety / Privacy reviewer: named agent or not required
QA / Review approver: named agent or unassigned
Contributors: zero or more agents
```

- Only the **Execution DRI** changes an `in_progress` issue file and its
  implementation branch/worktree at a time.
- Multiple PM or Engineer agents may contribute, but they must be listed as
  contributors with bounded responsibilities in the progress log.
- Split independent changes into separate issues rather than sharing a source
  file without coordination.
- The final reviewer must be independent of the material implementation.
- All role changes, handoffs, and review decisions are appended to the issue
  progress log; do not rewrite prior evidence.

## Required documentation for change classes

| Change | Required documentation |
| --- | --- |
| Code/UI/API | Issue, acceptance criteria, validation, changelog, reviewer decision. |
| Data/model pipeline | Above plus data contract, manifest/lineage, limitations, Data/ML review. |
| Safety/privacy workflow | Above plus Safety/Privacy review and human-escalation constraints. |
| Governance/playbook/stack | Issue, rationale, migration impact, playbook updates, PM + independent review. |
| Dependency/runtime upgrade | Issue, compatibility/rollback plan, validation, maintenance changelog. |
| CI/architecture change | Above plus named System Architect, architecture-CI review artifact, CI rollback plan, and required PR approval. |

## Handoff format

When handing an issue to another agent, append:

```markdown
| YYYY-MM-DD | in_progress | Handoff from <agent> to <agent>: completed <work>; next action <action>; blocker <none or detail>. | <paths/tests> |
```

The receiving agent must read the issue, relevant playbooks, and recorded
evidence before resuming.
