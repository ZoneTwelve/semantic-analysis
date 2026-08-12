# Upgrade Playbook

Use this for material changes: schemas, models, data pipelines, browser APIs,
package-manager/runtime changes, or issue workflow changes.

## Plan first

- Open an issue with migration scope, non-goals, rollback, validation, and
  affected paths.
- Identify backwards compatibility and whether old outputs must remain readable.
- State any privacy/safety effect before implementation.

## Execute safely

- Prefer additive, versioned outputs over destructive replacements.
- Add or update a schema version and manifest when an output contract changes.
- Migrate samples first; compare row counts, identifiers, and expected fields.
- Keep a rollback path until review approval.

## Finish

- Update docs, tests, and playbooks affected by the upgrade.
- Record the migration, validation evidence, and rollback decision in the issue
  changelog and `issues/CHANGELOG.md` when accepted.
