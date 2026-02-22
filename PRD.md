# Product Requirements Document (PRD)
# VT Morning Briefing — Personal Assistant

**Version:** 1.0
**Author:** Claude (via Claude Code)
**Date:** February 21, 2026
**Status:** Ready for Development

---

## 1. Overview

**VT Morning Briefing** is a personal assistant that runs autonomously in the cloud and sends a single, consolidated SMS to your phone every morning at 7:00 AM ET. The message contains a summary of your weather, emails, homework assignments, and reminders — everything you need to start your day.

### 1.1 Goals

- Wake up to one text message that tells you everything you need to know
- Zero manual effort — fully automated, runs without your computer
- AI-summarized so it's concise and actionable, not a wall of text

### 1.2 Non-Goals

- This is NOT a chatbot — it's a one-way daily briefing
- No WhatsApp integration (no official API available)
- No real-time notifications — this is a once-daily digest

---

## 2. Architecture

```
┌─────────────────────────────────────┐
│        Railway (Cloud Host)         │
│                                     │
│   Cron Trigger: 7:00 AM ET Daily    │
│              │                      │
│              ▼                      │
│   ┌─────────────────────┐           │
│   │  Data Fetchers       │           │
│   │  ├─ Weather (OWM)    │           │
│   │  ├─ Gmail (Google)   │           │
│   │  ├─ Outlook (MSFT)   │           │
│   │  ├─ Canvas (REST)    │           │
│   │  └─ Reminders (iCld) │           │
│   └─────────┬───────────┘           │
│             │                       │
│             ▼                       │
│   ┌─────────────────────┐           │
│   │  Claude API          │           │
│   │  (Summarize &        │           │
│   │   Prioritize)        │           │
│   └─────────┬───────────┘           │
│             │                       │
│             ▼                       │
│   ┌─────────────────────┐           │
│   │  Twilio SMS          │           │
│   │  (Send to phone)     │           │
│   └─────────────────────┘           │
└─────────────────────────────────────┘
```

### 2.1 Tech Stack

| Component        | Technology                     |
|-----------------|--------------------------------|
| Language         | Python 3.11+                  |
| Cloud Host       | Railway ($5/mo)               |
| Scheduler        | Railway Cron / APScheduler    |
| AI Summarizer    | Claude API (Sonnet 4)         |
| SMS Delivery     | Twilio                         |
| Email (Gmail)    | Google Gmail API (OAuth 2.0)  |
| Email (Outlook)  | Microsoft Graph API (OAuth 2.0)|
| Homework         | Canvas LMS REST API            |
| Weather          | OpenWeatherMap API (free tier) |
| Reminders        | iCloud CalDAV                  |
| Config/Secrets   | Environment variables          |

---

## 3. Data Sources — Detailed Specs

### 3.1 Weather

