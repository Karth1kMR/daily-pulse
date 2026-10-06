# Daily Pulse — generation playbook

Instructions for the scheduled job that refreshes the brief twice a day. Follow
this exactly; the app renders whatever lands in `docs/data/brief.json`.

## The product, in one line

Sixty seconds that leave the reader harder to fool and quicker to understand —
**not** a news digest. If an item doesn't change what he'd do, think, or notice,
it does not go in.

Three hard rules, in priority order:

1. **Mechanisms over events.** A scam story is worthless; the rule that detects
   every future version of it is the product. Same for news: the model that
   explains a category beats the event.
2. **Implications over headlines.** Never state what happened without stating
   what it means for one person living in Bengaluru.
3. **Ruthless brevity.** He has no time. Cutting a weak item is always correct.
   Four strong "moved" items beat seven padded ones.

## Steps

### 1. Fetch
```
python3 scripts/fetch_sources.py
```
Writes `docs/data/raw.json` (~75 headlines + weather). If some feeds error,
continue. Abort without committing only if *everything* failed.

### 2. Pick the Edge (street smart)

Read `content/edges.json`. Pick one entry, preferring in this order:

- An edge whose trap **appears in today's news** (a reported scam, theft, fraud,
  dispute). Set `anchor` to one factual line about that real incident. This is
  the ideal case — the trap is demonstrably live this week.
- Otherwise the least recently used edge. Check `docs/data/archive/` filenames
  and recent briefs; **never repeat an edge within 21 days**.

Copy the entry into `brief.edge` with fields: `id`, `category`, `title`,
`anchor` (omit if no real incident — do not invent one), `setup`, `tell`,
`move` (array), `why`, `variants`.

You may lightly localise `setup` to today's context, but **never alter `tell`,
`why`, or the legal/number facts in `move`** without verifying them.

**If no library entry fits and today's news reveals a genuinely new trap**, write
a new one into `content/edges.json` following the existing shape. The bar: the
`tell` must be a detection rule a tired person can apply in three seconds, and
`why` must explain the mechanism so it generalises beyond the incident.

### 3. Pick the Lens (mental model)

Read `content/lenses.json`. Pick the model that **best explains something in
today's raw.json** — this is the selection criterion, not rotation. Never repeat
a lens within 21 days.

Copy into `brief.lens`: `id`, `name`, `one_line`, `detail`, `elsewhere`, `test`,
plus a **newly written `today`** field (2–3 sentences) connecting the model to an
actual story in today's feeds. The `today` field is the whole point — it is
written fresh every time and must name the real story.

If nothing in the news fits any model honestly, pick the most useful model and
write `today` about a standing Bengaluru reality (traffic, rents, water, civic
process) rather than forcing a bad connection.

### 4. Write "What moved"

Four to six items, each `{tag, what, so_what}`.

- `tag`: short, reader-centric — "Commute", "Money", "Safety", "Civic",
  "Your record", "Worth booking", "Prices".
- `what`: the change, one or two sentences, concrete and specific.
- `so_what`: **the only part that matters.** What this means for him — a route to
  avoid, a window to act in, a thing to check, a cost that's coming. If you
  cannot write a real `so_what`, delete the item.

Admission test — an item belongs only if it affects at least one of: his money,
his commute, his safety, a record or entitlement of his, or a dated opportunity
he'd otherwise miss. **Deliberately exclude**: crime reports with no transferable
lesson, political point-scoring, celebrity and viral filler, corporate PR,
national and world news with no India-level consumer impact.

Prefer one well-chosen national or world item **only** when it transmits to daily
life (fuel, rates, prices, visas, flights) — written as the transmission, not the
event.

### 5. Weather

Copy numbers from raw.json. Write one `tip` that combines weather with something
else in today's brief (a closure, an event, a commute change). Generic
"carry an umbrella" is a wasted line.

### 6. Carry-over

Set `carry_over` to the **previous** brief's edge:
```json
{ "id": "<previous edge id>", "prompt": "<the setup compressed to one sentence, ending in a question>", "answer": "<that edge's tell>" }
```
Read the previous brief from `docs/data/archive/` to get it. Omit the
`first_run_note` field once a real carry-over exists.

### 7. Assemble, archive, validate

`brief.json` fields: `date` (IST), `edition` ("morning" before 12:00 IST else
"evening"), `city`, `generated_at`, `read_seconds` (estimate honestly, 60–100),
`weather`, `edge`, `lens`, `moved`, `carry_over`.

Copy to `docs/data/archive/YYYY-MM-DD-{edition}.json`, then:
```
python3 -c "import json; json.load(open('docs/data/brief.json'))"
```

### 8. Publish

Commit `Brief: <date> <edition>` and push to `main`. GitHub Pages redeploys
https://karth1kmr.github.io/daily-pulse/ automatically.

### 9. Notify

**The notification must carry the value, not advertise it.** If he reads only the
push and never opens the app, he should still have gained the Tell.

Title: `The Edge — <edge title>`
Body: the `tell`, then the single most actionable `so_what` from "What moved".

Topic is secret: read `NTFY_TOPIC` from the environment, or the gitignored
`.ntfy_topic` file locally. Skip without failing if neither exists.
```
curl -H "Title: The Edge — <title>" \
     -H "Click: https://karth1kmr.github.io/daily-pulse/" \
     -d "<tell> · <top so_what>" \
     "https://ntfy.sh/$NTFY_TOPIC"
```

If `docs/config.js` has a non-empty `pushWorkerUrl` and `PULSE_SEND_SECRET` is
set, also POST `{pushWorkerUrl}/send` with
`Authorization: Bearer $PULSE_SEND_SECRET` and
`{"title","body","url":"https://karth1kmr.github.io/daily-pulse/"}`.

## Voice

Calm, specific, zero hype. No exclamation marks, no "shocking", no "you won't
believe". Write as a well-informed friend who respects his time and assumes he's
intelligent. Indian English, rupees as ₹, 24-hour clock where ambiguous.

Never invent news, incidents, numbers, or helpline details. Everything factual
comes from raw.json or from the verified libraries.
