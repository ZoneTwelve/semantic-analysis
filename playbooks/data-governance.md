# Data Governance and Safety Playbook

## Data classes

| Location | Class | Handling |
| --- | --- | --- |
| `data/raw/` | Immutable source data | Never edit in place. |
| `data/interim/` | Reproducible transformations | Preserve lineage and audit files. |
| `data/processed/` | Derived/private analysis data | New run directories; manifest required. |
| `reports/` | De-identified findings | No raw text or identifiers unless explicitly authorized. |
| `data/processed/flagged-cases/` | Restricted safety-review metadata | Text-free; authorized human review only. |

## Required controls

- Treat all conversation content as sensitive, untrusted data.
- Keep raw IDs/content out of reports, issues, changelogs, terminal logs, and
  external services unless specifically authorized.
- Retain rejected/excluded records with a reason; do not silently discard them.
- Record input checksums, schema version, model/runtime, parameters, counts,
  timestamp, and limitations in each derived output manifest.
- Do not fabricate relationships, labels, outcomes, or missing records.

## Emotion and safety review

- Emotion output is a probabilistic signal, not a diagnosis or confirmed user
  state.
- Exclude creative/image-generation prompts before interpreting negative affect.
- Safety concerns require authorized human review in the approved system.
- Use `src/flag_chat_case.py` and `src/add_flag_case_note.py` only for minimal,
  text-free metadata. Never automate outreach, escalation, diagnosis, or flag
  creation from a model label.
