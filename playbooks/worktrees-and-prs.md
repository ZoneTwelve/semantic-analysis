# Worktrees and Pull Requests Playbook

Use this playbook for any implementation that changes code, configuration,
tests, applications, or governed documentation.

## Before creating a worktree

1. Read the issue and set its `Execution DRI`, roles, acceptance criteria, and
   validation plan.
2. Run `git status --short`, `git branch --show-current`, and
   `git worktree list` in the primary checkout.
3. Do not touch or stage files that another agent has modified, created, or
   claimed in an active issue.
4. If the primary checkout is dirty, create a dedicated worktree from the last
   committed base branch; do not stash, reset, or clean another agent's work.

## Naming

Use one branch and one worktree per implementation issue:

```text
Branch:    issue/<id>-<short-slug>
Worktree:  ../semantic-analysis-<id>-<short-slug>
PR title:  [<id>] Short imperative summary
```

Example:

```bash
git fetch origin main
git worktree add ../semantic-analysis-008-delivery-workflow \
  -b issue/008-delivery-workflow origin/main
```

The worktree path must be outside the primary repository directory when
possible. Never create a worktree inside `data/`, `apps/`, or another agent's
worktree. Do not copy private data, model artifacts, or `.env` files into it.

## Implementation and commits

- Work only in the assigned worktree/branch.
- Keep commits small and scoped to the issue. Each commit message should state
  the change, not an emotion or vague milestone.
- Use `python` and `pnpm` only.
- Before every commit: inspect `git diff --check`, `git status --short`, and
  staged file names. Ensure no `data/`, `reports/`, model, credential, or
  generated artifact is staged.
- Update the issue progress log and issue changelog with completed work and
  validation evidence before requesting review.

## Pull request lifecycle

1. Push the branch with `git push -u origin issue/<id>-<short-slug>`.
2. Create a PR using `gh pr create`:

   ```bash
   gh pr create --base main --head issue/<id>-<short-slug> \
     --title '[<id>] Short summary' \
     --body-file /path/to/pr-summary.md
   ```

3. The PR body must include issue path, goal, non-goals, changed files,
   validation results, data/privacy impact, rollback notes, and follow-ups.
4. Set the issue to `in_review`; record PR URL/number and reviewer assignment
   in its Review / PR record.
5. Merge only after required independent review approval. Do not self-merge a
   material change when an independent reviewer is required.
6. After merge, update the issue to `done`, add its de-identified entry to
   `issues/CHANGELOG.md`, move it to `issues/archive/done/`, then remove the
   worktree:

   ```bash
   git worktree remove ../semantic-analysis-<id>-<short-slug>
   git branch -d issue/<id>-<short-slug>
   ```

## Conflict and concurrent-work rules

- Never use `git reset --hard`, `git clean`, `git checkout --`, force-push, or
  rebase another agent's branch without explicit user authorization.
- If two issues need the same file, assign a single integration owner or split
  the change. Do not edit the file concurrently.
- Rebase/merge the latest `main` into an issue branch only after checking the
  affected files and recording the result in the issue.
- A blocked merge or conflict moves the issue to `blocked` until its owner and
  integration plan are clear.
