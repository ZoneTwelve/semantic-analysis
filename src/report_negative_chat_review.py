#!/usr/bin/env python3
"""Build a no-text Markdown review table for all negative-signal chats."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/processed/negative-emotion-review-v2/all-negative-emotion-chats.jsonl")
    parser.add_argument("--flags", default="data/processed/flagged-cases/flagged-cases.jsonl")
    parser.add_argument("--output", default="reports/negative-emotion-chat-review.md")
    args = parser.parse_args()
    flags = {}
    flag_path = Path(args.flags)
    if flag_path.exists():
        flags = {item["chatId"]: item for line in flag_path.read_text(encoding="utf-8").splitlines() if line.strip() for item in [json.loads(line)]}
    records = [item for line in Path(args.input).read_text(encoding="utf-8").splitlines() if line.strip() for item in [json.loads(line)]]
    records.sort(key=lambda item: item["maxNegativeScore"], reverse=True)
    rows = []
    for item in records:
        flag = flags.get(item["chatId"])
        labels = ", ".join(f"{signal['emotion']} ({signal['score']:.3f})" for signal in item["signals"])
        if flag:
            review_status = f"FLAGGED: {flag['priority']}/{flag['status']}"
            action = "Immediate authorized human safety review"
        elif item["imageGenerationLikely"]:
            review_status = "Excluded: image-generation-like"
            action = "No affect review; retain as audit exclusion"
        else:
            review_status = "Open for review"
            action = "Review original chat in approved system"
        rows.append(f"| `{item['chatId']}` | `{item['reviewAlias']}` | {labels} | {item['maxNegativeScore']:.3f} | {review_status} | {action} |")
    lines = [
        "# Negative Emotion Chat Review Queue",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        "This table contains identifiers and model-review metadata only. It intentionally omits user text. Emotion labels are probabilistic signals, not diagnoses or confirmed issues.",
        "",
        "| Chat ID | Review alias | Negative signal(s) | Max score | Status | Recommended action |",
        "| --- | --- | --- | ---: | --- | --- |",
        *rows,
        "",
        "## Review guidance",
        "",
        "- `FLAGGED` cases require the approved human safety escalation process; do not rely on model output alone.",
        "- `Excluded: image-generation-like` indicates creative content may have caused a false affect signal.",
        "- For `Open for review`, inspect original content only through the approved system. Record product-issue findings as hypotheses with evidence.",
    ]
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
