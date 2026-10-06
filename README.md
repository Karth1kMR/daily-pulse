# Daily Pulse

Sixty seconds a day that leave you harder to fool and quicker to understand.
Not a news app — a news app would tell you a cobra stopped traffic on Palace
Road. This tells you the rule that detects every rental scam you'll ever meet,
and the model that explains why the new tunnel won't fix Hebbal.

Live at **https://karth1kmr.github.io/daily-pulse/** — installable on iPhone via
Safari → Share → Add to Home Screen.

## What's in a brief

| Section | What it is | Why it's there |
| --- | --- | --- |
| **The Edge** | One trap decoded — the setup, the three-second *tell*, your move, and the mechanism that makes it generalise | Street smarts transfer through mechanisms, not anecdotes |
| **The Lens** | One mental model, applied to something that actually happened today | A model explains a category of news forever; a headline expires in a day |
| **What moved** | 4–6 changes, each written as *what → so what for you* | Awareness is only useful when it's decision-relevant |
| **Yesterday, five seconds** | The previous Edge, one tap to recall | Retention with no quiz and no time cost |

## Layout

- `docs/` — the PWA (static, no build step). Served by GitHub Pages.
- `docs/data/brief.json` — today's brief; the only file the app reads.
- `docs/data/archive/` — past briefs, used to avoid repeats and build carry-overs.
- `content/edges.json` — street-smart library (traps, mechanisms, tells).
- `content/lenses.json` — mental-model library.
- `scripts/fetch_sources.py` — Google News RSS, Times of India RSS, Open-Meteo.
  Standard library only, no API keys.
- `GENERATE.md` — the playbook the scheduled job follows. **The editorial
  standard lives here**, including the admission test for what counts as news.
- `worker/` — Cloudflare Worker for iOS web push (see `worker/README.md`).
- `ROUTINE-SETUP.md` — one-time cloud-routine setup so it runs with the Mac off.

The two libraries are the point of the architecture: the learning content is
curated and verified, so quality doesn't depend on whether today's news happened
to contain something instructive. News only *anchors* it.

## Daily flow

1. Scheduled job runs ~7:30 AM and ~7:30 PM IST (Claude cloud routine; a local
   desktop task is the fallback).
2. Fetches sources, follows `GENERATE.md`, writes `docs/data/brief.json`,
   archives, commits and pushes — Pages redeploys.
3. Pushes a notification that *carries* the Tell, so the value lands even if the
   app is never opened.

## Local preview

```bash
python3 -m http.server 4174 --directory docs
```
