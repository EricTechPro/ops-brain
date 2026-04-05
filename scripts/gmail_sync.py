#!/usr/bin/env python3
"""Gmail Sync — fetch emails/threads/labels from Gmail API as structured JSON.

Usage:
    python3 gmail_sync.py message <message_id> [--download-attachments <dir>]
    python3 gmail_sync.py thread <thread_id> [--download-attachments <dir>]
    python3 gmail_sync.py label <label_name> [--max-results N] [--download-attachments <dir>]
"""

import argparse
import base64
import json
import os
import sys
import time
from email.utils import parseaddr
from html.parser import HTMLParser
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent

# Load .env if present
_env_file = SCRIPT_DIR / ".env"
if _env_file.exists():
    for line in _env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, val = line.partition("=")
            os.environ.setdefault(key.strip(), val.strip())

CREDS_DIR = SCRIPT_DIR / ".gmail-credentials"
CREDENTIALS_FILE = Path(os.environ.get("GMAIL_CREDENTIALS_FILE", CREDS_DIR / "credentials.json"))
TOKEN_FILE = Path(os.environ.get("GMAIL_TOKEN_FILE", CREDS_DIR / "token.json"))
USER_EMAIL = os.environ.get("GMAIL_USER_EMAIL", "")

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.labels",
]

MAX_RETRIES = 3
BACKOFF_BASE = 2


# ---------------------------------------------------------------------------
# HTML → plain text
# ---------------------------------------------------------------------------
class _HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self._parts: list[str] = []
        self._skip = False

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._skip = True
        elif tag in ("br", "p", "div", "tr", "li"):
            self._parts.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self._skip = False

    def handle_data(self, data):
        if not self._skip:
            self._parts.append(data)

    def get_text(self) -> str:
        return "".join(self._parts).strip()


def html_to_text(html: str) -> str:
    stripper = _HTMLStripper()
    stripper.feed(html)
    return stripper.get_text()


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------
def authenticate():
    """Authenticate with Gmail API via OAuth2. Returns a service object."""
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except ImportError as e:
        _error(f"Missing dependency: {e}. Run: pip3 install -r scripts/requirements.txt")

    if not CREDENTIALS_FILE.exists():
        _error(
            f"credentials.json not found at {CREDENTIALS_FILE}\n"
            "Setup steps:\n"
            "1. Go to https://console.cloud.google.com/\n"
            "2. Enable the Gmail API\n"
            "3. Create OAuth2 credentials (Desktop app)\n"
            "4. Download the JSON and save it as:\n"
            f"   {CREDENTIALS_FILE}"
        )

    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                TOKEN_FILE.unlink(missing_ok=True)
                creds = None

        if not creds:
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)

        TOKEN_FILE.write_text(creds.to_json())

    return build("gmail", "v1", credentials=creds)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _error(msg: str):
    print(json.dumps({"error": msg}))
    sys.exit(1)


def _api_call(fn, *args, **kwargs):
    """Execute a Gmail API call with retry on rate-limit errors."""
    from googleapiclient.errors import HttpError

    for attempt in range(MAX_RETRIES):
        try:
            return fn(*args, **kwargs).execute()
        except HttpError as e:
            if e.resp.status == 429 and attempt < MAX_RETRIES - 1:
                wait = BACKOFF_BASE ** (attempt + 1)
                print(f"Rate limited, retrying in {wait}s...", file=sys.stderr)
                time.sleep(wait)
            elif e.resp.status == 404:
                _error(f"Not found: {e}")
            else:
                _error(f"Gmail API error: {e}")
    _error("Max retries exceeded due to rate limiting")


def _parse_header(headers: list[dict], name: str) -> str:
    for h in headers:
        if h["name"].lower() == name.lower():
            return h["value"]
    return ""


def _decode_body(payload: dict) -> tuple[str, str]:
    """Walk the MIME structure and return (plain_text, html_text)."""
    plain = ""
    html = ""

    def _walk(part):
        nonlocal plain, html
        mime = part.get("mimeType", "")
        if mime == "text/plain":
            data = part.get("body", {}).get("data", "")
            if data:
                plain += base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
        elif mime == "text/html":
            data = part.get("body", {}).get("data", "")
            if data:
                html += base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
        for sub in part.get("parts", []):
            _walk(sub)

    _walk(payload)
    return plain, html


def _collect_attachments(payload: dict) -> list[dict]:
    """Collect attachment metadata from the MIME structure."""
    attachments = []

    def _walk(part):
        filename = part.get("filename", "")
        body = part.get("body", {})
        att_id = body.get("attachmentId")
        if filename and att_id:
            attachments.append({
                "filename": filename,
                "mime_type": part.get("mimeType", "application/octet-stream"),
                "size": body.get("size", 0),
                "attachment_id": att_id,
            })
        for sub in part.get("parts", []):
            _walk(sub)

    _walk(payload)
    return attachments


