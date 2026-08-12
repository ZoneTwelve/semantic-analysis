#!/usr/bin/env python
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
TERMINAL_STATUSES = {"withdrawn", "not_tracking"}
CHAT_ID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I)


def known_chat(chat_id: str, conversations: Path) -> bool:
    with conversations.open(encoding="utf-8") as src:
        return any(json.loads(line).get("chatId") == chat_id for line in src)


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()] if path.exists() else []


def current_statuses(output_dir: Path) -> dict[str, str]:
    """Resolve current state from immutable creation records plus lifecycle events."""
    statuses = {case["chatId"]: case.get("status", "open") for case in read_jsonl(output_dir / "flagged-cases.jsonl")}
    for event in read_jsonl(output_dir / "flag-case-events.jsonl"):
        if event.get("eventType") == "flag_status_changed" and event.get("status") in TERMINAL_STATUSES:
            statuses[event["chatId"]] = event["status"]
    return statuses


def refresh_manifest(output_dir: Path, updated_at: str | None = None) -> None:
    """Write derived counts without mutating immutable case or event records."""
    cases = read_jsonl(output_dir / "flagged-cases.jsonl")
    events = read_jsonl(output_dir / "flag-case-events.jsonl")
    statuses = current_statuses(output_dir)
    manifest = {
        "updatedAt": updated_at or datetime.now(timezone.utc).isoformat(),
        "schemaVersion": "1.1",
        "script": "src/flag_chat_case.py",
        "counts": {
            "byCurrentStatus": Counter(statuses.values()),
            "byPriority": Counter(case["priority"] for case in cases),
            "byCategory": Counter(case["category"] for case in cases),
            "totalCases": len(cases),
            "lifecycleEvents": len(events),
        },
        "handling": "Authorized human reviewer must access original content only through the approved system and follow the organization's safety escalation protocol.",
        "privacy": "Contains no user message text. Access is restricted to authorized reviewers.",
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def validate_operational_note(note: str) -> str:
    note = note.strip()
    if not note or len(note) > 500:
        raise ValueError("review note must be 1–500 characters")
    if any(marker in note.lower() for marker in ("<user_message>", "system prompt", "http://", "https://")):
        raise ValueError("review note appears to contain raw or untrusted content")
    return note


def create_case(*, chat_id: str, category: str, priority: str, assessment_source: str,
                review_note: str, output_dir: Path, chat_exists: bool, human_confirmed: bool,
                write: bool = True) -> dict:
    """Create one validated, text-free case; callable by the local browser."""
    if not CHAT_ID_RE.fullmatch(chat_id):
        raise ValueError("chat ID must use UUID format")
    if category not in ALLOWED_CATEGORIES or priority not in ALLOWED_PRIORITIES or assessment_source not in ALLOWED_SOURCES:
        raise ValueError("invalid flag category, priority, or assessment source")
    if not chat_exists:
        raise ValueError("chat ID was not found in the grouped conversation dataset")
    if human_confirmed is not True:
        raise ValueError("explicit human confirmation is required")
    review_note = validate_operational_note(review_note)
    queue = output_dir / "flagged-cases.jsonl"
    existing = read_jsonl(queue)
    if any(case.get("chatId") == chat_id for case in existing):
        raise ValueError("a flagged case already exists for this chat; preserve its lifecycle history")
    now = datetime.now(timezone.utc).isoformat()
    record = {"caseId": "FLAG-" + uuid.uuid4().hex[:12].upper(), "chatId": chat_id,
              "status": "open", "priority": priority, "category": category,
              "assessmentSource": assessment_source, "reviewNote": review_note.strip(),
              "requiredAction": "Authorized human review in the approved system. Follow the organization's safety escalation protocol.",
              "automatedAction": "none", "createdAt": now,
              "humanConfirmed": True,
              "privacy": "No user message text is stored in this flag record."}
    if not write:
        return record
    output_dir.mkdir(parents=True, exist_ok=True)
    with queue.open("a", encoding="utf-8") as dest:
        dest.write(json.dumps(record, ensure_ascii=False) + "\n")
    refresh_manifest(output_dir, now)
    return record


def change_case_status(*, chat_id: str, status: str, assessment_source: str, review_note: str,
                       output_dir: Path, human_confirmed: bool, write: bool = True) -> dict:
    """Append a terminal status event. Original flag records are never changed."""
    if status not in TERMINAL_STATUSES:
        raise ValueError("status must be withdrawn or not_tracking")
    if assessment_source not in ALLOWED_SOURCES:
        raise ValueError("invalid assessment source")
    if human_confirmed is not True:
        raise ValueError("explicit human confirmation is required")
    review_note = validate_operational_note(review_note)
    if current_statuses(output_dir).get(chat_id) != "open":
        raise ValueError("only an open flag can be withdrawn or marked not tracking")
    event = {"eventId": "FLAG-EVENT-" + uuid.uuid4().hex[:12].upper(), "chatId": chat_id,
             "eventType": "flag_status_changed", "previousStatus": "open", "status": status,
             "assessmentSource": assessment_source, "reviewNote": review_note,
             "humanConfirmed": True, "createdAt": datetime.now(timezone.utc).isoformat(),
             "privacy": "No raw user message text is stored in this lifecycle event."}
    if not write:
        return event
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "flag-case-events.jsonl").open("a", encoding="utf-8") as dest:
        dest.write(json.dumps(event, ensure_ascii=False) + "\n")
    refresh_manifest(output_dir, event["createdAt"])
    return event


def main() -> None:
    parser = argparse.ArgumentParser(description="Add a manual, text-free safety-review flag for an existing chat.")
    parser.add_argument("--chat-id", required=True)
    parser.add_argument("--category", choices=sorted(ALLOWED_CATEGORIES), required=True)
    parser.add_argument("--priority", choices=sorted(ALLOWED_PRIORITIES), default="high")
    parser.add_argument("--assessment-source", choices=sorted(ALLOWED_SOURCES), required=True)
    parser.add_argument("--review-note", required=True, help="Minimal operational reason only; never include raw user text or PII.")
    parser.add_argument("--human-confirmed", action="store_true", help="Required confirmation of authorized human assessment.")
    parser.add_argument("--conversations", default="data/interim/conversations/conversations.jsonl")
    parser.add_argument("--output-dir", default="data/processed/flagged-cases")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    conversations = Path(args.conversations)
    output = Path(args.output_dir)
    try:
        record = create_case(chat_id=args.chat_id, category=args.category, priority=args.priority,
                             assessment_source=args.assessment_source, review_note=args.review_note,
                             output_dir=output, chat_exists=known_chat(args.chat_id, conversations),
                             human_confirmed=args.human_confirmed, write=not args.dry_run)
    except ValueError as error:
        parser.error(str(error))
    if args.dry_run:
        print(json.dumps(record, ensure_ascii=False, indent=2))
        return
    print(json.dumps({"caseId": record["caseId"], "chatId": record["chatId"], "status": record["status"], "priority": record["priority"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
