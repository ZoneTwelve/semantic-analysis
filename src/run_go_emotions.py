#!/usr/bin/env python3
"""Run SamLowe GoEmotions on the English-likely conversation subset on MPS.

Writes auditable message-level top-3 predictions and a conversation-level
summary (mean score per label across messages). It never modifies source data.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/processed/english-conversations/english-conversations.jsonl")
    parser.add_argument("--model", default="/private/tmp/go-emotions-mps")
    parser.add_argument("--output-dir", default="data/processed/go-emotions-english")
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--limit-chats", type=int, help="Optional bounded smoke test.")
    args = parser.parse_args()
    if args.batch_size < 1:
        parser.error("--batch-size must be positive")

    import torch
    from transformers import pipeline

    if not torch.backends.mps.is_available():
        raise RuntimeError("MPS is unavailable. Run outside the filesystem sandbox on an Apple Silicon host.")
    model_path = Path(args.model)
    if not (model_path / "model.safetensors").is_file():
        raise FileNotFoundError(f"Model weights are unavailable: {model_path / 'model.safetensors'}")
    output = Path(args.output_dir)
    if output.exists():
        raise FileExistsError(f"Output directory exists: {output}. Choose a new --output-dir; do not overwrite prior runs.")
    output.mkdir(parents=True)

    records: list[dict] = []
    with Path(args.input).open(encoding="utf-8") as src:
        for chat_index, line in enumerate(src):
            if args.limit_chats is not None and chat_index >= args.limit_chats:
                break
            chat = json.loads(line)
            for message_index, message in enumerate(chat["messages"]):
                records.append({"chatId": chat["chatId"], "chatMessageCount": chat["messageCount"], "conversationMessageIndex": message_index, **message})

    classifier = pipeline("text-classification", model=str(model_path), tokenizer=str(model_path), device="mps", top_k=3, truncation=True, max_length=512)
    message_path = output / "message-emotions.jsonl"
    summaries: dict[str, defaultdict[str, float]] = defaultdict(lambda: defaultdict(float))
    message_counts: Counter[str] = Counter()
    top_labels: Counter[str] = Counter()
    with message_path.open("w", encoding="utf-8") as dest:
        for start in range(0, len(records), args.batch_size):
            batch = records[start:start + args.batch_size]
            predictions = classifier([record["text"] for record in batch], batch_size=args.batch_size)
            for record, emotions in zip(batch, predictions):
                emotions.sort(key=lambda item: item["score"], reverse=True)
                result = {**record, "topEmotion": emotions[0]["label"], "topEmotionScore": emotions[0]["score"], "emotions": emotions, "model": "SamLowe/roberta-base-go_emotions"}
                dest.write(json.dumps(result, ensure_ascii=False) + "\n")
                top_labels[result["topEmotion"]] += 1
                message_counts[result["chatId"]] += 1
                for emotion in emotions:
                    summaries[result["chatId"]][emotion["label"]] += emotion["score"]
            print(f"classified {min(start + len(batch), len(records))}/{len(records)} messages", flush=True)

    conversation_path = output / "conversation-emotion-summary.jsonl"
    with conversation_path.open("w", encoding="utf-8") as dest:
        for chat_id, label_scores in summaries.items():
            mean_scores = [{"label": label, "meanTop3Score": score / message_counts[chat_id]} for label, score in label_scores.items()]
            mean_scores.sort(key=lambda item: item["meanTop3Score"], reverse=True)
            dest.write(json.dumps({"chatId": chat_id, "classifiedMessageCount": message_counts[chat_id], "dominantEmotion": mean_scores[0]["label"], "emotions": mean_scores}, ensure_ascii=False) + "\n")

    manifest = {"createdAt": datetime.now(timezone.utc).isoformat(), "script": "src/run_go_emotions.py", "model": "SamLowe/roberta-base-go_emotions", "modelPath": str(model_path), "device": "mps", "topK": 3, "batchSize": args.batch_size, "input": args.input, "outputs": {"messageResults": message_path.name, "conversationSummary": conversation_path.name}, "counts": {"conversations": len(summaries), "messages": len(records), "topEmotionCounts": top_labels}, "limitations": "This model is trained on English Reddit comments. Results are probabilistic emotion signals, not user facts or diagnoses."}
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
