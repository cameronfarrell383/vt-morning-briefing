import requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import config


def fetch_canvas_assignments() -> list[dict]:
    """Fetch assignments due in the next 7 days from Canvas."""
    token = config.CANVAS_API_TOKEN
    base = config.CANVAS_BASE_URL.rstrip("/")
    tz = ZoneInfo(config.TIMEZONE)

    if not token:
        return [{"error": "CANVAS_API_TOKEN not set"}]

    headers = {"Authorization": f"Bearer {token}"}
    now = datetime.now(tz)
    cutoff = now + timedelta(days=7)

    try:
        # Get active courses
        courses_resp = requests.get(
            f"{base}/api/v1/courses",
            headers=headers,
            params={"enrollment_state": "active", "per_page": 50},
            timeout=10,
        )
        courses_resp.raise_for_status()
        courses = courses_resp.json()
    except requests.RequestException as e:
        return [{"error": f"Failed to fetch courses: {e}"}]

    course_map = {c["id"]: c.get("name", "Unknown Course") for c in courses}
    assignments = []

    for course_id, course_name in course_map.items():
        try:
            resp = requests.get(
                f"{base}/api/v1/courses/{course_id}/assignments",
                headers=headers,
                params={
                    "bucket": "upcoming",
                    "order_by": "due_at",
                    "per_page": 50,
                },
                timeout=10,
            )
            resp.raise_for_status()
            for a in resp.json():
                due = a.get("due_at")
                if not due:
                    continue
                due_dt = datetime.fromisoformat(due.replace("Z", "+00:00")).astimezone(tz)
                if now <= due_dt <= cutoff:
                    assignments.append({
                        "course": course_name,
                        "name": a["name"],
                        "due": due_dt,
                    })
        except requests.RequestException:
            continue

    assignments.sort(key=lambda a: a["due"])
    return assignments


def format_canvas(assignments: list[dict]) -> str:
    """Format Canvas assignments into a briefing-friendly string."""
    if not assignments:
        return "📚 CANVAS\nNo assignments due in the next 7 days."

    if "error" in assignments[0]:
        return f"⚠️ Canvas unavailable: {assignments[0]['error']}"

    lines = ["📚 CANVAS"]
    for a in assignments:
        due_str = a["due"].strftime("%a %b %d %I:%M %p")
        lines.append(f"• {a['course']}: {a['name']} — due {due_str}")
    return "\n".join(lines)
