"""Fetch unread emails from the last 24 hours via Gmail API."""

import requests
import config

TOKEN_URL = "https://oauth2.googleapis.com/token"
GMAIL_API = "https://gmail.googleapis.com/gmail/v1/users/me"


def _get_access_token() -> str:
    """Exchange the refresh token for a fresh access token."""
    resp = requests.post(TOKEN_URL, data={
        "client_id": config.GOOGLE_CLIENT_ID,
        "client_secret": config.GOOGLE_CLIENT_SECRET,
        "refresh_token": config.GOOGLE_REFRESH_TOKEN,
        "grant_type": "refresh_token",
    }, timeout=10)
    resp.raise_for_status()
    return resp.json()["access_token"]


def fetch_emails() -> list[dict]:
    """Fetch unread emails from the last 24 hours.

    Returns a list of dicts with keys: sender, subject, snippet.
    """
    if not all([config.GOOGLE_CLIENT_ID, config.GOOGLE_CLIENT_SECRET,
                config.GOOGLE_REFRESH_TOKEN]):
        return [{"error": "Gmail credentials not configured"}]

    try:
        token = _get_access_token()
    except requests.RequestException as e:
        return [{"error": f"Gmail auth failed: {e}"}]

    headers = {"Authorization": f"Bearer {token}"}

    # Search for unread emails from the last 24 hours
    query = "is:unread newer_than:1d"
    try:
        list_resp = requests.get(
            f"{GMAIL_API}/messages",
            headers=headers,
            params={"q": query, "maxResults": 10},
            timeout=10,
        )
        list_resp.raise_for_status()
        list_data = list_resp.json()
    except requests.RequestException as e:
        return [{"error": f"Gmail list failed: {e}"}]

    messages = list_data.get("messages", [])
    if not messages:
        return []

    results = []
    for msg in messages:
        try:
            detail_resp = requests.get(
                f"{GMAIL_API}/messages/{msg['id']}",
                headers=headers,
                params={"format": "metadata", "metadataHeaders": ["From", "Subject"]},
                timeout=10,
            )
            detail_resp.raise_for_status()
            detail = detail_resp.json()
        except requests.RequestException:
            continue

        headers_list = detail.get("payload", {}).get("headers", [])
        sender = ""
        subject = ""
        for h in headers_list:
            if h["name"] == "From":
                sender = h["value"]
            elif h["name"] == "Subject":
                subject = h["value"]

        results.append({
            "sender": sender,
            "subject": subject,
            "snippet": detail.get("snippet", ""),
        })

    return results


def format_emails(emails: list[dict]) -> str:
    """Format email data into a briefing-friendly string."""
    if not emails:
        return "📧 EMAIL\nNo unread emails in the last 24h."

    if "error" in emails[0]:
        return f"⚠️ Email unavailable: {emails[0]['error']}"

    lines = [f"📧 EMAIL ({len(emails)} unread)"]
    for e in emails:
        # Trim sender to just the name if possible (e.g. "Name <addr>" → "Name")
        sender = e["sender"]
        if "<" in sender:
            sender = sender.split("<")[0].strip().strip('"')
        lines.append(f"• {sender}: {e['subject']}")

    return "\n".join(lines)