# ---------------------------------------------------------------------------
# Core fetch functions
# ---------------------------------------------------------------------------
def download_attachment(service, message_id: str, attachment_id: str, filename: str, download_dir: str) -> str:
    """Download a single attachment and return the local path."""
    dest = Path(download_dir)
    dest.mkdir(parents=True, exist_ok=True)

    data = _api_call(
        service.users().messages().attachments().get,
        userId="me",
        messageId=message_id,
        id=attachment_id,
    )

    file_data = base64.urlsafe_b64decode(data["data"])
    stem = Path(filename).stem
    suffix = Path(filename).suffix
    file_path = dest / filename

    counter = 1
    while file_path.exists():
        file_path = dest / f"{stem}-{counter}{suffix}"
        counter += 1

    file_path.write_bytes(file_data)
    return str(file_path)


def _parse_message(service, msg: dict, download_dir: str | None = None) -> dict:
    """Parse a raw Gmail API message dict into structured data."""
    payload = msg.get("payload", {})
    headers = payload.get("headers", [])
    message_id = msg["id"]

    from_name, from_email = parseaddr(_parse_header(headers, "From"))

    to_raw = _parse_header(headers, "To")
    to_list = [addr.strip() for addr in to_raw.split(",") if addr.strip()]

    cc_raw = _parse_header(headers, "Cc")
    cc_list = [addr.strip() for addr in cc_raw.split(",") if addr.strip()] if cc_raw else []

    subject = _parse_header(headers, "Subject")
    date = _parse_header(headers, "Date")

    plain, html = _decode_body(payload)
    body = plain if plain else html_to_text(html)

    labels = msg.get("labelIds", [])

    attachments = _collect_attachments(payload)
    if download_dir:
        for att in attachments:
            try:
                att["local_path"] = download_attachment(
                    service, message_id, att["attachment_id"], att["filename"], download_dir
                )
            except Exception as e:
                att["download_error"] = str(e)
    for att in attachments:
        att.pop("attachment_id", None)

    direction = "sent" if (
        (USER_EMAIL and USER_EMAIL.lower() in from_email.lower()) or "SENT" in labels
    ) else "received"

    return {
        "id": message_id,
        "thread_id": msg["threadId"],
        "date": date,
        "from": from_email,
        "from_name": from_name,
        "to": to_list,
        "cc": cc_list,
        "subject": subject,
        "body": body,
        "direction": direction,
        "labels": labels,
        "attachments": attachments,
    }


def fetch_message(service, message_id: str, download_dir: str | None = None) -> dict:
    """Fetch a single message by ID."""
    msg = _api_call(
        service.users().messages().get,
        userId="me",
        id=message_id,
        format="full",
    )
    return _parse_message(service, msg, download_dir)


def fetch_thread(service, thread_id: str, download_dir: str | None = None) -> dict:
    """Fetch all messages in a thread (single API call)."""
    thread = _api_call(
        service.users().threads().get,
        userId="me",
        id=thread_id,
        format="full",
    )
    messages = [_parse_message(service, msg, download_dir) for msg in thread.get("messages", [])]
    return {
        "thread_id": thread_id,
        "subject": messages[0]["subject"] if messages else "",
        "message_count": len(messages),
        "messages": messages,
    }


def fetch_by_label(service, label_name: str, max_results: int = 50, download_dir: str | None = None) -> dict:
    """Fetch messages by Gmail label name."""
    # Resolve label name to ID
    labels_response = _api_call(service.users().labels().list, userId="me")
    label_id = None
    for label in labels_response.get("labels", []):
        if label["name"].lower() == label_name.lower():
            label_id = label["id"]
            break

    if not label_id:
        available = [l["name"] for l in labels_response.get("labels", [])]
        _error(f"Label '{label_name}' not found. Available labels: {', '.join(sorted(available))}")

    # List messages with this label
    response = _api_call(
        service.users().messages().list,
        userId="me",
        labelIds=[label_id],
        maxResults=max_results,
    )

    message_refs = response.get("messages", [])
    messages = []
    for ref in message_refs:
        msg_data = fetch_message(service, ref["id"], download_dir)
        messages.append(msg_data)

    return {
        "label": label_name,
        "label_id": label_id,
        "total_results": len(messages),
        "messages": messages,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Fetch Gmail data as JSON")
    subparsers = parser.add_subparsers(dest="mode", required=True)

    # message mode
    msg_parser = subparsers.add_parser("message", help="Fetch a single message")
    msg_parser.add_argument("id", help="Gmail message ID")
    msg_parser.add_argument("--download-attachments", dest="download_dir", help="Directory to save attachments")

    # thread mode
    thread_parser = subparsers.add_parser("thread", help="Fetch an entire thread")
    thread_parser.add_argument("id", help="Gmail thread ID")
    thread_parser.add_argument("--download-attachments", dest="download_dir", help="Directory to save attachments")

    # label mode
    label_parser = subparsers.add_parser("label", help="Fetch messages by label")
    label_parser.add_argument("name", help="Gmail label name")
    label_parser.add_argument("--max-results", type=int, default=50, help="Max messages to fetch (default: 50)")
    label_parser.add_argument("--download-attachments", dest="download_dir", help="Directory to save attachments")

    args = parser.parse_args()

    service = authenticate()

    if args.mode == "message":
        result = fetch_message(service, args.id, args.download_dir)
    elif args.mode == "thread":
        result = fetch_thread(service, args.id, args.download_dir)
    elif args.mode == "label":
        result = fetch_by_label(service, args.name, args.max_results, args.download_dir)
    else:
        _error(f"Unknown mode: {args.mode}")

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
