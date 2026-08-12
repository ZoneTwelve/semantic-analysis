#!/usr/bin/env python3
"""Safely add a chat to the private, text-free flagged-case dataset.

This tool creates a review record only. It does not classify, diagnose, notify,
or take action on behalf of a reviewer.
"""
from __future__ import annotations

import argparse
import json
import re
import uuid
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ALLOWED_CATEGORIES = {"potential_self_harm", "potential_imminent_danger", "safety_review", "other_human_review"}
ALLOWED_PRIORITIES = {"urgent", "high", "normal"}
ALLOWED_SOURCES = {"authorized_human_review", "user_reported_manual_review", "manual_quality_review"}
CHAT_ID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I)


def known_chat(chat_id: str, conversations: Path) -> bool:
    with conversations.open(encoding="utf-8") as src:
        return any(json.loads(line).get("chatId") == chat_id for line in src)


def create_case(*, chat_id: str, category: str, priority: str, assessment_source: str,
                review_note: str, output_dir: Path, chat_exists: bool, write: bool = True) -> dict:
    """Create one validated, text-free case; callable by the local browser."""
    if not CHAT_ID_RE.fullmatch(chat_id):
        raise ValueError("chat ID must use UUID format")
    if category not in ALLOWED_CATEGORIES or priority not in ALLOWED_PRIORITIES or assessment_source not in ALLOWED_SOURCES:
        raise ValueError("invalid flag category, priority, or assessment source")
    if not chat_exists:
        raise ValueError("chat ID was not found in the grouped conversation dataset")
    if not review_note.strip() or len(review_note) > 500:
        raise ValueError("review note must be 1–500 characters")
    if any(marker in review_note.lower() for marker in ("<user_message>", "system prompt", "http://", "https://")):
        raise ValueError("review note appears to contain raw or untrusted content")
    queue = output_dir / "flagged-cases.jsonl"
    existing = [json.loads(line) for line in queue.read_text(encoding="utf-8").splitlines() if line.strip()] if queue.exists() else []
    if any(case["chatId"] == chat_id and case.get("status") == "open" for case in existing):
        raise ValueError("an open flagged case already exists for this chat")
    now = datetime.now(timezone.utc).isoformat()
    record = {"caseId": "FLAG-" + uuid.uuid4().hex[:12].upper(), "chatId": chat_id,
              "status": "open", "priority": priority, "category": category,
              "assessmentSource": assessment_source, "reviewNote": review_note.strip(),
              "requiredAction": "Authorized human review in the approved system. Follow the organization's safety escalation protocol.",
              "automatedAction": "none", "createdAt": now,
              "privacy": "No user message text is stored in this flag record."}
    if not write:
        return record
    output_dir.mkdir(parents=True, exist_ok=True)
    with queue.open("a", encoding="utf-8") as dest:
        dest.write(json.dumps(record, ensure_ascii=False) + "\n")
    cases = [*existing, record]
    manifest = {"updatedAt": now, "schemaVersion": "1.0", "script": "src/flag_chat_case.py",
                "counts": {"byStatus": Counter(case["status"] for case in cases), "byPriority": Counter(case["priority"] for case in cases), "byCategory": Counter(case["category"] for case in cases), "total": len(cases)},
                "handling": "Authorized human reviewer must access original content only through the approved system and follow the organization's safety escalation protocol.",
                "privacy": "Contains no user message text. Access is restricted to authorized reviewers."}
    (output_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return record


def main() -> None:
    parser = argparse.ArgumentParser(description="Add a manual, text-free safety-review flag for an existing chat.")
    parser.add_argument("--chat-id", required=True)
    parser.add_argument("--category", choices=sorted(ALLOWED_CATEGORIES), required=True)
    parser.add_argument("--priority", choices=sorted(ALLOWED_PRIORITIES), default="high")
    parser.add_argument("--assessment-source", choices=sorted(ALLOWED_SOURCES), required=True)
    parser.add_argument("--review-note", required=True, help="Minimal operational reason only; never include raw user text or PII.")
    parser.add_argument("--conversations", default="data/interim/conversations/conversations.jsonl")
    parser.add_argument("--output-dir", default="data/processed/flagged-cases")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    conversations = Path(args.conversations)
    output = Path(args.output_dir)
    try:
        record = create_case(chat_id=args.chat_id, category=args.category, priority=args.priority,
                             assessment_source=args.assessment_source, review_note=args.review_note,
                             output_dir=output, chat_exists=known_chat(args.chat_id, conversations), write=not args.dry_run)
    except ValueError as error:
        parser.error(str(error))
    if args.dry_run:
        print(json.dumps(record, ensure_ascii=False, indent=2))
        return
    print(json.dumps({"caseId": record["caseId"], "chatId": record["chatId"], "status": record["status"], "priority": record["priority"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
