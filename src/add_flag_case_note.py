#!/usr/bin/env python3
"""Append a minimal, text-free authorized review note to an open flagged case."""
from __future__ import annotations

import argparse
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--chat-id", required=True)
    parser.add_argument("--note", required=True, help="Operational summary only; never include raw user text or PII.")
    parser.add_argument("--source", choices=["authorized_human_review", "user_reported_manual_review", "manual_quality_review"], required=True)
    parser.add_argument("--output-dir", default="data/processed/flagged-cases")
    args = parser.parse_args()
    if len(args.note) > 500:
        parser.error("--note must be at most 500 characters")
    if any(token in args.note.lower() for token in ("<user_message>", "http://", "https://", "byebye")):
        parser.error("--note appears to include raw content; provide an operational summary instead")
    output = Path(args.output_dir)
    cases = [json.loads(line) for line in (output / "flagged-cases.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    if not any(case.get("chatId") == args.chat_id and case.get("status") == "open" for case in cases):
        parser.error("no open flagged case exists for this chat ID")
    event = {"eventId": "NOTE-" + uuid.uuid4().hex[:12].upper(), "chatId": args.chat_id, "eventType": "authorized_review_note", "source": args.source, "note": args.note, "createdAt": datetime.now(timezone.utc).isoformat(), "privacy": "No raw user message text is stored."}
    with (output / "flag-case-events.jsonl").open("a", encoding="utf-8") as dest:
        dest.write(json.dumps(event, ensure_ascii=False) + "\n")
    print(json.dumps({"eventId": event["eventId"], "chatId": event["chatId"], "eventType": event["eventType"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
