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
