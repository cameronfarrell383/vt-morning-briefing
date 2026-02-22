"""Fetch unread emails from the last 24 hours via Outlook IMAP."""

import imaplib
import email
import email.header
from datetime import datetime, timedelta, timezone

import config

IMAP_HOST = "outlook.office365.com"
IMAP_PORT = 993


def _decode_header(raw: str) -> str:
    """Decode an RFC 2047 encoded header into a plain string."""
    parts = email.header.decode_header(raw)
    decoded = []
    for data, charset in parts:
        if isinstance(data, bytes):
            decoded.append(data.decode(charset or "utf-8", errors="replace"))
        else:
            decoded.append(data)
    return "".join(decoded)


def _extract_snippet(msg: email.message.Message, max_len: int = 120) -> str:
    """Extract a plain-text snippet from the email body."""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                payload = part.get_payload(decode=True)
                if payload:
                    text = payload.decode(part.get_content_charset() or "utf-8", errors="replace")
                    snippet = " ".join(text.split())
                    return snippet[:max_len]
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            charset = msg.get_content_charset() or "utf-8"
            text = payload.decode(charset, errors="replace")
            snippet = " ".join(text.split())
            return snippet[:max_len]
    return ""


def fetch_outlook_emails() -> list[dict]:
    """Fetch unread emails from the last 24 hours via IMAP.

    Returns a list of dicts with keys: sender, subject, snippet.
    """
    if not all([config.OUTLOOK_EMAIL, config.OUTLOOK_PASSWORD]):
        return [{"error": "Outlook credentials not configured"}]

    # IMAP SINCE date filter (date only, no time)
    since_date = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%d-%b-%Y")

    try:
        conn = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
        conn.login(config.OUTLOOK_EMAIL, config.OUTLOOK_PASSWORD)
        conn.select("INBOX", readonly=True)

        # Search for unseen messages since yesterday
        status, msg_ids = conn.search(None, f'(UNSEEN SINCE {since_date})')
        if status != "OK" or not msg_ids[0]:
            conn.logout()
            return []

        ids = msg_ids[0].split()
        # Cap at 10 most recent
        ids = ids[-10:]

        results = []
        for mid in ids:
            status, data = conn.fetch(mid, "(RFC822)")
            if status != "OK":
                continue
            raw = data[0][1]
            msg = email.message_from_bytes(raw)

            sender = _decode_header(msg.get("From", ""))
            subject = _decode_header(msg.get("Subject", "(no subject)"))
            snippet = _extract_snippet(msg)

            results.append({
                "sender": sender,
                "subject": subject,
                "snippet": snippet,
            })

        conn.logout()
        return results

    except imaplib.IMAP4.error as e:
        return [{"error": f"Outlook IMAP error: {e}"}]
    except Exception as e:
        return [{"error": f"Outlook fetch failed: {e}"}]


def format_outlook_emails(emails: list[dict]) -> str:
    """Format Outlook email data into a briefing-friendly string."""
    if not emails:
        return "📬 OUTLOOK\nNo unread emails in the last 24h."

    if "error" in emails[0]:
        return f"⚠️ Outlook unavailable: {emails[0]['error']}"

    lines = [f"📬 OUTLOOK ({len(emails)} unread)"]
    for e in emails:
        sender = e["sender"]
        if "<" in sender:
            sender = sender.split("<")[0].strip().strip('"')
        lines.append(f"• {sender}: {e['subject']}")

    return "\n".join(lines)
