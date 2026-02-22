import os
from dotenv import load_dotenv

load_dotenv()

# Weather
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
LOCATION_LAT = os.getenv("LOCATION_LAT", "37.2296")
LOCATION_LON = os.getenv("LOCATION_LON", "-80.4139")
LOCATION_NAME = os.getenv("LOCATION_NAME", "Blacksburg, VA")

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Outlook (IMAP)
OUTLOOK_EMAIL = os.getenv("OUTLOOK_EMAIL")
OUTLOOK_PASSWORD = os.getenv("OUTLOOK_PASSWORD")

# Gmail
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REFRESH_TOKEN = os.getenv("GOOGLE_REFRESH_TOKEN")

# Canvas
CANVAS_API_TOKEN = os.getenv("CANVAS_API_TOKEN")
CANVAS_BASE_URL = os.getenv("CANVAS_BASE_URL", "https://canvas.vt.edu")

# iCloud (CalDAV Reminders)
ICLOUD_USERNAME = os.getenv("ICLOUD_USERNAME")
ICLOUD_APP_PASSWORD = os.getenv("ICLOUD_APP_PASSWORD")

# Anthropic (Claude API)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Timezone
TIMEZONE = os.getenv("TIMEZONE", "America/New_York")
