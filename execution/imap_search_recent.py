"""
Search the ASG mailbox for recent messages. Replaces the gmail_search_messages
step from the original Gmail-based skill.

Plain IMAP's SEARCH SINCE only has day granularity (no hours), so this searches
a generously wide date window server-side, then filters precisely by the parsed
Date header client-side. It also pulls in anything UNSEEN or FLAGGED regardless
of date, to catch anything that might otherwise be missed (mirrors the original
skill's "starred is:unread" secondary search).

Usage:
  python execution/imap_search_recent.py --since-hours 9 [--folder INBOX]

Prints a JSON array of message summaries to stdout, one per message:
  {uid, folder, from, to, delivered_to, x_original_to, subject, date, message_id,
   in_reply_to, references, snippet}

`to` is the message's own To: header — for genuine redirect-style forwarding this
still shows the original address (e.g. dawn.garibaldi@talentgrowthpartners.com)
rather than the ASG mailbox it landed in. `delivered_to`/`x_original_to` are a
fallback for forwarding setups that rewrite To: — not every mail server sets
these, so they may be empty even on legitimately forwarded mail.
"""

import argparse
import email
import email.header
import email.utils
import json
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from imap_common import connect


def decode_mime_header(value: str) -> str:
    if not value:
        return value
    parts = email.header.decode_header(value)
    decoded = ""
    for text, charset in parts:
        if isinstance(text, bytes):
            decoded += text.decode(charset or "utf-8", errors="replace")
        else:
            decoded += text
    return decoded


def decode_snippet(msg: email.message.Message, max_len: int = 300) -> str:
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain" and not part.get_filename():
                try:
                    body = part.get_payload(decode=True).decode(
                        part.get_content_charset() or "utf-8", errors="replace"
                    )
                except Exception:
                    continue
                break
    else:
        try:
            body = msg.get_payload(decode=True).decode(
                msg.get_content_charset() or "utf-8", errors="replace"
            )
        except Exception:
            body = ""
    body = " ".join(body.split())
    return body[:max_len]


def fetch_summaries(conn, folder: str, uids: set) -> list[dict]:
    results = []
    for raw_uid in sorted(uids, key=int):
        uid_str = raw_uid.decode() if isinstance(raw_uid, bytes) else str(raw_uid)
        status, data = conn.uid("fetch", uid_str, "(RFC822)")
        if status != "OK" or not data or data[0] is None:
            continue
        raw = data[0][1]
        msg = email.message_from_bytes(raw)
        results.append(
            {
                "uid": uid_str,
                "folder": folder,
                "from": decode_mime_header(msg.get("From", "")),
                "to": decode_mime_header(msg.get("To", "")),
                "delivered_to": decode_mime_header(msg.get("Delivered-To", "")),
                "x_original_to": decode_mime_header(msg.get("X-Original-To", "")),
                "subject": decode_mime_header(msg.get("Subject", "")),
                "date": msg.get("Date", ""),
                "message_id": msg.get("Message-ID", ""),
                "in_reply_to": msg.get("In-Reply-To", ""),
                "references": msg.get("References", ""),
                "snippet": decode_snippet(msg),
            }
        )
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--since-hours", type=float, default=9)
    parser.add_argument("--folder", default="INBOX")
    args = parser.parse_args()

    cutoff = datetime.now(timezone.utc) - timedelta(hours=args.since_hours)
    # IMAP SINCE is day-granularity only — widen by a day to be safe, then filter precisely below.
    imap_since_date = (cutoff - timedelta(days=1)).strftime("%d-%b-%Y")

    conn = connect()
    conn.select(args.folder, readonly=True)

    uids = set()

    status, data = conn.uid("search", None, f"(SINCE {imap_since_date})")
    if status == "OK" and data[0]:
        uids.update(data[0].split())

    # UNSEEN/FLAGGED are bounded by the same date window — otherwise an inbox with
    # years of unread cold-pitch mail would return everything on every run.
    status, data = conn.uid("search", None, f"(SINCE {imap_since_date} UNSEEN)")
    if status == "OK" and data[0]:
        uids.update(data[0].split())

    status, data = conn.uid("search", None, f"(SINCE {imap_since_date} FLAGGED)")
    if status == "OK" and data[0]:
        uids.update(data[0].split())

    summaries = fetch_summaries(conn, args.folder, uids)
    conn.logout()

    filtered = []
    for msg in summaries:
        try:
            parsed_date = email.utils.parsedate_to_datetime(msg["date"])
            if parsed_date.tzinfo is None:
                parsed_date = parsed_date.replace(tzinfo=timezone.utc)
        except (TypeError, ValueError):
            filtered.append(msg)
            continue
        if parsed_date >= cutoff:
            filtered.append(msg)

    print(json.dumps(filtered, indent=2))


if __name__ == "__main__":
    main()
