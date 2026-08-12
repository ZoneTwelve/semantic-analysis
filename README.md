# Semantic Analysis Dataset

This project keeps immutable source data separate from reproducible intermediate
and analysis-ready outputs.

## Layout

| Path | Purpose |
| --- | --- |
| `data/raw/` | Original inputs. Do not edit in place. |
| `data/interim/conversations/` | Traces grouped and sorted by `metadata.chatId`. |
| `data/processed/emotion-evaluation/` | User-message candidates after safety filtering, ready for message-level inference. |
| `data/processed/emotion-evaluation-qwen35/` | Conversation-level Qwen3.5 MLX results and run manifest. |
| `src/` | Re-runnable transformation and evaluation scripts. |
| `apps/` | Catalog of locally runnable applications and their ownership boundaries. |
| `docs/` | Dataset contracts and workflow notes. |

## Current pipeline

1. `data/raw/traces.jsonl` contains one trace record per line.
2. `src/preprocess-conversations.mjs` groups linked traces by `metadata.chatId`
   and orders each chat by timestamp.
3. `data/interim/conversations/conversations.jsonl` contains one conversation
   per line. Unlinked records are retained separately rather than assigned a
   fabricated conversation ID.
4. The legacy emotion filtering stage writes eligible and excluded user messages
   to `data/processed/emotion-evaluation/`; every excluded message retains an
   exclusion reason for review.
5. `src/evaluate_user_emotions.py` evaluates one conversation at a time with
   `mlx-community/Qwen3.5-2B-4bit`, using MLX-VLM continuous batching. Results
   are written to `data/processed/emotion-evaluation-qwen35/` and are resumable.

See [docs/data-contract.md](docs/data-contract.md) before adding derived data.
See [apps/README.md](apps/README.md) for the application inventory; the repo
currently has one local application, the Conversation Browser.
For multi-step development work, follow the local
[issue workflow](issues/README.md). Active work lives in `issues/active/`; only
accepted work is moved to `issues/archive/done/` and summarized in the
[issue changelog](issues/CHANGELOG.md).
For day-to-day development, maintenance, upgrades, and collaboration, read the
relevant [project playbook](playbooks/README.md) before making changes.

## Pipeline commands

Run commands from the repository root. Use `python` (not `python3`) for Python
commands and `pnpm` (not `npm` or `npx`) for JavaScript dependencies/scripts.
Every script reads the source data and
creates new derived outputs; never edit `data/raw/` directly.

### 1. Group traces into conversations

```bash
node src/preprocess-conversations.mjs \
  data/raw/traces.jsonl \
  data/interim/conversations
```

The output directory must be empty. The script groups only on
`metadata.chatId`, orders turns chronologically, and preserves unlinked traces
in a separate file.

### 2. Create an English-likely subset

```bash
python src/filter_english_conversations.py \
  --input data/processed/emotion-evaluation/eligible-user-messages.jsonl \
  --output-dir data/processed/english-conversations
```

This is a conservative heuristic, not language identification. It retains a
chat only when all eligible user messages appear English, and writes rejected
chats with reasons for audit.

### 3. Run GoEmotions on Apple Silicon

The model requires a complete local `SamLowe/roberta-base-go_emotions` model
directory and an MPS-enabled PyTorch runtime. Run outside a filesystem sandbox
when necessary, because the sandbox may not expose Apple MPS.

```bash
python src/run_go_emotions.py \
  --input data/processed/english-conversations/english-conversations.jsonl \
  --model /path/to/roberta-base-go_emotions \
  --output-dir data/processed/go-emotions-english \
  --batch-size 32
```

The run writes message-level top-3 predictions and a per-chat summary. Use a
new output directory for every model run. For a bounded smoke test, add
`--limit-chats 100`.

## Model-output interpretation

GoEmotions outputs probabilistic labels, not facts about a person. Do not use
them for diagnosis or individual profiling. Aggregate results before reporting
insights, retain filtering/manifest files, and mark unreported product issues
as hypotheses supported by observable evidence.

## Negative-signal review and safety flags

Use `src/classify_image_generation_chats.py` to label image-generation-like
chats before interpreting emotion results. It records explainable rule signals
without copying user text. Then use `src/build_negative_review_queue.py` to
produce three text-free queues: all negative signals, image-generation
exclusions, and the remaining review queue.

```bash
python src/classify_image_generation_chats.py
python src/build_negative_review_queue.py
```

`data/processed/flagged-cases/` is for authorized human safety review only.
Never auto-escalate or diagnose from a classifier label. A potential self-harm
signal requires immediate human review of the original conversation in the
approved system, following the organization's safety escalation protocol.

