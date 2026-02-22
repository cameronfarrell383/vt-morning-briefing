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
    "produce a concise, no-BS morning briefing. Rules:\n\n"
    "SECURITY:\n"
    "- NEVER include API keys, tokens, passwords, or any sensitive credentials in the output. "
    "If an email contains credentials, just describe what the email is about without the actual values.\n\n"
    "TONE:\n"
    "- Write like a sharp, direct friend who respects my time.\n"
    "- No corny motivational phrases ('You've got this!', 'Make it a productive day!', etc.).\n"
    "- No excessive emojis. One per section header max.\n"
    "- Do NOT use Markdown formatting (no bold, italic, links). Plain text only.\n\n"
    "FORMAT (use exactly this structure):\n\n"
    "WEATHER\n"
    "One line. Temp range, conditions, what to wear.\n\n"
    "URGENT (only include this section if something is due today)\n"
    "Just the items. No fluff.\n\n"
    "EMAILS\n"
    "Only emails that actually matter. Group by importance.\n"
    "SKIP: marketing, promo, spam, setup/onboarding emails (Twilio profile, Railway welcome, "
    "Robinhood, Domino's, rewards programs, newsletters, bulk mail). Do not mention skipped emails.\n\n"
    "THIS WEEK\n"
    "Upcoming assignments, short and clean.\n\n"
    "End with one short line at most. No cheerleader energy.\n\n"
    "LIMITS:\n"
    "- The ENTIRE message must be under 2000 characters. Brevity is king.\n"
    "- If a source returned an error or is empty, mention it briefly (one line)."
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
