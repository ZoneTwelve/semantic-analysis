# Data Contract

## Raw

- `traces.jsonl`: one exported trace object per line; unchanged from source.
- `chat_id_turn_counts.txt`: supplied chat-ID/turn-count reference report.

## Interim conversations

`conversations.jsonl` contains one object per `chatId`:

```json
{
  "schemaVersion": "1.0",
  "chatId": "…",
  "firstTimestamp": "…",
  "lastTimestamp": "…",
  "traceCount": 2,
  "turns": ["original trace objects, ascending by timestamp"]
}
```

Trace records without `metadata.chatId` belong in `unlinked-traces.jsonl`.
Never infer a replacement ID unless a documented linking rule is introduced.

## Emotion-analysis input

`eligible-user-messages.jsonl` contains only user-role text eligible for a
classifier. Runtime wrappers, scheduled-task context, empty content, and likely
prompt-injection or long instruction payloads are held in
`excluded-user-messages.jsonl`, with `exclusionReason` for audit.

## Analysis outputs

Use one JSONL result per evaluation unit (message or conversation). Include
`chatId`, source trace/message location, model revision, device, top labels and
scores, plus a `manifest.json` containing the run configuration and counts.

### Qwen3.5 conversation emotions

`data/processed/emotion-evaluation-qwen35/conversation-emotions.jsonl` has one
result per `chatId`. The evaluator retains chronological user-role text after
the documented filtering rules, then emits `emotion` from the fixed taxonomy
`joy`, `sadness`, `anger`, `fear`, `surprise`, `disgust`, `neutral`, or `mixed`,
plus model-reported `confidence` when generated (otherwise it is `null`).
`manifest.json` records the MLX-VLM runtime,
model ID, request concurrency, input cap, elapsed time, and counts.

## Authorized human safety flags

`data/processed/flagged-cases/flagged-cases.jsonl` is an append-only, text-free
creation ledger. Each record has a unique `caseId`, `chatId`, creation metadata,
an initial `status` of `open`, an allowlisted assessment source, a 1–500
character operational note, `humanConfirmed: true`, and no raw conversation
text or PII.

`flag-case-events.jsonl` is a separate append-only event ledger. A lifecycle
event has `eventType: "flag_status_changed"`, the prior status, one terminal
status (`withdrawn` or `not_tracking`), allowlisted assessment source, text-free
operational note, `humanConfirmed: true`, timestamp, and privacy statement.
Original creation records and events are never modified or deleted.

The current status is derived deterministically: start with each creation
record's `open` status, then apply valid lifecycle events in file order. When
no lifecycle event exists, legacy records remain `open`. Only an `open` case can
receive one terminal event. `withdrawn` and `not_tracking` are not active flags
and must be excluded from open-review filters; `not_tracking` also excludes the
case from ongoing review queues while retaining its audit record.

`manifest.json` is a derived summary only, with current-status, category,
priority, case, and lifecycle-event counts. It may be regenerated; it is not an
audit source. All files stay local and restricted to authorized reviewers.