Add a manually assessed chat without storing its raw text:

```bash
python src/flag_chat_case.py \
  --chat-id '<chat-id>' \
  --category potential_self_harm \
  --priority urgent \
  --assessment-source authorized_human_review \
  --review-note 'Credible safety concern; immediate human review required.'
```

Use `--dry-run` first to validate a proposed record. The tool verifies that the
chat exists, refuses a duplicate open case, appends a text-free JSONL record,
and refreshes the flagged-case manifest.

To add an authorized review update to an existing open case without duplicating
the case or storing raw user text:

```bash
python src/add_flag_case_note.py \
  --chat-id '<chat-id>' \
  --source authorized_human_review \
  --note 'Explicit self-harm intent and method with farewell/aftercare signals; immediate human review required.'
```

## Data handling

The raw trace data may contain user content and identifiers. Keep `data/`
private, avoid committing it, and store future model outputs under
`data/processed/<analysis-name>/` with a manifest that records inputs, model,
parameters, and counts.

## Qwen3.5 MLX evaluation

Requirements: an Apple Silicon Mac with Metal available and Python 3.12+. The
model is local-only; no conversation data is sent to an external inference API.

Install the runtime once:

```bash
python -m pip install -r requirements-mlx-vlm.txt
```

The first model load downloads approximately 1.7 GB unless it is already in
the Hugging Face cache. Run a 10-conversation smoke test before a larger job:

```bash
python src/evaluate_user_emotions.py --limit 10 --overwrite
```

Run a 100-conversation throughput benchmark:

```bash
python src/evaluate_user_emotions.py --limit 100 --overwrite
```

Run the remaining conversations; the output JSONL is resumed automatically:

```bash
python src/evaluate_user_emotions.py
```

The default retains the most recent 2,000 user-text characters per conversation
to keep MLX continuous batches balanced. Increase `--max-conversation-chars`
when full historical context matters more than throughput.

The evaluator starts a local `mlx_vlm.server`, submits concurrent requests to
its continuous batcher, and shuts the server down when the run completes. To
reuse an already-running server, start it separately and pass its URL:

```bash
python -m mlx_vlm.server --model mlx-community/Qwen3.5-2B-4bit --port 8080
python src/evaluate_user_emotions.py --no-launch-server --server-url http://127.0.0.1:8080
```

Each JSONL row has one `chatId`, an `emotion`, and a model-reported
`confidence` when available (`null` otherwise). `manifest.json` records model,
runtime, concurrency, input cap, elapsed time, and filtering/classification
counts. Existing result rows are resumed automatically; use `--overwrite` only
when intentionally replacing the derived result set.

### Observed local benchmark

On this machine, the 10-conversation smoke test completed in 16.4 seconds,
including model startup. The model produced 10 parseable labels; two responses
omitted confidence and were saved with `confidence: null`. Throughput on longer
or more heterogeneous conversations varies with retained prompt length, so run
the 100-conversation benchmark before estimating a full-dataset runtime.

## Conversation Browser

Use the local browser to search chat IDs and read each conversation turn-by-turn.
Browsing is read-only; the only write path is the explicit human-review flag
form described below. On its first run it scans the interim JSONL and creates a compact
SQLite index containing metadata and byte offsets only; it does not duplicate
conversation bodies.

```bash
python src/conversation_browser.py
```

Open <http://127.0.0.1:8765> in a browser. The `:8765` port is required: plain
`http://127.0.0.1` points to port 80, where this tool does not run. The browser
starts on the newest conversations, shows recent user-text previews, supports
previous/next pages, and can search previews or chat IDs. Subsequent launches reuse the index.
If the interim source changes, the browser rebuilds it automatically. To build
the index without opening the server:

```bash
python src/conversation_browser.py --build-index-only
```

### Safety review and flag workflow

Open a chat only in an authorized environment and inspect the original content
before an authorized human makes a safety decision. Do not copy browser content
into reports, flag records, command arguments, or logs.

After authorized review, use the selected chat's **Create human review flag**
form. It requires a category, priority, assessment source, text-free
operational note, and an explicit confirmation checkbox. The local browser uses
the same validation and output schema as `src/flag_chat_case.py`; it rejects
invalid choices, unknown chats, and duplicate open cases. It never auto-flags
from model labels or conversation text. Use `src/add_flag_case_note.py` to add
a text-free update to an existing open case.

### Browser tests

The Playwright tests use a small synthetic fixture, never your private dataset.
Install the test dependency and browser once, then run:

```bash
pnpm install --frozen-lockfile
pnpm exec playwright install chromium
pnpm run test:browser
```
