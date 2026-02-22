"""Fetch incomplete reminders from iCloud via CalDAV."""

import caldav
import vobject
from datetime import datetime
from zoneinfo import ZoneInfo

import config

ICLOUD_CALDAV_URL = "https://caldav.icloud.com/"

# iCloud upgrade stubs — not real reminders
_UPGRADE_KEYWORDS = {"upgraded these reminders", "where are my reminders"}


def fetch_reminders() -> list[dict]:
    """Connect to iCloud CalDAV and return incomplete reminders."""
    username = config.ICLOUD_USERNAME
    password = config.ICLOUD_APP_PASSWORD

    if not username or not password:
        return [{"error": "ICLOUD_USERNAME or ICLOUD_APP_PASSWORD not set"}]

    tz = ZoneInfo(config.TIMEZONE)

    try:
        client = caldav.DAVClient(
            url=ICLOUD_CALDAV_URL,
            username=username,
            password=password,
        )
        principal = client.principal()
        calendars = principal.calendars()
    except Exception as e:
        return [{"error": f"Failed to connect to iCloud CalDAV: {e}"}]

    reminders = []

    for cal in calendars:
        # iCloud returns 500 on cal.todos() REPORT, so iterate objects instead
        try:
            objs = list(cal.objects())
        except Exception:
            continue

        if not objs:
            continue

        # Sample first object to skip event-only calendars (avoids loading
        # hundreds of VEVENTs from large calendars like shared Family ones)
        try:
            objs[0].load()
            if objs[0].data and "VEVENT" in objs[0].data:
                continue
        except Exception:
            pass

        for obj in objs:
            try:
                if not obj.data:
                    obj.load()
                if not obj.data or "VTODO" not in obj.data:
                    continue

                parsed = vobject.readOne(obj.data)
                if not hasattr(parsed, "vtodo"):
                    continue
                vtodo = parsed.vtodo

                # Skip completed
                if hasattr(vtodo, "status") and str(vtodo.status.value).upper() == "COMPLETED":
                    continue
                if hasattr(vtodo, "completed"):
                    continue

                name = str(vtodo.summary.value) if hasattr(vtodo, "summary") else "Untitled"

                # Skip iCloud upgrade notice stubs
                if any(kw in name.lower() for kw in _UPGRADE_KEYWORDS):
                    continue

                due = None
                if hasattr(vtodo, "due"):
                    raw = vtodo.due.value
                    if isinstance(raw, datetime):
                        due = raw.astimezone(tz)
                    else:
                        # date-only value
                        due = datetime(raw.year, raw.month, raw.day, tzinfo=tz)

                reminders.append({"name": name, "due": due})
            except Exception:
                continue

    reminders.sort(key=lambda r: (r["due"] is None, r["due"] or datetime.max.replace(tzinfo=tz)))
    return reminders


def format_reminders(reminders: list[dict]) -> str:
    """Format reminders into a briefing-friendly string."""
    if not reminders:
        return "✅ REMINDERS\nNo incomplete reminders."

    if "error" in reminders[0]:
        return f"⚠️ Reminders unavailable: {reminders[0]['error']}"

    lines = ["✅ REMINDERS"]
    for r in reminders:
        if r["due"]:
            due_str = r["due"].strftime("%a %b %d %I:%M %p")
            lines.append(f"• {r['name']} — due {due_str}")
        else:
            lines.append(f"• {r['name']}")
    return "\n".join(lines)
