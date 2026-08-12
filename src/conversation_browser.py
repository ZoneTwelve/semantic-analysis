#!/usr/bin/env python
"""Local, read-only browser for structured conversations.

The SQLite index contains metadata and byte offsets only. Conversation bodies
remain in data/interim/conversations/conversations.jsonl and are loaded only
when a reader opens a specific chat.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from flag_chat_case import (
    ALLOWED_CATEGORIES,
    ALLOWED_PRIORITIES,
    ALLOWED_SOURCES,
    change_case_status,
    create_case,
    current_statuses,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data/interim/conversations/conversations.jsonl"
DEFAULT_INDEX = ROOT / "data/processed/conversation-browser/conversations.sqlite3"
DEFAULT_FLAG_OUTPUT = ROOT / "data/processed/flagged-cases"
INDEX_VERSION = "2"


def connect(index_path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(index_path)
    connection.row_factory = sqlite3.Row
    return connection


def source_signature(source: Path) -> str:
    stat = source.stat()
    return f"{stat.st_size}:{stat.st_mtime_ns}"


def index_is_current(index_path: Path, source: Path) -> bool:
    if not index_path.exists():
        return False
    with connect(index_path) as connection:
        rows = {row["key"]: row["value"] for row in connection.execute("SELECT key, value FROM metadata")}
    return rows.get("source_signature") == source_signature(source) and rows.get("index_version") == INDEX_VERSION


def message_text(value: object) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "\n".join(message_text(item) for item in value)
    if isinstance(value, dict):
        return str(value.get("text", ""))
    return ""


def preview(chat: dict) -> str:
    """Keep a small recent user-text excerpt solely for browsing/searching."""
    latest = ""
    for turn in chat.get("turns", []):
        for message in turn.get("input", []) if isinstance(turn.get("input"), list) else []:
            if isinstance(message, dict) and message.get("role") == "user":
                candidate = message_text(message.get("content")).strip()
                if candidate:
                    latest = candidate
    return " ".join(latest.split())[:360]


def build_index(source: Path, index_path: Path, rebuild: bool) -> int:
    """Index records without retaining conversation bodies or duplicating the dataset."""
    if not source.exists():
        raise FileNotFoundError(f"Conversation input not found: {source}")
    if index_is_current(index_path, source) and not rebuild:
        with connect(index_path) as connection:
            return connection.execute("SELECT COUNT(*) FROM conversations").fetchone()[0]
    index_path.parent.mkdir(parents=True, exist_ok=True)
    if index_path.exists():
        index_path.unlink()
    with connect(index_path) as connection:
        connection.executescript("""
            CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE conversations (
                chat_id TEXT PRIMARY KEY,
                first_timestamp TEXT,
                last_timestamp TEXT,
                trace_count INTEGER,
                preview TEXT NOT NULL,
                byte_offset INTEGER NOT NULL,
                byte_length INTEGER NOT NULL
            );
            CREATE INDEX conversations_first_timestamp ON conversations(first_timestamp DESC);
            CREATE INDEX conversations_preview ON conversations(preview);
        """)
        inserted = 0
        with source.open("rb") as records:
            while True:
                offset = records.tell()
                line = records.readline()
                if not line:
                    break
                chat = json.loads(line)
                connection.execute(
                    "INSERT INTO conversations VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (chat["chatId"], chat.get("firstTimestamp"), chat.get("lastTimestamp"),
                     chat.get("traceCount"), preview(chat), offset, len(line)),
                )
                inserted += 1
                if inserted % 1_000 == 0:
                    connection.commit()
                    print(f"indexed {inserted:,} conversations", flush=True)
        connection.executemany("INSERT INTO metadata VALUES (?, ?)", [
            ("source", str(source)),
            ("source_signature", source_signature(source)),
            ("index_version", INDEX_VERSION),
            ("created_at", datetime.now(timezone.utc).isoformat()),
        ])
        connection.commit()
    return inserted


def load_conversation(source: Path, offset: int, length: int) -> dict:
    with source.open("rb") as records:
        records.seek(offset)
        return json.loads(records.read(length))


def page() -> str:
    return """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Conversation Browser</title><style>
