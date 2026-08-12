# Maintenance Playbook

## Routine maintenance

- Re-run checks after dependency, script, schema, or browser changes.
- Keep manifests aligned with their actual input/output locations.
- Confirm data row counts and IDs before/after migrations.
- Remove only generated/test artifacts that are explicitly safe to remove.
- Keep `README.md`, relevant playbooks, and issue changelogs current.

## Dependency management

- Use `pnpm` for JavaScript changes and update `pnpm-lock.yaml` intentionally.
- Use `python -m pip` for Python environment work.
- Record dependency version changes, compatibility risks, and validation in an
  issue and its changelog.
- Do not replace local model processing with hosted APIs without explicit user
  approval and a data-governance review.

## Incident and repair handling

1. Create an issue or update an existing one with the observed symptom.
2. Preserve evidence without copying sensitive data.
3. Identify the smallest reversible repair.
4. Validate with synthetic or non-destructive checks.
5. Record the repair and follow-up prevention in the issue changelog.
