#!/usr/bin/env python3
"""Build a text-free negative-signal review queue, excluding image prompts."""
from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--negative-input", default="data/processed/negative-emotion-review/negative-emotion-chats.jsonl")
    parser.add_argument("--activity-input", default="data/processed/conversation-activity/conversation-activity.jsonl")
    parser.add_argument("--output-dir", default="data/processed/negative-emotion-review-v2")
    args = parser.parse_args()
    output = Path(args.output_dir)
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite: {output}")
    output.mkdir(parents=True)
    activity = {item["chatId"]: item for item in map(json.loads, Path(args.activity_input).read_text(encoding="utf-8").splitlines()) if item}
    all_queue, excluded_queue, review_queue = [], [], []
    for record in map(json.loads, Path(args.negative_input).read_text(encoding="utf-8").splitlines()):
        flag = activity.get(record["chatId"], {"imageGenerationLikely": False, "signalCounts": {}})
        safe_record = {**record, "imageGenerationLikely": flag["imageGenerationLikely"], "activitySignals": flag["signalCounts"]}
        all_queue.append(safe_record)
        (excluded_queue if flag["imageGenerationLikely"] else review_queue).append(safe_record)
    for name, records in (("all-negative-emotion-chats.jsonl", all_queue), ("excluded-image-generation-chats.jsonl", excluded_queue), ("negative-emotion-review-chats.jsonl", review_queue)):
        with (output / name).open("w", encoding="utf-8") as dest:
            for record in records:
                dest.write(json.dumps(record, ensure_ascii=False) + "\n")
    manifest = {"createdAt": datetime.now(timezone.utc).isoformat(), "script": "src/build_negative_review_queue.py", "inputs": {"negative": args.negative_input, "activity": args.activity_input}, "outputs": {"all": "all-negative-emotion-chats.jsonl", "excludedImageGeneration": "excluded-image-generation-chats.jsonl", "review": "negative-emotion-review-chats.jsonl"}, "counts": {"allNegativeChats": len(all_queue), "excludedImageGeneration": len(excluded_queue), "reviewChats": len(review_queue)}, "privacy": "No user message text is copied into any queue.", "limitations": "Activity classification and emotions are heuristic/model signals requiring human review."}
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
