"""VT Morning Briefing — AI-summarized daily digest."""

from fetchers.weather import fetch_weather
from fetchers.gmail import fetch_emails
from fetchers.canvas import fetch_canvas_assignments
from summarizer import summarize
from messenger import send_telegram


def build_briefing() -> str:
    """Fetch all data sources and produce an AI-summarized briefing."""
    weather = fetch_weather()
    emails = fetch_emails()
    canvas = fetch_canvas_assignments()

    return summarize(weather, emails, canvas)


def main():
    print("Building morning briefing...")
    message = build_briefing()
    print(f"\n--- Briefing ---\n{message}\n--- End ---\n")

    print("Sending Telegram message...")
    result = send_telegram(message)
    msg_id = result["result"]["message_id"]
    print(f"Telegram message sent! ID: {msg_id}")


if __name__ == "__main__":
    main()
