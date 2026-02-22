# PROGRESS.md — VT Morning Briefing

> **Instructions for Claude Code:** This file tracks the build progress of the VT Morning Briefing personal assistant. Update this file as you complete each task. Check boxes by changing `[ ]` to `[x]`. Refer to `PRD.md` for full specifications.

---

## Quick Status

| Phase | Description           | Status      |
|-------|-----------------------|-------------|
| 1     | Foundation            | 🟡 In Progress |
| 2     | Email Integration     | 🔲 Not Started |
| 3     | Canvas + Reminders    | 🔲 Not Started |
| 4     | AI Summarization      | 🔲 Not Started |
| 5     | Deployment            | 🔲 Not Started |

---

## Phase 1: Foundation

- [x] Create project directory structure (see PRD Section 5)
- [x] Create `requirements.txt` with all dependencies
- [x] Create `.env.example` with all required variables
- [x] Create `config.py` to load environment variables
- [x] Implement `fetchers/weather.py` — OpenWeatherMap API
- [x] Implement `messenger.py` — Twilio SMS sender
- [x] Create `main.py` — basic orchestrator
- [ ] **TEST:** Send a weather-only SMS to your phone

**Credentials needed before starting:**
- [ ] OpenWeatherMap API key
- [ ] Twilio Account SID, Auth Token, Phone Number

---

## Phase 2: Email Integration

- [ ] Implement `auth/google_auth.py` — one-time OAuth flow
- [ ] Implement `fetchers/gmail.py` — fetch unread emails (last 24h)
- [ ] Run Google OAuth flow and save refresh token
- [ ] **TEST:** Verify Gmail fetcher returns correct unread emails
- [ ] Implement `auth/outlook_auth.py` — one-time OAuth flow
- [ ] Implement `fetchers/outlook.py` — fetch unread emails (last 24h)
- [ ] Run Outlook OAuth flow and save refresh token
- [ ] **TEST:** Verify Outlook fetcher returns correct unread emails
- [ ] **TEST:** Send SMS with weather + both email summaries

**Credentials needed before starting:**
- [ ] Google Cloud project with Gmail API enabled + OAuth credentials
- [ ] Azure App Registration with Mail.Read permission + client secret

---

## Phase 3: Canvas + Reminders

- [ ] Implement `fetchers/canvas.py` — fetch upcoming assignments (next 7 days)
- [ ] **TEST:** Verify Canvas returns correct assignments and due dates
- [ ] Implement `fetchers/reminders.py` — iCloud CalDAV integration
- [ ] **TEST:** Verify reminders fetcher returns incomplete reminders
- [ ] **TEST:** Send full briefing SMS (weather + emails + canvas + reminders)

**Credentials needed before starting:**
- [ ] Canvas personal access token from canvas.vt.edu
- [ ] Apple ID app-specific password from appleid.apple.com

---

## Phase 4: AI Summarization

- [ ] Implement `summarizer.py` — Claude API integration
- [ ] Write summarization prompt (concise, prioritized, SMS-friendly)
- [ ] Wire summarizer into `main.py` pipeline
- [ ] **TEST:** Run full pipeline locally — all fetchers → Claude → SMS
- [ ] Verify SMS is concise and within character limits
- [ ] Handle edge cases: no emails, no assignments, no reminders

**Credentials needed before starting:**
- [ ] Anthropic API key from console.anthropic.com

---

## Phase 5: Deployment to Railway

- [ ] Create `railway.json` with cron config
- [ ] Create `Procfile`
- [ ] Push code to GitHub repository
- [ ] Connect GitHub repo to Railway
- [ ] Add all environment variables to Railway dashboard
- [ ] Set cron schedule to `0 12 * * *` (7:00 AM ET = 12:00 UTC)
- [ ] **TEST:** Let it run for 1 morning and verify SMS arrives at 7 AM
- [ ] Add error handling — send error notification if pipeline fails
- [ ] Monitor for 3 days
- [ ] **DONE:** 🎉 You now have a personal AI assistant

---

## Troubleshooting Log

_Use this section to track any issues encountered during development._

| Date | Issue | Resolution |
|------|-------|------------|
| 2/21 | OWM API key returns 401 | Key may need a few hours to activate after creation |

---

## Notes

- SMS limit is ~1,600 characters via Twilio (long SMS / concatenated messages)
- If a single data source fails, the briefing should still send with available data
- OAuth tokens (Google, Microsoft) need refresh — code handles this automatically
- Canvas tokens don't expire unless revoked
- iCloud app-specific passwords don't expire unless revoked
- Railway cron uses UTC — 7:00 AM ET = 12:00 PM UTC (adjust for DST: 11:00 AM UTC in summer)

---

*Last Updated: February 21, 2026*
