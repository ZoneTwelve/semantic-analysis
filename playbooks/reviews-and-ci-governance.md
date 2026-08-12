# Independent Review and CI Governance Playbook

## Independent review artifacts

Reviewers must not concurrently edit an implementation issue file that is
owned by another active agent. Instead, create a separate review artifact:

```text
issues/reviews/<issue-id>_<reviewer-slug>.md
```

Start from `issues/templates/review.md`. The reviewer works in a detached,
read-only review worktree where possible:

```bash
git fetch origin
git worktree add --detach ../semantic-analysis-review-<issue-id> \
  origin/issue/<issue-id>-<slug>
```

The review artifact records only findings, evidence, validation, and decision;
it must not include raw user content, credentials, or sensitive data. The
reviewer may also submit the corresponding GitHub PR review. The Execution DRI
then appends the reviewer decision/PR link to the implementation issue and
changes its status.

## Review decision rules

| Decision | Meaning | Next action |
| --- | --- | --- |
| `approved` | Acceptance criteria and required safeguards pass. | DRI may merge if required approvals are satisfied. |
| `changes_requested` | One or more concrete required changes remain. | DRI returns issue to `in_progress`; reviewer artifact remains immutable evidence. |
| `blocked` | A safety, privacy, architecture, or dependency blocker prevents approval. | Keep issue blocked until named resolution is documented. |

An agent may not be the only reviewer of its own material implementation.

## System Architect role

| Responsibility | System Architect authority |
| --- | --- |
| Architecture boundaries | Approve or reject material architecture, runtime, dependency, and integration changes. |
| CI ownership | Sole role allowed to implement or approve CI-controlled-path changes. |
| CI standards | Define required checks, branch protection expectations, runner/security policy, and rollback requirements. |
| Architecture review | Produce or approve architecture/CI review artifacts for material delivery changes. |

System Architect authority is bounded by user instructions, data/safety rules,
and independent review. They cannot force-push protected branches, bypass GitHub
rulesets, or self-approve a material CI change without the required independent
review.

## CI-controlled paths and changes

Until a System Architect is explicitly assigned in an issue, all changes to the
following classes are **blocked**:

- `.github/workflows/**`
- `.github/actions/**`
- `.github/dependabot.yml`
- CI runner, secrets, permissions, branch-protection, or ruleset configuration
- build/test scripts or configuration invoked by CI

For a CI change, the issue must include:

1. `System Architect: <named agent/person>` in Roles;
2. risk, security, runtime-cost, and rollback analysis;
3. validation evidence, including success and failure behavior;
4. an independent architecture-CI review artifact;
5. a PR that receives required approvals before merge.

## GitHub enforcement prerequisites

Policy alone does not technically prevent a non-architect from editing CI.
After the user designates a GitHub user or team for System Architect ownership,
configure GitHub with:

1. a `.github/CODEOWNERS` rule for CI-controlled paths;
2. a branch ruleset requiring code-owner review for `main`;
3. required status checks and restricted force-push/branch deletion;
4. least-privilege GitHub Actions permissions and environment protection where
   deployments exist.

Do not invent a GitHub username/team in CODEOWNERS. Track this configuration in
a dedicated issue after the owner identity is supplied.

## Required role declarations

For new issues, include:

```text
System Architect: unassigned / not required / named agent or person
```

CI, architecture, or material integration work cannot move past `pending` while
this field is `unassigned`.
