"""CLI for conversation-level emotion classification with MLX-VLM."""
from __future__ import annotations

import argparse
import asyncio
import json
import time
from collections import Counter
from pathlib import Path
from typing import Any

from .mlx_vlm import EMOTIONS, MLXVLMServer, classify_all
from .prepare import prepare_conversation


def existing_chat_ids(results_path: Path) -> set[str]:
    if not results_path.exists():
        return set()
    with results_path.open(encoding="utf-8") as source:
        return {json.loads(line)["chatId"] for line in source if line.strip()}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/interim/conversations/conversations.jsonl")
    parser.add_argument("--output-dir", default="data/processed/emotion-evaluation-qwen35")
    parser.add_argument("--model", default="mlx-community/Qwen3.5-2B-4bit")
    parser.add_argument("--server-url", default="http://127.0.0.1:8080", help="Existing mlx_vlm.server URL.")
    parser.add_argument("--no-launch-server", action="store_true", help="Use an already running server instead of launching one.")
    parser.add_argument("--concurrency", type=int, default=24, help="Concurrent requests submitted to MLX-VLM continuous batching.")
    parser.add_argument("--max-conversation-chars", type=int, default=2000,
                        help="Most-recent user text retained per conversation; 2,000 keeps batches fast on Apple Silicon.")
    parser.add_argument("--limit", type=int, help="Classify only the first N pending conversations (use 100 for a benchmark).")
    parser.add_argument("--overwrite", action="store_true", help="Discard the result file rather than resume it.")
    args = parser.parse_args()
    if args.concurrency < 1 or args.max_conversation_chars < 1:
        parser.error("concurrency and max-conversation-chars must be positive")
    return args


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    results_path = output_dir / "conversation-emotions.jsonl"
    if args.overwrite and results_path.exists():
        results_path.unlink()
    done = existing_chat_ids(results_path)
    counts: Counter = Counter()
    pending: list[dict[str, Any]] = []
    with input_path.open(encoding="utf-8") as source:
        for line in source:
            chat = json.loads(line)
            if chat["chatId"] in done:
                counts["resumed_conversations"] += 1
                continue
            text, message_counts = prepare_conversation(chat, args.max_conversation_chars)
            counts.update(message_counts)
            if not text:
                counts["conversations_without_eligible_user_text"] += 1
                continue
            pending.append({"chatId": chat["chatId"], "firstTimestamp": chat.get("firstTimestamp"), "lastTimestamp": chat.get("lastTimestamp"), "traceCount": chat.get("traceCount"), "conversationText": text})
            if args.limit and len(pending) >= args.limit:
                break

    server = MLXVLMServer(args.model, args.server_url.rstrip("/"), not args.no_launch_server)
    started = time.monotonic()
    try:
        server.start()
        predictions = asyncio.run(classify_all(pending, server.base_url, args.model, args.concurrency))
    finally:
        server.stop()
    elapsed = time.monotonic() - started
    with results_path.open("a", encoding="utf-8") as destination:
        for record, (emotion, confidence, error, raw) in zip(pending, predictions):
            result = {key: value for key, value in record.items() if key != "conversationText"}
            result.update({"emotion": emotion, "confidence": confidence, "model": args.model, "runtime": "mlx-vlm"})
            if error:
                result.update({"parseError": error, "rawModelOutput": raw})
                counts["parse_errors"] += 1
            destination.write(json.dumps(result, ensure_ascii=False) + "\n")
            counts["classified_conversations"] += 1
            counts[f"emotion_{emotion}"] += 1
    manifest: dict[str, Any] = {"model": args.model, "runtime": "mlx-vlm", "input": str(input_path.resolve()), "results": str(results_path.resolve()), "concurrency": args.concurrency, "maxConversationChars": args.max_conversation_chars, "elapsedSeconds": elapsed, "counts": counts, "labels": sorted(EMOTIONS), "classificationUnit": "one result per conversation, based on retained chronological user messages"}
    (output_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"classified {counts['classified_conversations']} conversations in {elapsed:.1f}s")
