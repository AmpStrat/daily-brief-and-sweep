"""
Search the ASG mailbox by IMAP header criteria (From/To/Subject/Text), not just
by date. Complements imap_search_recent.py, which only supports date windows.

Usage:
  python execution/imap_search_query.py --from-addr bryan.zymanek@broan.com --folder INBOX
  python execution/imap_search_query.py --text "Banchik" --folder INBOX
  python execution/imap_search_query.py --from-addr x@y.com --since-days 90

Prints a JSON array of message summaries (same shape as imap_search_recent.py).
"""

import argparse
import email
import email.header
import json
import sys
from datetime import datetime, timedelta

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


def decode_snippet(msg: email.message.Message, max_len: int = 400) -> str:
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--from-addr", default=None)
    parser.add_argument("--to-addr", default=None)
    parser.add_argument("--text", default=None, help="Search body+subject text")
    parser.add_argument("--since-days", type=int, default=90)
    parser.add_argument("--folder", default="INBOX")
    args = parser.parse_args()

    if not any([args.from_addr, args.to_addr, args.text]):
        sys.exit("Provide at least one of --from-addr, --to-addr, --text")

    cutoff = datetime.now() - timedelta(days=args.since_days)
    since_date = cutoff.strftime("%d-%b-%Y")

    criteria = ["SINCE", since_date]
    if args.from_addr:
        criteria += ["FROM", args.from_addr]
    if args.to_addr:
        criteria += ["TO", args.to_addr]
    if args.text:
        criteria += ["TEXT", args.text]

    conn = connect()
    conn.select(args.folder, readonly=True)
    status, data = conn.uid("search", None, "(" + " ".join(f'"{c}"' if " " in c else c for c in criteria) + ")")
    if status != "OK" or not data[0]:
        conn.logout()
        print(json.dumps([]))
        return

    uids = data[0].split()
    results = []
    for raw_uid in sorted(uids, key=int):
        uid_str = raw_uid.decode() if isinstance(raw_uid, bytes) else str(raw_uid)
        status, msg_data = conn.uid("fetch", uid_str, "(RFC822)")
        if status != "OK" or not msg_data or msg_data[0] is None:
            continue
        msg = email.message_from_bytes(msg_data[0][1])
        results.append(
            {
                "uid": uid_str,
                "folder": args.folder,
                "from": decode_mime_header(msg.get("From", "")),
                "to": decode_mime_header(msg.get("To", "")),
                "subject": decode_mime_header(msg.get("Subject", "")),
                "date": msg.get("Date", ""),
                "message_id": msg.get("Message-ID", ""),
                "in_reply_to": msg.get("In-Reply-To", ""),
                "snippet": decode_snippet(msg),
            }
        )
    conn.logout()
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
