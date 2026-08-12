# Application Development Playbook

An application is a runnable, user-facing local or deployed product surface.
Transformation CLIs, one-off scripts, and report generators are not apps unless
an issue explicitly promotes them to that role.

## Start a new app

1. Create or accept a feature-request issue using
   `issues/templates/feature-request.md`.
2. Assign Product/System Steward, Engineering DRI, QA reviewer, and where
   applicable Data/ML and Safety/Privacy reviewers.
3. Define users, local/network boundary, data classes, permissions, runtime,
   success criteria, and rollback before implementation.
4. Create an app catalog entry under `apps/<app-name>/README.md` before or with
   the first implementation PR. Link the owning issue and current source path.
5. Implement in an issue-specific worktree/branch and deliver through a PR.

## Minimum app contract

Every app entry must document:

- purpose, owner, issue ID, and lifecycle state;
- source path, launch command, test command, and supported platform;
- local/remote network binding and authentication boundary;
- data inputs/outputs and whether content is persisted;
- privacy/safety limitations, operational logs, and rollback/removal steps.

## Privacy and safety defaults

- Bind local tools to `127.0.0.1` by default.
- Do not send private conversation content to a hosted service without explicit
  user approval and a data-governance review.
- Keep generated outputs, browser indexes, model checkpoints, and credentials
  out of Git.
- New actions involving flags, safety decisions, or user content require
  explicit human confirmation and an approved audit path.

## App release checklist

- [ ] Feature issue and acceptance criteria approved.
- [ ] App catalog entry and user/developer documentation updated.
- [ ] Synthetic tests cover core and failure paths.
- [ ] Data/privacy review completed where applicable.
- [ ] PR reviewed, rollback documented, and changelog updated.
