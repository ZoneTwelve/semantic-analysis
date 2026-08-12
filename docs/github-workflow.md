# GitHub CI, Issues, and Pull Requests

This repository uses two linked records for durable work:

1. A GitHub issue is the collaboration and discussion record.
2. A local issue file in `issues/active/` is the auditable delivery record for
   roles, progress, privacy impact, validation, review, and changelog evidence.

Do not include private conversation content, IDs, credentials, screenshots, or
safety-case details in either record.

## Create and link work

1. Open a GitHub issue with the supplied Bug report or Feature request form.
2. For a feature, create a matching local issue from
   `issues/templates/feature-request.md`; for other durable work, use
   `issues/templates/issue.md`.
3. Add each reference to the other record: put the GitHub issue URL/number in
   the local issue and the local issue path in the GitHub issue.
4. Use an issue-specific branch and pull request as required by
   `playbooks/worktrees-and-prs.md`.
5. In the PR body, write `Closes #123` (or another supported closing keyword)
   and the local issue path. GitHub links the PR to the issue and closes the
   issue when the PR is merged into the default branch.

GitHub documents the supported [closing keywords](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/using-keywords-in-issues-and-pull-requests).

## Continuous integration

`.github/workflows/ci.yml` runs on pushes to `main`, pull requests targeting
`main`, and manual dispatch. It has two required-candidate checks:

- **Python syntax** compiles `src/` without reading private data.
- **Browser tests** installs pinned JavaScript dependencies and Chromium, then
  runs `pnpm run test:browser` against the synthetic fixture only.

The workflow has read-only repository permissions and must not run a model,
inspect `data/`, upload artifacts containing data, or use secrets.

## Repository-admin setup

After this workflow runs successfully on `main`, a repository admin should
configure a `main` branch-protection rule in GitHub Settings:

1. Require a pull request before merging and require at least one independent
   approving review.
2. Require the **Python syntax** and **Browser tests** status checks to pass.
3. Require branches to be up to date before merging if the team wants merge
   commits tested against the latest `main`.
4. Restrict direct pushes to `main` according to the team's release authority.

Branch protection is an administrator-controlled GitHub setting; this
repository configuration does not change it automatically. See GitHub's
[branch-protection documentation](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/managing-a-branch-protection-rule) and [required-check guidance](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks).

## Review and completion

The PR template requires both links, validation evidence, privacy/safety
impact, rollback notes, and independent-review confirmation. When a PR is
merged, complete the linked local issue according to `issues/README.md`; do
not mark it done without the recorded reviewer decision.
