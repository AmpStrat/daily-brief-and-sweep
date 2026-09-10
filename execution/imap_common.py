"""
Shared IMAP connection + credential loading for the ASG mailbox
(d.garibaldi@amplifystrategy.com, hosted on privateemail.com).

Credentials live outside the project folder at
C:\\Users\\dmgar\\.secrets\\Email_Triage\\.env — kept off the Obsidian-synced path.

NOTE: privateemail.com's "Application Passwords" feature doesn't document which
dropdown type (Drive Sync App / Calendar Client / Backup Client / etc.) grants
IMAP access. Empirically confirmed on 2026-07-18: the "Backup Client" type works.
If auth ever starts failing, that's the first thing to re-verify — Namecheap may
have changed the scoping.
"""

import imaplib
import sys
from pathlib import Path

ENV_PATH = Path.home() / ".secrets" / "Email_Triage" / ".env"
IMAP_HOST = "mail.privateemail.com"
IMAP_PORT = 993
SMTP_HOST = "mail.privateemail.com"
SMTP_PORT = 587


def load_env(path: Path = ENV_PATH) -> dict:
    if not path.exists():
        sys.exit(f"Missing .env file at {path}")
    values = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        values[key.strip()] = value.strip()
    return values


def get_credentials() -> tuple[str, str]:
    env = load_env()
    address = env.get("PRIVATEEMAIL_ADDRESS")
    password = env.get("PRIVATEEMAIL_APP_PASSWORD")
    if not address or not password:
        sys.exit(
            "PRIVATEEMAIL_ADDRESS and/or PRIVATEEMAIL_APP_PASSWORD are not set in "
            f"{ENV_PATH}."
        )
    return address, password


def connect() -> imaplib.IMAP4_SSL:
    """Returns an authenticated IMAP connection. Caller is responsible for logout()."""
    address, password = get_credentials()
    conn = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
    conn.login(address, password)
    return conn
