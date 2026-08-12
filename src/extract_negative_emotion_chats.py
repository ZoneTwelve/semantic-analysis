#!/usr/bin/env python3
"""Create a private, no-text review queue for negative GoEmotions signals."""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

NEGATIVE = {"anger", "annoyance", "disapproval", "disgust", "disappointment", "embarrassment", "fear", "grief", "nervousness", "remorse", "sadness"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/processed/go-emotions-english/message-emotions.jsonl")
    parser.add_argument("--output-dir", default="data/processed/negative-emotion-review")
    parser.add_argument("--min-score", type=float, default=0.0)
    args = parser.parse_args()
    if not 0 <= args.min_score <= 1:
        parser.error("--min-score must be between 0 and 1")
    output = Path(args.output_dir)
    if output.exists():
        raise FileExistsError(f"Output directory already exists: {output}")
    output.mkdir(parents=True)

    grouped: dict[str, list[dict]] = defaultdict(list)
    labels = Counter()
    with Path(args.input).open(encoding="utf-8") as src:
        for line in src:
            item = json.loads(line)
            if item["topEmotion"] not in NEGATIVE or item["topEmotionScore"] < args.min_score:
                continue
            labels[item["topEmotion"]] += 1
            # Deliberately omit `text` and all message content.
            grouped[item["chatId"]].append({
                "timestamp": item.get("timestamp"),
                "traceId": item.get("traceId"),
                "emotion": item["topEmotion"],
                "score": item["topEmotionScore"],
            })
    queue = output / "negative-emotion-chats.jsonl"
    with queue.open("w", encoding="utf-8") as dest:
        for chat_id, signals in sorted(grouped.items(), key=lambda entry: max(signal["score"] for signal in entry[1]), reverse=True):
            signals.sort(key=lambda signal: (signal["timestamp"] or "", signal["traceId"] or ""))
            dest.write(json.dumps({
                "chatId": chat_id,
                "reviewAlias": "NEG-" + hashlib.sha256(chat_id.encode()).hexdigest()[:10].upper(),
                "negativeSignalCount": len(signals),
                "maxNegativeScore": max(signal["score"] for signal in signals),
                "signals": signals,
            }, ensure_ascii=False) + "\n")
    manifest = {"createdAt": datetime.now(timezone.utc).isoformat(), "script": "src/extract_negative_emotion_chats.py", "input": args.input, "minScore": args.min_score, "negativeLabels": sorted(NEGATIVE), "output": queue.name, "counts": {"chats": len(grouped), "signals": sum(labels.values()), "signalsByLabel": labels}, "privacy": "The review queue intentionally contains no user message text. It retains source identifiers solely for authorized local review.", "limitations": "Model labels and scores are probabilistic review signals, not confirmed user sentiment or product issues."}
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
