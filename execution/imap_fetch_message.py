"""
Fetch the full body of a single message by UID. Replaces gmail_read_thread from
the original Gmail-based skill.

Plain IMAP doesn't have Gmail-style threads. This fetches one message at a time;
use the References/In-Reply-To headers from imap_search_recent.py's output to
identify related messages and fetch each one if you need the full back-and-forth.

Usage:
  python execution/imap_fetch_message.py --uid 2784594 [--folder INBOX]

Prints JSON: {uid, folder, from, to, delivered_to, x_original_to, cc, subject,
date, message_id, in_reply_to, references, body}

`to` is the message's own To: header — for genuine redirect-style forwarding this
still shows the original address (e.g. dawn.garibaldi@talentgrowthpartners.com)
rather than the ASG mailbox it landed in. `delivered_to`/`x_original_to` are a
fallback for forwarding setups that rewrite To: — may be empty even on
legitimately forwarded mail if the sending server doesn't set them.
"""

import argparse
import email
import email.header
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
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


def extract_body(msg: email.message.Message) -> str:
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain" and not part.get_filename():
                try:
                    return part.get_payload(decode=True).decode(
                        part.get_content_charset() or "utf-8", errors="replace"
                    )
                except Exception:
                    continue
        # Fall back to HTML if no plain-text part exists.
        for part in msg.walk():
            if part.get_content_type() == "text/html" and not part.get_filename():
                try:
                    return part.get_payload(decode=True).decode(
                        part.get_content_charset() or "utf-8", errors="replace"
                    )
                except Exception:
                    continue
        return ""
    try:
        return msg.get_payload(decode=True).decode(
            msg.get_content_charset() or "utf-8", errors="replace"
        )
    except Exception:
        return ""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--uid", required=True)
    parser.add_argument("--folder", default="INBOX")
    args = parser.parse_args()

    conn = connect()
    conn.select(args.folder, readonly=True)
    status, data = conn.uid("fetch", args.uid, "(RFC822)")
    conn.logout()

    if status != "OK" or not data or data[0] is None:
        sys.exit(f"Could not fetch UID {args.uid} in folder {args.folder}")

    msg = email.message_from_bytes(data[0][1])
    result = {
        "uid": args.uid,
        "folder": args.folder,
        "from": decode_mime_header(msg.get("From", "")),
        "to": decode_mime_header(msg.get("To", "")),
        "delivered_to": decode_mime_header(msg.get("Delivered-To", "")),
        "x_original_to": decode_mime_header(msg.get("X-Original-To", "")),
        "cc": decode_mime_header(msg.get("Cc", "")),
        "subject": decode_mime_header(msg.get("Subject", "")),
        "date": msg.get("Date", ""),
        "message_id": msg.get("Message-ID", ""),
        "in_reply_to": msg.get("In-Reply-To", ""),
        "references": msg.get("References", ""),
        "body": extract_body(msg),
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
