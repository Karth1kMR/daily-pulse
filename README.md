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

1. A scheduled job (Claude cloud routine; local desktop task as fallback) runs at
   ~7:30 AM and ~7:30 PM IST.
2. It executes `scripts/fetch_sources.py`, then follows `GENERATE.md` to write a
   fresh `docs/data/brief.json` (+ archive copy), commits, and pushes — GitHub
   Pages redeploys the site at https://karth1kmr.github.io/daily-pulse/.
3. It notifies the phone via ntfy.sh (topic kept out of the repo) and, once the
   push worker in `worker/` is deployed, via iOS web push to the installed PWA.
   See `ROUTINE-SETUP.md` for the cloud-routine recipe and `worker/README.md`
   for the push-worker deploy steps.

## Features

- **Around you today** — 5–7 curated local/national items with practical angles.
- **Happenings** — attendable events this week.
- **Street Smart** — one interactive scenario a day (choose → see which choice
  is the trap / risky / best, with mechanism-level feedback), preferably drawn
  from a real incident in that day's news.
- **Daily GK** — 5-question quiz from today's news + evergreen topics, with a
  localStorage day streak.
