#!/usr/bin/env python3
"""Create a de-identified Markdown report from a completed GoEmotions run."""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

NEGATIVE = {"anger", "annoyance", "disapproval", "disgust", "disappointment", "embarrassment", "fear", "grief", "nervousness", "remorse", "sadness"}


def pct(value: int, total: int) -> str:
    return f"{value / total * 100:.1f}%" if total else "0.0%"


def table(counter: Counter, total: int, averages: dict[str, float] | None = None, limit: int = 12) -> list[str]:
    lines = ["| Emotion | Count | Share | Mean top-label confidence |", "| --- | ---: | ---: | ---: |"]
    for label, count in counter.most_common(limit):
        confidence = f"{averages[label] / count:.3f}" if averages and count else "—"
        lines.append(f"| {label} | {count:,} | {pct(count, total)} | {confidence} |")
    return lines


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", default="data/processed/go-emotions-english")
    parser.add_argument("--output", default="reports/go-emotions-english-report.md")
    args = parser.parse_args()
    source = Path(args.input_dir)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    top_labels: Counter = Counter()
    confidence_sums: defaultdict[str, float] = defaultdict(float)
    chat_labels: Counter = Counter()
    messages = 0
    high_negative = 0
    with (source / "message-emotions.jsonl").open(encoding="utf-8") as src:
        for line in src:
            record = json.loads(line)
            label = record["topEmotion"]
            score = record["topEmotionScore"]
            top_labels[label] += 1
            confidence_sums[label] += score
            messages += 1
            if label in NEGATIVE and score >= 0.50:
                high_negative += 1
    chats = 0
    with (source / "conversation-emotion-summary.jsonl").open(encoding="utf-8") as src:
        for line in src:
            chat_labels[json.loads(line)["dominantEmotion"]] += 1
            chats += 1
    manifest = json.loads((source / "manifest.json").read_text(encoding="utf-8"))
    lines = [
        "# GoEmotions: English-Likely Conversation Report",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        "## Scope",
        "",
        f"- **Unit:** {chats:,} English-likely chats and {messages:,} retained user messages.",
        "- **Model:** `SamLowe/roberta-base-go_emotions`, run locally on Apple MPS.",
        "- **Output:** top 3 model labels per message; chat-level label is derived from mean scores across each message's top-3 labels.",
        "- **Privacy:** this report contains aggregate statistics only—no raw user messages or identifiers.",
        "",
        "## Message-Level Top Emotion",
        "",
        *table(top_labels, messages, confidence_sums),
        "",
        "## Chat-Level Dominant Emotion",
        "",
        *table(chat_labels, chats),
        "",
        "## Negative-Signal Triage",
        "",
        f"- **{high_negative:,} messages ({pct(high_negative, messages)})** had a negative top emotion with confidence ≥ 0.50.",
        "- This is a review prioritization signal, not evidence of a product issue or a statement about an individual user.",
        "- To identify unreported issues, next cluster these messages by anonymized intent/topic and inspect aggregate patterns such as retries, abandonment, tool errors, or repeated requests. Keep any finding labelled as a hypothesis until independently verified.",
        "",
        "## Interpretation Limits",
        "",
        "- The English-likely subset is heuristic-filtered; it is not guaranteed language identification.",
        "- GoEmotions was trained on English Reddit text. Its labels and confidence scores are probabilistic and context-sensitive.",
        "- A chat label is an aggregation convenience, not a user's enduring emotional state.",
        "",
        "## Reproducibility",
        "",
        f"- Result manifest: `{source / 'manifest.json'}`",
        f"- Batch size: {manifest.get('batchSize')}; top K: {manifest.get('topK')}; device: {manifest.get('device')}.",
    ]
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
