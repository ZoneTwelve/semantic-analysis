"""Prepare auditable, user-only conversation text for classification."""
from __future__ import annotations

import re
from collections import Counter
from typing import Any

SYSTEM_MARKERS = [
    r"\[scheduled task context\]", r"<sprite_message_context>",
    r"<youmind_runtime_context>", r"<system(?:_message)?>", r"<developer(?:_message)?>",
]
INJECTION_MARKERS = [
    r"\b(ignore|disregard|forget) (all |any )?(previous|prior|above) (instructions|rules|messages)",
    r"\b(system prompt|developer message|jailbreak|dan mode)\b", r"\bdo not follow (the )?(previous|above)",
    r"忽略.{0,12}(之前|上述|上面).{0,12}(指令|规则|提示)", r"系统提示词|开发者消息|越狱",
]
USER_MESSAGE_RE = re.compile(r"<user_message>\s*(.*?)\s*</user_message>", re.I | re.S)


def text_content(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "\n".join(
            str(item.get("text", ""))
            for item in value
            if isinstance(item, dict) and item.get("type") == "text"
        )
    return ""


def filter_text(raw: str) -> tuple[str | None, str | None]:
    raw = raw.strip()
    embedded = USER_MESSAGE_RE.search(raw)
    text = (embedded.group(1) if embedded else raw).strip()
    if not text:
        return None, "empty_or_nontext"
    if any(re.search(pattern, raw, re.I) for pattern in SYSTEM_MARKERS) and not embedded:
        return None, "runtime_or_scheduled_context"
    if any(re.search(pattern, text, re.I) for pattern in INJECTION_MARKERS):
        return None, "prompt_injection_pattern"
    return text, None


def prepare_conversation(chat: dict[str, Any], max_chars: int) -> tuple[str, Counter]:
    """Extract chronological user text, keeping the most recent part if needed."""
    messages: list[str] = []
    counts: Counter = Counter()
    for trace in chat.get("turns", []):
        inputs = trace.get("input", []) if isinstance(trace.get("input"), list) else []
        for message in inputs:
            if not isinstance(message, dict) or message.get("role") != "user":
                continue
            counts["user_message_candidates"] += 1
            text, reason = filter_text(text_content(message.get("content")))
            if reason:
                counts[f"excluded_{reason}"] += 1
            else:
                messages.append(text or "")
                counts["included_user_messages"] += 1
    joined = "\n\n".join(f"[User message {index}]\n{text}" for index, text in enumerate(messages, start=1))
    if len(joined) > max_chars:
        joined = "[Earlier user messages omitted for speed]\n\n" + joined[-max_chars:]
        counts["truncated_conversations"] += 1
    return joined, counts
