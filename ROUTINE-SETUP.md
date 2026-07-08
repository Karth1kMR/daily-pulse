# Cloud routine setup (runs with the Mac off)

One-time, ~3 minutes, in the Claude desktop app or at claude.ai/code/routines.

## 1. Create the routine

Desktop app → **Routines** in the sidebar → **New routine** → choose **Remote**
(Local would run on this Mac instead). Then:

- **Name**: `Daily Pulse refresh`
- **Repository**: add `Karth1kMR/daily-pulse`. If GitHub isn't connected yet,
  the form walks you through installing the Claude GitHub App — approve access
  to this repo.
- **Instructions (prompt)**: paste the block below.
- **Trigger → Schedule**: pick **Daily at 7:30 AM**. (After saving, the schedule
  can be changed to twice daily with the custom cron `0 2,14 * * *` — that's
  7:30 AM and 7:30 PM IST expressed in UTC.)

## 2. Environment settings (critical — runs fail without these)

Open the environment selector under the Instructions box → gear icon →
**Update cloud environment**:

- **Network access** → **Custom**, keep "include default list" checked, and add:
  `news.google.com`, `timesofindia.indiatimes.com`, `api.open-meteo.com`, `ntfy.sh`
- **Environment variables** → add `NTFY_TOPIC` = the topic name from the
  (gitignored) `.ntfy_topic` file in this repo on the Mac. Later, when the push
  worker is deployed, also add `PULSE_SEND_SECRET`.

## 3. Permissions

In the routine form under **Permissions**, enable **Allow unrestricted branch
pushes** for `Karth1kMR/daily-pulse` — the routine commits the fresh brief
directly to `main` so GitHub Pages redeploys.

## 4. Test

On the routine's page click **Run now**, open the run session, and check that it:
fetched sources → wrote `docs/data/brief.json` → pushed to main → sent the ntfy
notification. Then disable the local desktop fallback task if desired.

---

## Prompt to paste

```
Refresh the Daily Pulse brief for Bengaluru in this repo (Karth1kMR/daily-pulse).

Read GENERATE.md at the repo root and follow it exactly, end to end:
run scripts/fetch_sources.py, curate docs/data/raw.json into a fresh
docs/data/brief.json per the playbook's rules, archive it, validate the JSON,
commit with message "Brief: <date> <edition>" and push to main, then send the
ntfy notification using the NTFY_TOPIC environment variable (and web push if
configured). Set edition to "morning" if before 12:00 IST, else "evening".

Rules that must hold: never invent news — only summarize what fetch_sources.py
actually retrieved; exactly one street-smart scenario with one "best" choice and
at least one "trap"; exactly 5 quiz questions; avoid street-smart topics used in
docs/data/archive/ within the last 3 weeks. If every news feed fails, stop
without committing. Success = valid brief.json pushed to main + notification sent.
```