:root{color-scheme:light dark;font-family:ui-sans-serif,system-ui,sans-serif}body{margin:0;background:Canvas;color:CanvasText}.app{display:grid;grid-template-columns:minmax(320px,36%) 1fr;height:100vh}.sidebar{border-right:1px solid color-mix(in srgb,CanvasText 20%,transparent);padding:16px;overflow:auto}.reader{padding:24px;overflow:auto}.search{display:flex;gap:8px}.search input{min-width:0;flex:1;padding:9px}.search button,.pager button,.flag button{padding:8px 12px}.status{color:GrayText;font-size:.9rem;margin:12px 0}.pager{display:flex;justify-content:space-between;align-items:center;gap:8px;margin:10px 0}.item{width:100%;text-align:left;margin:0;padding:13px 4px;border:0;border-bottom:1px solid color-mix(in srgb,CanvasText 12%,transparent);background:transparent;color:inherit;cursor:pointer}.item:hover,.item:focus{background:color-mix(in srgb,Highlight 15%,transparent)}.preview{font-size:.92rem;line-height:1.35;margin:5px 0;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}.id{font-family:ui-monospace,monospace;font-size:.72rem;overflow-wrap:anywhere;color:GrayText}.meta{color:GrayText;font-size:.82rem;margin-top:4px}.turn,.flag{border:1px solid color-mix(in srgb,CanvasText 18%,transparent);border-radius:8px;margin:16px 0;padding:12px}.turn summary{cursor:pointer;font-weight:600}.message{margin:12px 0;border-left:4px solid color-mix(in srgb,Highlight 45%,transparent);padding:8px 12px;background:color-mix(in srgb,CanvasText 5%,transparent)}.message.assistant{border-left-color:color-mix(in srgb,GrayText 45%,transparent)}.role{font-size:.8rem;color:GrayText;margin-bottom:5px;text-transform:uppercase}.content{white-space:pre-wrap;overflow-wrap:anywhere}.raw,.flag textarea,.flag select{width:100%;min-height:36px;box-sizing:border-box;font-family:inherit;margin:5px 0 10px}.raw{min-height:180px;font-family:ui-monospace,monospace}.flag textarea{min-height:68px}.flag label{display:block;margin-top:6px}.flag .confirm{font-size:.9rem}.flag-status{margin-top:8px;color:GrayText}@media(max-width:700px){.app{display:block;height:auto}.sidebar{border-right:0;border-bottom:1px solid color-mix(in srgb,CanvasText 20%,transparent);max-height:42vh}.reader{min-height:58vh}}</style></head>
<body><main class="app"><aside class="sidebar"><h1>Browse conversations</h1><form class="search" id="search"><input id="q" aria-label="Search conversations" placeholder="Search recent user text or chat ID"><button>Search</button></form><label class="meta"><input id="open-flags-only" type="checkbox"> Show open flags only</label><p class="status" id="status"></p><nav class="pager" aria-label="Result pages"><button id="previous" type="button">Previous</button><span id="page"></span><button id="next" type="button">Next</button></nav><section id="list" aria-label="Conversation results"></section></aside><section class="reader" id="reader"><h2>Choose a conversation</h2><p>Browse the newest conversations on the left, or search the latest user-message preview.</p></section></main>
<script>
const list=document.querySelector('#list'),status=document.querySelector('#status'),reader=document.querySelector('#reader'),q=document.querySelector('#q'),openFlagsOnly=document.querySelector('#open-flags-only'),previous=document.querySelector('#previous'),next=document.querySelector('#next'),pageLabel=document.querySelector('#page');let offset=0;const pageSize=50;
function element(tag,cls,text){const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e}
async function search(){status.textContent='Loading…';list.replaceChildren();try{const response=await fetch(`/api/conversations?q=${encodeURIComponent(q.value)}&offset=${offset}&limit=${pageSize}&flagged=${openFlagsOnly.checked?'1':'0'}`);if(!response.ok)throw new Error(`HTTP ${response.status}`);const data=await response.json();const first=data.total?offset+1:0,last=Math.min(offset+data.items.length,data.total);status.textContent=`Showing ${first}–${last} of ${data.total}`;pageLabel.textContent=`Page ${Math.floor(offset/pageSize)+1}`;previous.disabled=offset===0;next.disabled=offset+pageSize>=data.total;for(const chat of data.items){const b=element('button','item');b.type='button';const flagLabel=chat.flagStatus==='open'?' · open flag':'';b.append(element('div','preview',chat.preview||'No user-text preview available'),element('div','meta',`${chat.traceCount||0} turns · ${chat.firstTimestamp||'no timestamp'}${flagLabel}`),element('div','id',chat.chatId));b.onclick=()=>openChat(chat.chatId);list.append(b)}}catch(error){status.textContent=`Unable to load conversations: ${error.message}`;pageLabel.textContent='';previous.disabled=true;next.disabled=true}}
function text(value){if(typeof value==='string')return value;if(Array.isArray(value))return value.map(text).filter(Boolean).join('\\n');if(value&&typeof value==='object'){if(typeof value.text==='string')return value.text;return JSON.stringify(value,null,2)}return ''}
function appendMessages(parent,value,role){const values=Array.isArray(value)?value:[value];for(const part of values){const body=text(part);if(!body)continue;const m=element('article','message '+(role==='assistant'?'assistant':''));m.append(element('div','role',role),element('div','content',body));parent.append(m)}}
function option(value,label){const o=document.createElement('option');o.value=value;o.textContent=label;return o}
function flagForm(chatId){const form=element('form','flag');form.append(element('h3','', 'Create human review flag'));form.append(element('p','meta','This is manual only. Do not paste conversation text or personal data into the note.'));const category=element('select','');category.name='category';category.setAttribute('aria-label','Flag category');category.append(option('safety_review','Safety review'),option('potential_self_harm','Potential self-harm'),option('potential_imminent_danger','Potential imminent danger'),option('other_human_review','Other human review'));const priority=element('select','');priority.name='priority';priority.setAttribute('aria-label','Flag priority');priority.append(option('high','High'),option('urgent','Urgent'),option('normal','Normal'));const source=element('select','');source.name='assessmentSource';source.setAttribute('aria-label','Assessment source');source.append(option('authorized_human_review','Authorized human review'),option('user_reported_manual_review','User-reported manual review'),option('manual_quality_review','Manual quality review'));const note=element('textarea','');note.name='reviewNote';note.maxLength=500;note.required=true;note.placeholder='Minimal operational note; no raw conversation text';note.setAttribute('aria-label','Text-free operational note');for(const [label,control] of [['Category',category],['Priority',priority],['Assessment source',source],['Operational note',note]]){form.append(element('label','',label),control)}const confirmation=element('input','');confirmation.type='checkbox';confirmation.required=true;confirmation.setAttribute('aria-label','Confirm human assessment');const confirmLabel=element('label','confirm');confirmLabel.append(confirmation,document.createTextNode(' I completed an authorized human assessment and this note contains no conversation text.'));const submit=element('button','', 'Create flag');submit.type='submit';const result=element('p','flag-status');form.append(confirmLabel,submit,result);form.onsubmit=async event=>{event.preventDefault();submit.disabled=true;result.textContent='Saving…';try{const response=await fetch('/api/flags',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({chatId,category:category.value,priority:priority.value,assessmentSource:source.value,reviewNote:note.value,humanConfirmed:confirmation.checked})});const data=await response.json();if(!response.ok)throw new Error(data.error||`HTTP ${response.status}`);result.textContent=`Flag ${data.caseId} created as ${data.priority}.`;form.querySelectorAll('select,textarea,input,button').forEach(control=>control.disabled=true)}catch(error){result.textContent=`Unable to create flag: ${error.message}`;submit.disabled=false}};return form}
function lifecycleForm(chatId){const form=element('form','flag');form.append(element('h3','', 'Update flag lifecycle'));form.append(element('p','meta','This appends an audit event; it never deletes the original flag.'));const status=element('select','');status.setAttribute('aria-label','New flag status');status.append(option('withdrawn','Withdraw flag'),option('not_tracking','Mark not tracking'));const source=element('select','');source.setAttribute('aria-label','Lifecycle assessment source');source.append(option('authorized_human_review','Authorized human review'),option('user_reported_manual_review','User-reported manual review'),option('manual_quality_review','Manual quality review'));const note=element('textarea','');note.required=true;note.maxLength=500;note.placeholder='Text-free operational reason';note.setAttribute('aria-label','Lifecycle operational note');const confirmation=element('input','');confirmation.type='checkbox';confirmation.required=true;confirmation.setAttribute('aria-label','Confirm lifecycle decision');const confirmLabel=element('label','confirm');confirmLabel.append(confirmation,document.createTextNode(' I confirm this authorized human decision and the note contains no conversation text.'));const submit=element('button','', 'Save lifecycle decision');submit.type='submit';const result=element('p','flag-status');for(const [label,control] of [['Decision',status],['Assessment source',source],['Operational note',note]])form.append(element('label','',label),control);form.append(confirmLabel,submit,result);form.onsubmit=async event=>{event.preventDefault();submit.disabled=true;result.textContent='Saving…';try{const response=await fetch('/api/flags/'+encodeURIComponent(chatId)+'/status',{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify({status:status.value,assessmentSource:source.value,reviewNote:note.value,humanConfirmed:confirmation.checked})});const data=await response.json();if(!response.ok)throw new Error(data.error||`HTTP ${response.status}`);result.textContent=`Status changed to ${data.status}.`;form.querySelectorAll('select,textarea,input,button').forEach(control=>control.disabled=true)}catch(error){result.textContent=`Unable to update flag: ${error.message}`;submit.disabled=false}};return form}
async function openChat(id){reader.replaceChildren(element('p','',`Loading ${id}…`));try{const response=await fetch('/api/conversations/'+encodeURIComponent(id));if(!response.ok)throw new Error(`HTTP ${response.status}`);const chat=await response.json();reader.replaceChildren();const statusText=chat.flagStatus?` · flag status: ${chat.flagStatus}`:'';reader.append(element('h2','',chat.chatId),element('p','meta',`${chat.traceCount||chat.turns.length} turns · ${chat.firstTimestamp||''} — ${chat.lastTimestamp||''}${statusText}`),chat.flagStatus==='open'?lifecycleForm(chat.chatId):chat.flagStatus?element('p','flag-status',`This flag is ${chat.flagStatus}.`):flagForm(chat.chatId));for(const [n,turn] of chat.turns.entries()){const details=element('details','turn');details.open=true;const summary=element('summary','',`Turn ${n+1} · ${turn.name||'unnamed'} · ${turn.timestamp||'no timestamp'}`);details.append(summary);appendMessages(details,turn.input,'user');appendMessages(details,turn.output,'assistant');const raw=element('details','');raw.append(element('summary','', 'Raw turn JSON'));const area=element('textarea','raw');area.readOnly=true;area.value=JSON.stringify(turn,null,2);raw.append(area);details.append(raw);reader.append(details)}}catch(error){reader.replaceChildren(element('p','',`Unable to load conversation: ${error.message}`))}}
document.querySelector('#search').addEventListener('submit',event=>{event.preventDefault();offset=0;search()});openFlagsOnly.onchange=()=>{offset=0;search()};previous.onclick=()=>{offset=Math.max(0,offset-pageSize);search()};next.onclick=()=>{offset+=pageSize;search()};search();
</script></body></html>"""


def handler_factory(source: Path, index_path: Path, flag_output: Path):
    class Handler(BaseHTTPRequestHandler):
        def send_json(self, value: object, status: int = HTTPStatus.OK) -> None:
            payload = json.dumps(value, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def flag_statuses(self) -> dict[str, str]:
            return current_statuses(flag_output)

        def request_json(self) -> dict:
            size = int(self.headers.get("Content-Length", "0"))
            if size < 1 or size > 1_500:
                raise ValueError("invalid request size")
            body = json.loads(self.rfile.read(size))
            if not isinstance(body, dict):
                raise ValueError("request must be a JSON object")
            return body

        def do_GET(self) -> None:  # noqa: N802
            request = urlparse(self.path)
            if request.path == "/":
                payload = page().encode("utf-8")
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
                return
            if request.path == "/api/conversations":
                parameters = parse_qs(request.query)
                query = parameters.get("q", [""])[0].strip()
                flagged_only = parameters.get("flagged", ["0"])[0] == "1"
                offset = max(0, int(parameters.get("offset", ["0"])[0]))
                limit = min(100, max(1, int(parameters.get("limit", ["50"])[0])))
                with connect(index_path) as connection:
                    statuses = self.flag_statuses()
                    open_ids = {chat_id for chat_id, status in statuses.items() if status == "open"}
                    condition, values = "", []
                    if query:
                        term = f"%{query}%"
                        condition, values = "chat_id LIKE ? OR preview LIKE ?", [term, term]
                    if flagged_only:
                        if not open_ids:
                            self.send_json({"total": 0, "items": []})
                            return
                        flag_condition = "chat_id IN (" + ",".join("?" for _ in open_ids) + ")"
                        condition = f"({condition}) AND {flag_condition}" if condition else flag_condition
                        values.extend(sorted(open_ids))
                    if condition:
                        rows = connection.execute(f"SELECT chat_id, first_timestamp, last_timestamp, trace_count, preview FROM conversations WHERE {condition} ORDER BY first_timestamp DESC LIMIT ? OFFSET ?", (*values, limit, offset)).fetchall()
                    else:
                        rows = connection.execute("SELECT chat_id, first_timestamp, last_timestamp, trace_count, preview FROM conversations ORDER BY first_timestamp DESC LIMIT ? OFFSET ?", (limit, offset)).fetchall()
                    total = connection.execute("SELECT COUNT(*) FROM conversations" + (f" WHERE {condition}" if condition else ""), values).fetchone()[0]
                self.send_json({"total": total, "items": [{"chatId": row["chat_id"], "firstTimestamp": row["first_timestamp"], "lastTimestamp": row["last_timestamp"], "traceCount": row["trace_count"], "preview": row["preview"], "flagStatus": statuses.get(row["chat_id"])} for row in rows]})
                return
            if request.path.startswith("/api/conversations/"):
                chat_id = unquote(request.path.removeprefix("/api/conversations/"))
                with connect(index_path) as connection:
                    row = connection.execute("SELECT byte_offset, byte_length FROM conversations WHERE chat_id = ?", (chat_id,)).fetchone()
                if row is None:
                    self.send_json({"error": "conversation not found"}, HTTPStatus.NOT_FOUND)
                else:
                    chat = load_conversation(source, row["byte_offset"], row["byte_length"])
                    chat["flagStatus"] = self.flag_statuses().get(chat_id)
                    self.send_json(chat)
                return
            self.send_json({"error": "not found"}, HTTPStatus.NOT_FOUND)

        def do_POST(self) -> None:  # noqa: N802
            if urlparse(self.path).path != "/api/flags":
                self.send_json({"error": "not found"}, HTTPStatus.NOT_FOUND)
                return
            try:
                body = self.request_json()
                chat_id = str(body.get("chatId", ""))
                with connect(index_path) as connection:
                    exists = connection.execute("SELECT 1 FROM conversations WHERE chat_id = ?", (chat_id,)).fetchone() is not None
                record = create_case(chat_id=chat_id, category=str(body.get("category", "")),
                                     priority=str(body.get("priority", "")), assessment_source=str(body.get("assessmentSource", "")),
                                     review_note=str(body.get("reviewNote", "")), output_dir=flag_output, chat_exists=exists,
                                     human_confirmed=body.get("humanConfirmed") is True)
            except (ValueError, json.JSONDecodeError) as error:
                self.send_json({"error": str(error)}, HTTPStatus.BAD_REQUEST)
                return
            self.send_json({"caseId": record["caseId"], "chatId": record["chatId"], "status": record["status"], "priority": record["priority"]}, HTTPStatus.CREATED)

        def do_PUT(self) -> None:  # noqa: N802
            prefix = "/api/flags/"
            path = urlparse(self.path).path
            if not path.startswith(prefix) or not path.endswith("/status"):
                self.send_json({"error": "not found"}, HTTPStatus.NOT_FOUND)
                return
            chat_id = unquote(path[len(prefix):-len("/status")]).rstrip("/")
            try:
                body = self.request_json()
                event = change_case_status(chat_id=chat_id, status=str(body.get("status", "")),
                                           assessment_source=str(body.get("assessmentSource", "")),
                                           review_note=str(body.get("reviewNote", "")), output_dir=flag_output,
                                           human_confirmed=body.get("humanConfirmed") is True)
            except (ValueError, json.JSONDecodeError) as error:
                self.send_json({"error": str(error)}, HTTPStatus.BAD_REQUEST)
                return
            self.send_json({"eventId": event["eventId"], "chatId": event["chatId"], "status": event["status"]})

        def log_message(self, format: str, *args: object) -> None:
            return
    return Handler


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve a local read-only browser for conversations.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--index", type=Path, default=DEFAULT_INDEX)
    parser.add_argument("--rebuild-index", action="store_true")
    parser.add_argument("--build-index-only", action="store_true")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--flag-output-dir", type=Path, default=DEFAULT_FLAG_OUTPUT)
    args = parser.parse_args()
    count = build_index(args.input, args.index, args.rebuild_index)
    print(f"index ready: {count:,} conversations at {args.index}")
    if args.build_index_only:
        return
    server = ThreadingHTTPServer(("127.0.0.1", args.port), handler_factory(args.input, args.index, args.flag_output_dir))
    print(f"Conversation Browser: http://127.0.0.1:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
