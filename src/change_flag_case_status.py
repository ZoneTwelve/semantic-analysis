#!/usr/bin/env python
"""Append a human-confirmed, text-free terminal lifecycle event for an open flag."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from flag_chat_case import ALLOWED_SOURCES, TERMINAL_STATUSES, change_case_status


def main() -> None:
    parser = argparse.ArgumentParser(description="Withdraw an open flag or mark it not tracking without deleting audit history.")
    parser.add_argument("--chat-id", required=True)
    parser.add_argument("--status", choices=sorted(TERMINAL_STATUSES), required=True)
    parser.add_argument("--assessment-source", choices=sorted(ALLOWED_SOURCES), required=True)
    parser.add_argument("--review-note", required=True, help="Text-free operational reason only.")
    parser.add_argument("--human-confirmed", action="store_true", help="Required confirmation of authorized human assessment.")
    parser.add_argument("--output-dir", default="data/processed/flagged-cases")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        event = change_case_status(chat_id=args.chat_id, status=args.status,
                                   assessment_source=args.assessment_source, review_note=args.review_note,
                                   output_dir=Path(args.output_dir), human_confirmed=args.human_confirmed,
                                   write=not args.dry_run)
    except ValueError as error:
        parser.error(str(error))
    print(json.dumps({key: event[key] for key in ("eventId", "chatId", "eventType", "status")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
