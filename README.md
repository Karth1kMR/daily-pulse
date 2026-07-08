# Daily Pulse

A personal daily-awareness app for Bengaluru: local news digest, street-smart
scenario training, and a GK quiz — refreshed morning and evening, built entirely
on free keyless data sources.

## Layout

- `docs/` — static mobile-first web app (no build step). Serve with any static
  server, e.g. `python3 -m http.server 4174 --directory docs`.
- `docs/data/brief.json` — the current brief the app renders.
- `docs/data/raw.json` — raw fetched inputs (news RSS + weather).
- `docs/data/archive/` — past briefs, one per edition.
- `scripts/fetch_sources.py` — pulls Google News RSS, Times of India RSS and
  Open-Meteo weather (stdlib only, no API keys).
- `GENERATE.md` — the playbook the scheduled Claude job follows to turn raw
  inputs into a brief.

## Daily flow

1. Scheduled job runs at ~7:30 AM and ~8:00 PM IST.
2. It executes `scripts/fetch_sources.py`, then follows `GENERATE.md` to write a
   fresh `docs/data/brief.json` (+ archive copy).
3. (Planned) It then pushes a notification to the phone — channel TBD
   (options: Telegram bot, ntfy.sh, or iOS web push once installed as a PWA).

## Features

- **Around you today** — 5–7 curated local/national items with practical angles.
- **Happenings** — attendable events this week.
- **Street Smart** — one interactive scenario a day (choose → see which choice
  is the trap / risky / best, with mechanism-level feedback), preferably drawn
  from a real incident in that day's news.
- **Daily GK** — 5-question quiz from today's news + evergreen topics, with a
  localStorage day streak.
