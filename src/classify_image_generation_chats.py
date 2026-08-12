#!/usr/bin/env python3
"""Label image-generation-like chats using conservative, explainable signals.

The goal is to prevent fictional/creative image prompts from being interpreted
as user affect. This script emits no user text; it records only rule names.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

RULES = {
    "explicit_image_request": re.compile(r"\b(?:generate|create|make|draw|render|produce) (?:an? )?(?:image|picture|illustration|artwork|photo|portrait)\b", re.I),
    "prompt_vocabulary": re.compile(r"\b(?:image prompt|negative prompt|aspect ratio|no watermark|no text|speech bubbles|resolution|photorealistic|cinematic lighting|camera angle|color palette)\b", re.I),
    "image_style_vocabulary": re.compile(r"\b(?:anime|manhua|manga|pixel art|oil painting|watercolor|3d render|cel-shaded|screentone)\b", re.I),
}


def message_text(value):
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "\n".join(item.get("text", "") for item in value if isinstance(item, dict) and item.get("type") == "text")
    return ""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/interim/conversations/conversations.jsonl")
    parser.add_argument("--output", default="data/processed/conversation-activity/conversation-activity.jsonl")
    args = parser.parse_args()
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite: {destination}")
    counts = Counter()
    with Path(args.input).open(encoding="utf-8") as src, destination.open("w", encoding="utf-8") as dest:
        for line in src:
            chat = json.loads(line)
            rules = Counter()
            for trace in chat.get("turns", []):
                for message in trace.get("input") if isinstance(trace.get("input"), list) else []:
                    if not isinstance(message, dict) or message.get("role") != "user":
                        continue
                    text = message_text(message.get("content"))
                    for name, pattern in RULES.items():
                        if pattern.search(text):
                            rules[name] += 1
            # Require explicit intent, or two separate image-prompt-style signals.
            image_generation_likely = bool(rules["explicit_image_request"] or sum(bool(rules[name]) for name in ("prompt_vocabulary", "image_style_vocabulary")) >= 2)
            result = {"chatId": chat["chatId"], "imageGenerationLikely": image_generation_likely, "signalCounts": dict(rules)}
            dest.write(json.dumps(result, ensure_ascii=False) + "\n")
            counts["chats"] += 1
            counts["image_generation_likely" if image_generation_likely else "other"] += 1
    manifest = {"createdAt": datetime.now(timezone.utc).isoformat(), "script": "src/classify_image_generation_chats.py", "input": args.input, "output": str(destination), "rules": {name: pattern.pattern for name, pattern in RULES.items()}, "decisionRule": "explicit image request OR two independent prompt/style signal categories", "counts": counts, "limitations": "Conservative heuristic. A non-image chat may be flagged and some image chats may be missed; use as an exclusion/review signal, not ground truth."}
    destination.with_name("manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
