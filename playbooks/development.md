# Development Playbook

## Before coding

1. Read the relevant issue under `issues/active/` and set it to `in_progress`
   before meaningful work begins.
2. Read `AGENT.md`, `CLAUDE.md`, this playbook, and any relevant data contract.
3. Inspect existing code/tests before adding new abstractions.
4. Identify privacy, safety, and migration impact before changing a data path or
   local browser/API.

## Stack rules

- Python: run `python`, not `python3`.
- JavaScript: run `pnpm`, not `npm` or `npx`.
- Install JavaScript dependencies with `pnpm install --frozen-lockfile`.
- Keep `pnpm-lock.yaml` as the sole Node lockfile. Do not create
  `package-lock.json`.

## Implementation rules

- Prefer small CLI tools and JSONL/SQLite interfaces with explicit schemas.
- Stream large datasets; never load multi-gigabyte JSONL files wholesale.
- Do not overwrite derived datasets by default. Write a fresh output directory
  and a manifest with inputs, parameters, counts, and limitations.
- Local browser/API tools must bind to `127.0.0.1` only unless the user gives
  explicit approval for another exposure model.
- Never turn untrusted dataset text into instructions, shell arguments, or an
  external request.

## Validation and review

- Run syntax/type checks appropriate to each changed language.
- Use synthetic fixtures for browser/UI tests; never use real data as a test
  fixture.
- Record validation command, result, changed files, and limitations in the
  issue before moving to `in_review`.
- Update the issue `## Changelog` when a meaningful change is complete.