- **API:** OpenWeatherMap One Call API (free tier — 1,000 calls/day)
- **Data Needed:** Current temp, high/low, conditions, precipitation chance
- **Location:** Blacksburg, VA (37.2296, -80.4139)
- **Setup:**
  1. Create free account at [openweathermap.org](https://openweathermap.org)
  2. Generate API key
  3. Store as `OPENWEATHER_API_KEY` env variable

### 3.2 Gmail

- **API:** Google Gmail API v1
- **Auth:** OAuth 2.0 with offline refresh token
- **Data Needed:** Unread emails from last 24 hours — sender, subject, snippet
- **Scope:** `gmail.readonly`
- **Setup:**
  1. Go to [Google Cloud Console](https://console.cloud.google.com)
  2. Create a new project (e.g., "VT Morning Briefing")
  3. Enable the Gmail API
  4. Create OAuth 2.0 credentials (Desktop app type)
  5. Download `credentials.json`
  6. Run the auth flow once locally to generate a refresh token
  7. Store `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REFRESH_TOKEN` as env variables

### 3.3 Outlook

- **API:** Microsoft Graph API v1.0
- **Auth:** OAuth 2.0 with refresh token (MSAL library)
- **Endpoint:** `GET /me/mailFolders/inbox/messages?$filter=isRead eq false`
- **Data Needed:** Unread emails from last 24 hours — sender, subject, preview
- **Setup:**
  1. Go to [Azure Portal → App Registrations](https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps)
  2. Register a new app
  3. Add redirect URI: `http://localhost:8000/callback`
  4. Under API Permissions, add `Mail.Read` (delegated)
  5. Create a client secret
  6. Run auth flow once locally to get refresh token
  7. Store `OUTLOOK_CLIENT_ID`, `OUTLOOK_CLIENT_SECRET`, `OUTLOOK_REFRESH_TOKEN`, `OUTLOOK_TENANT_ID` as env variables

### 3.4 Canvas (Virginia Tech)

- **API:** Canvas LMS REST API
- **Base URL:** `https://canvas.vt.edu/api/v1`
- **Auth:** Personal Access Token (no OAuth needed — much simpler)
- **Data Needed:**
  - Upcoming assignments (next 7 days): name, course, due date, points
  - Any new announcements from today
- **Endpoints:**
  - `GET /api/v1/users/self/upcoming_events`
  - `GET /api/v1/courses?enrollment_state=active`
  - `GET /api/v1/courses/:id/assignments?bucket=upcoming`
- **Setup:**
  1. Log in to [canvas.vt.edu](https://canvas.vt.edu)
  2. Go to Account → Settings → New Access Token
  3. Generate a token with no expiry (or set a long expiry)
  4. Store as `CANVAS_API_TOKEN` env variable
  5. Store `CANVAS_BASE_URL=https://canvas.vt.edu` as env variable

### 3.5 iPhone Reminders (via iCloud CalDAV)

- **Protocol:** CalDAV over HTTPS
- **Library:** `caldav` Python package
- **Auth:** Apple ID + App-Specific Password
- **Data Needed:** All incomplete reminders, sorted by due date
- **Setup:**
  1. Go to [appleid.apple.com](https://appleid.apple.com) → Security → App-Specific Passwords
  2. Generate a password (label it "VT Briefing")
  3. Store `ICLOUD_USERNAME` (your Apple ID email) and `ICLOUD_APP_PASSWORD` as env variables
  4. CalDAV endpoint: `https://caldav.icloud.com`

### 3.6 Twilio SMS

- **API:** Twilio Programmable Messaging
- **Cost:** ~$1.50/mo for a phone number + $0.0079/SMS (essentially free at 1 msg/day)
- **Setup:**
  1. Create account at [twilio.com](https://www.twilio.com)
  2. Get a phone number (free trial gives you one)
  3. Note your Account SID, Auth Token, and Twilio phone number
  4. Store as `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER` env variables
  5. Store your personal phone number as `MY_PHONE_NUMBER`

### 3.7 Claude API (Summarizer)

- **API:** Anthropic Messages API
- **Model:** claude-sonnet-4-5-20250929 (fast, cheap, great at summarization)
- **Purpose:** Takes all raw data from the fetchers and produces a clean, concise, prioritized morning briefing
- **Cost:** ~$0.01-0.03 per daily briefing (negligible)
- **Setup:**
  1. Go to [console.anthropic.com](https://console.anthropic.com)
  2. Create an API key
  3. Store as `ANTHROPIC_API_KEY` env variable

---

## 4. Output Format

The SMS should be concise (SMS has a ~1,600 char limit for long messages via Twilio). Claude will summarize everything into this format:

```
☀️ GOOD MORNING — Fri Feb 21

🌤 WEATHER
45°F → 58°F, partly cloudy, 10% rain

📬 EMAIL (3 need attention)
• Prof. Johnson re: midterm grade posted
• Career Services: Spring fair registration
• Mom: dinner Sunday?

📚 HOMEWORK (2 due soon)
• CS 3114: Project 2 — due tomorrow 11:59 PM
• MATH 2214: HW 7 — due Monday

✅ REMINDERS
• Buy cleats before Saturday practice
• Call dentist

Have a great day! 🤙
```

**Note:** If there's nothing notable for a section (e.g., no reminders), that section is omitted to save space.

---

## 5. Project Structure

```
vt-morning-briefing/
├── README.md
├── PROGRESS.md
├── PRD.md
├── requirements.txt
├── .env.example
├── main.py                  # Entry point — orchestrates everything
├── config.py                # Loads env vars, constants
├── fetchers/
│   ├── __init__.py
│   ├── weather.py           # OpenWeatherMap fetcher
│   ├── gmail.py             # Gmail API fetcher
│   ├── outlook.py           # Microsoft Graph fetcher
│   ├── canvas.py            # Canvas LMS fetcher
│   └── reminders.py         # iCloud CalDAV fetcher
├── summarizer.py            # Claude API summarization
├── messenger.py             # Twilio SMS sender
├── auth/
│   ├── google_auth.py       # One-time Google OAuth setup
│   └── outlook_auth.py      # One-time Microsoft OAuth setup
├── railway.json             # Railway deployment config
└── Procfile                 # Process definition for Railway
```

---

## 6. Environment Variables

Create a `.env` file locally (never commit this). On Railway, add these in the dashboard under Variables.

```env
# Weather
OPENWEATHER_API_KEY=

# Gmail
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REFRESH_TOKEN=

# Outlook
OUTLOOK_CLIENT_ID=
OUTLOOK_CLIENT_SECRET=
OUTLOOK_REFRESH_TOKEN=
OUTLOOK_TENANT_ID=

# Canvas
CANVAS_API_TOKEN=
CANVAS_BASE_URL=https://canvas.vt.edu

# iCloud Reminders
ICLOUD_USERNAME=
ICLOUD_APP_PASSWORD=

# Twilio
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=
MY_PHONE_NUMBER=

# Claude API
ANTHROPIC_API_KEY=

# Config
TIMEZONE=America/New_York
BRIEFING_HOUR=7
BRIEFING_MINUTE=0
LOCATION_LAT=37.2296
LOCATION_LON=-80.4139
LOCATION_NAME=Blacksburg, VA
```

---

## 7. Development Phases

### Phase 1: Foundation (Day 1)
- Set up project structure and config
- Implement weather fetcher (simplest — good smoke test)
- Implement Twilio SMS sender
- Test: send yourself a weather-only briefing

### Phase 2: Email Integration (Day 2)
- Implement Gmail fetcher with OAuth
- Implement Outlook fetcher with MSAL
- Test: send yourself a briefing with weather + emails

### Phase 3: Canvas + Reminders (Day 3)
- Implement Canvas assignment fetcher
- Implement iCloud CalDAV reminders fetcher
- Test: full briefing with all data sources

### Phase 4: AI Summarization (Day 4)
- Implement Claude API summarizer
- Craft the summarization prompt
- Test: full pipeline end-to-end locally

### Phase 5: Deployment (Day 5)
- Deploy to Railway
- Configure cron schedule (7:00 AM ET daily)
- Monitor for 3 days to ensure reliability
- Set up basic error handling (send error SMS if pipeline fails)

---

## 8. Error Handling Strategy

- If a single fetcher fails (e.g., Canvas is down), the briefing still sends with whatever data succeeded, plus a note like "⚠️ Couldn't reach Canvas today"
- If Twilio fails, log the error to Railway logs
- If Claude API fails, send the raw data as a fallback (less pretty but still useful)
- All API calls use retry logic with exponential backoff (max 3 retries)

---

## 9. Cost Breakdown

| Service            | Monthly Cost |
|-------------------|-------------|
| Railway hosting    | ~$5.00      |
| Twilio (1 SMS/day) | ~$1.50      |
| Claude API         | ~$0.50      |
| OpenWeatherMap     | Free        |
| Gmail API          | Free        |
| Microsoft Graph    | Free        |
| Canvas API         | Free        |
| iCloud CalDAV      | Free        |
| **Total**          | **~$7/mo**  |

---

## 10. Future Enhancements (V2 Ideas)

- Add a "reply to text" feature to interact with the assistant (e.g., reply "snooze reminder: buy cleats" to push it to tomorrow)
- Add Google Calendar integration for today's schedule
- Add a weekly summary on Sundays
- Add Spotify "daily playlist" recommendation based on weather/mood
- Move to Telegram bot for richer formatting (bold, links, etc.)
- Add grade tracking from Canvas with alerts for grade changes

---

## 11. How to Build This with Claude Code

1. Open your terminal
2. Run `claude` to start Claude Code
3. Paste this PRD and say: "Build this project following this PRD. Start with Phase 1."
4. Claude Code will create the files, write the code, and walk you through setup
5. Follow the PROGRESS.md file to track what's done

---

*End of PRD*
