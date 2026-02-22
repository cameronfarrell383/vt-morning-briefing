"""Send raw briefing data to Claude for a concise, prioritized summary."""

import json
from datetime import datetime

import anthropic

import config


def _serialize_data(weather, emails, canvas) -> str:
    """Convert raw fetcher outputs to a JSON string for the prompt."""

    def _default(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Not serializable: {type(obj)}")

    blob = {
        "weather": weather,
        "gmail": emails,
        "canvas": canvas,
    }
    return json.dumps(blob, default=_default, indent=2)


SYSTEM_PROMPT = (
    "You are a personal morning-briefing assistant for a Virginia Tech student. "
    "Given raw data from several sources (weather, Gmail, Canvas), "
    "produce a concise, prioritized morning briefing. Rules:\n"
    "- Start with a friendly one-line greeting that includes today's date.\n"
    "- Lead with the most time-sensitive items (assignments due today, urgent emails).\n"
    "- Then weather, then remaining emails grouped logically.\n"
    "- FILTER EMAILS: Only include emails that actually need attention — school-related, "
    "personal messages, important account alerts (security, billing, etc.). "
    "SKIP marketing, promotional, and spam emails entirely (e.g. food deals, retail promos, "
    "airline promotions, app newsletters, Robinhood, Domino's, rewards programs, unsubscribe-type bulk mail). "
    "Do not mention skipped emails at all.\n"
    "- Use short bullet points and emojis sparingly for scannability.\n"
    "- If a source returned an error or is empty, mention it briefly (one line).\n"
    "- The ENTIRE message must be under 4000 characters (Telegram limit).\n"
    "- Do NOT use Markdown formatting (no bold, italic, links). Plain text and emojis only.\n"
    "- End with a short motivational sign-off."
)


def summarize(weather, emails, canvas) -> str:
    """Call Claude to summarize raw briefing data into a Telegram-ready message."""
    raw = _serialize_data(weather, emails, canvas)

    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Today is {datetime.now().strftime('%A, %B %d, %Y')}. "
                    f"Here is the raw briefing data:\n\n{raw}\n\n"
                    "Write the morning briefing now."
                ),
            }
        ],
    )

    return response.content[0].text
