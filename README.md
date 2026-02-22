# ☀️ VT Morning Briefing

A personal AI assistant that sends you a daily SMS at 7:00 AM with everything you need to start your day.

## What You Get

Every morning, one text message with:
- **Weather** — current conditions and forecast for Blacksburg, VA
- **Gmail** — unread emails that need your attention
- **Outlook** — unread emails that need your attention
- **Canvas** — upcoming homework and assignments (next 7 days)
- **Reminders** — your incomplete iPhone reminders

All summarized by Claude AI into a concise, actionable briefing.

## Quick Start

1. Clone this repo
2. Copy `.env.example` to `.env` and fill in your credentials
3. Run auth scripts for Google and Outlook (one-time setup)
4. Test locally: `python main.py`
5. Deploy to Railway for daily automated runs

## Building with Claude Code

This project was designed to be built with [Claude Code](https://docs.anthropic.com/en/docs/claude-code). To get started:

```bash
claude
```

Then paste the contents of `PRD.md` and say: **"Build this project following this PRD. Start with Phase 1."**

Track your progress in `PROGRESS.md`.

## Docs

- [PRD.md](PRD.md) — Full product requirements and architecture
- [PROGRESS.md](PROGRESS.md) — Build checklist and progress tracker

## Cost

~$7/month total (Railway hosting + Twilio SMS + Claude API)

## License

Personal project — use however you'd like.
