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

Read GENERATE.md at the repo root and follow it exactly, end to end: run
scripts/fetch_sources.py, then build docs/data/brief.json with four parts —

1. edge: ONE trap decoded, from content/edges.json. Prefer one whose trap appears
   in today's news (set "anchor" to one factual line about that real incident);
   otherwise least recently used. Never repeat within 21 days (check
   docs/data/archive/).
2. lens: ONE mental model from content/lenses.json, chosen because it explains
   something in today's news. Write a FRESH "today" field (2-3 sentences) naming
   the real story. Never repeat within 21 days.
3. moved: 4-6 items {tag, what, so_what}. The so_what is the point — what it
   means for one person in Bengaluru. Admission test: it must affect his money,
   commute, safety, a record/entitlement of his, or a dated opportunity. Exclude
   crime reports with no transferable lesson, political point-scoring, celebrity
   and viral filler, corporate PR.
4. carry_over: the PREVIOUS brief's edge as {id, prompt, answer}, read from
   docs/data/archive/.

Plus weather with a tip tied to something else in the brief, and read_seconds.
Set edition to "morning" if before 12:00 IST, else "evening".

Then archive to docs/data/archive/YYYY-MM-DD-{edition}.json, validate the JSON,
commit "Brief: <date> <edition>", push to main, and send the ntfy notification
using the NTFY_TOPIC environment variable: title "The Edge — <edge title>", body
= the edge's "tell" followed by the most actionable so_what. The notification must
carry the value, not advertise it.

Never invent news, incidents, numbers or helpline details. If every feed fails,
stop without committing.
```
