# Daily Pulse — brief generation playbook

This is the instruction set for the scheduled job (a Claude session) that refreshes
the app twice a day. Follow it exactly; the app renders whatever lands in
`docs/data/brief.json`.

## Steps

1. **Fetch raw inputs** (free, keyless sources):
   ```
   python3 scripts/fetch_sources.py
   ```
   This writes `docs/data/raw.json` with ~75 headlines (Bengaluru news, traffic/metro,
   events, national/world) and today's weather. If it reports errors for some feeds,
   continue with what fetched; only abort if *everything* failed.

2. **Read `docs/data/raw.json`** and write `docs/data/brief.json` with this shape
   (see the existing file for a full example):
   - `date` (IST, YYYY-MM-DD), `edition` ("morning" if before 12:00 IST else "evening"), `city`, `generated_at`
   - `weather` — copy numbers from raw; write a one-line practical `tip`
     (rain → umbrella/traffic; heat → hydration; nothing notable → commute note)
   - `around` — 5–7 items curated from the feeds. Rules:
     - Prioritize: safety incidents & scams > transport/traffic changes > civic
       decisions that affect daily life > one big India/world story with a
       "what it means for you" angle
     - Deduplicate stories covered by multiple outlets; cite 1–2 sources
     - `category` one of: "Getting around", "Safety", "Scam alert", "Civic",
       "Money", "India & world"
     - Each `summary` ≤ 2 sentences, and where natural include one practical
       implication for a Bengaluru resident
   - `events` — 3–5 upcoming happenings from the events feed (skip PR/corporate
     announcements; prefer things a person can actually attend)
   - `street_smart` — ONE scenario. Strongly prefer basing it on a real incident
     from today's feeds (scams, road rage, theft, rental/consumer traps); note the
     source in `based_on`. Otherwise rotate evergreen topics (see rotation below).
     Exactly one choice has `verdict: "best"`, at least one is `"trap"`, rest
     `"risky"`. Feedback must teach the *mechanism* of the trap, not just
     right/wrong. 2–3 `takeaways`, each concrete (a number to call, a rule of
     thumb, a check to perform).
   - `quiz` — exactly 5 questions: ~3 from today's actual news (local + national),
     ~2 evergreen GK (civics, geography, economics, science). `answer` is the
     0-based index. `why` teaches one extra fact beyond the answer.

3. **Archive**: copy the finished brief to `docs/data/archive/YYYY-MM-DD-{edition}.json`.

4. **Verify**: `python3 -c "import json; json.load(open('docs/data/brief.json'))"` must pass.

5. **Publish**: commit all changes with message `Brief: YYYY-MM-DD {edition}` and push
   to `main`. GitHub Pages (https://karth1kmr.github.io/daily-pulse/) redeploys
   automatically from `docs/`.

6. **Notify (ntfy)**: send the phone notification — title
   `Daily Pulse — {morning|evening} brief`, body = the single most important headline
   plus the weather tip. The topic name is a secret: read it from the `NTFY_TOPIC`
   environment variable, or from the gitignored `.ntfy_topic` file when running
   locally. Skip this step (without failing) if neither exists.
   ```
   curl -H "Title: Daily Pulse — morning brief" \
        -H "Click: https://karth1kmr.github.io/daily-pulse/" \
        -d "<top headline>. <weather tip>" \
        "https://ntfy.sh/${NTFY_TOPIC:-$(cat .ntfy_topic)}"
   ```

7. **Notify (web push, optional)**: if `docs/config.js` has a non-empty
   `pushWorkerUrl` and a `PULSE_SEND_SECRET` secret is available in the environment,
   also POST `{pushWorkerUrl}/send` with header `Authorization: Bearer $PULSE_SEND_SECRET`
   and JSON body `{"title": "...", "body": "...", "url": "https://karth1kmr.github.io/daily-pulse/"}`.
   Skip silently if either is missing.

## Street-smart evergreen rotation (when no news-based scenario fits)

digital-arrest scams · UPI fraud & fake payment screenshots · auto/cab overcharging
& refusal · rental agreement traps · fake job offers & deposit fraud · OTP/social
engineering · two-wheeler theft prevention · medical emergency response (108, CPR
basics) · tenant/landlord rights · consumer court basics · phone snatching response
(CEIR blocking) · loan-app harassment · credit-card skimming.

Keep a note of recently used topics by scanning `docs/data/archive/` filenames'
recent briefs to avoid repeats within ~3 weeks.

## Tone

Practical, calm, zero clickbait. Every item should leave the reader either safer,
better informed, or knowing something they can act on. Never invent news — only
summarize what is in raw.json.
