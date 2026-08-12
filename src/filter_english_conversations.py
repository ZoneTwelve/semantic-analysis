#!/usr/bin/env python3
"""Create a conservative English-likely, user-only conversation subset.

This is deliberately a heuristic, not a language-identification model. It
keeps every decision auditable and avoids describing the result as certain
English. Source data is read only; outputs are new JSONL files.
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from collections import Counter, defaultdict
from pathlib import Path

NON_LATIN_RE = re.compile(r"[^\x00-\x7f]")
WORD_RE = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")
STOPWORDS = frozenset("a an and are as at be but by can did do does for from had has have he her him his how i if in is it its me my no not of on or our please she so that the their them then there these they this to us was we were what when where which who why will with would you your yes thanks thank okay help need want could should".split())
SHORT_ENGLISH = frozenset("ok okay yes no thanks thank you hi hello help please great awesome cool".split())
AUTOMATION_RE = re.compile(r"\b(run the following skill|available parameters and context|respond in (?:en|zh)-|\[skill:|runSkill:|<user_message>|<sprite_message_context>|scheduled task context)\b", re.I)


def classify(text: str) -> tuple[bool, str]:
    clean = " ".join(text.split())
    if not clean:
        return False, "empty"
    if AUTOMATION_RE.search(clean):
        return False, "automation_or_instruction_template"
    if NON_LATIN_RE.search(clean):
        return False, "contains_non_ascii_text"
    words = [word.lower() for word in WORD_RE.findall(clean)]
    if not words:
        return False, "no_latin_words"
    if len(words) <= 3:
        return (True, "short_english_phrase") if " ".join(words) in SHORT_ENGLISH else (False, "short_ambiguous_text")
    if any(word in STOPWORDS for word in words):
        return True, "english_function_word_signal"
    # Common technical/product queries can lack function words (e.g. "fix API 401").
    if re.search(r"\b(api|app|browser|code|error|login|model|server|file|install|download|image|video)\b", clean, re.I):
        return True, "english_technical_vocabulary_signal"
    return False, "no_english_signal"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/processed/emotion-evaluation/eligible-user-messages.jsonl")
    parser.add_argument("--output-dir", default="data/processed/english-conversations")
    args = parser.parse_args()
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=False)

    by_chat: dict[str, list[dict]] = defaultdict(list)
    counts: Counter = Counter()
    with Path(args.input).open(encoding="utf-8") as src:
        for line in src:
            record = json.loads(line)
            allowed, reason = classify(record["text"])
            record["englishLikely"] = allowed
            record["languageDecisionReason"] = reason
            by_chat[record["chatId"]].append(record)
            counts["messages_seen"] += 1
            counts[f"message_{reason}"] += 1

    kept_path = output / "english-conversations.jsonl"
    excluded_path = output / "excluded-conversations.jsonl"
    with kept_path.open("w", encoding="utf-8") as kept, excluded_path.open("w", encoding="utf-8") as excluded:
        for chat_id, records in by_chat.items():
            records.sort(key=lambda record: (record.get("timestamp") or "", record.get("traceIndex", 0), record.get("messageIndex", 0)))
            failures = [record["languageDecisionReason"] for record in records if not record["englishLikely"]]
            if failures:
                excluded.write(json.dumps({"chatId": chat_id, "messageCount": len(records), "exclusionReasons": dict(Counter(failures))}, ensure_ascii=False) + "\n")
                counts["conversations_excluded"] += 1
            else:
                kept.write(json.dumps({"chatId": chat_id, "messageCount": len(records), "messages": [{key: record[key] for key in ("traceId", "timestamp", "traceIndex", "messageIndex", "text", "languageDecisionReason")} for record in records]}, ensure_ascii=False) + "\n")
                counts["conversations_english_likely"] += 1

    manifest = {
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "script": "src/filter_english_conversations.py",
        "classification": "conservative heuristic: english_likely, not a language-identification model",
        "input": str(Path(args.input)),
        "inclusionRule": "every retained eligible user message in a chat must pass the English-likely heuristic",
        "excludedAutomationTemplates": True,
        "outputs": {"englishConversations": kept_path.name, "excludedConversations": excluded_path.name},
        "counts": counts,
        "limitations": "ASCII/English-function-word heuristics can exclude valid English and include some non-English Latin-script text. Use a dedicated language-ID model before high-stakes conclusions.",
    }
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
