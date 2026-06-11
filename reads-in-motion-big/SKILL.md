---
name: reads-in-motion-big
description: >
  Autonomous routine for the 'Reads in Motion' curation account (account='readsinmotion'),
  BIG-newsletters variant. Runs 5x/day: pick ONE article from a BIG newsletter in Substack's
  Suggestions, render a reel, AUTO-PUBLISH it as Reads in Motion (tagging the author), then
  add a promo comment from the danielrusnok account. Self-contained: NEVER ask questions,
  NEVER wait for an ack-gate. Uses substack-mcp + pc-mcp tools + Bash (notify + sleeps).
---

# reads-in-motion-big

Autonomous 5x/day curation run for **Reads in Motion** (`account='readsinmotion'`),
sourcing from Substack's **Suggestions** (big newsletters). Smaller publications get
prioritized (`find_reel_candidate` defaults `maxAuthorSubs=30000` for suggestions).

**Inputs from the routine prompt (NOT in this file — public repo):**
- `NOTIFY_KEY` — subhook Telegram relay key. If missing, skip notify steps.

Self-contained: NEVER ask questions, NEVER wait for an ack-gate. Use only
substack-mcp / pc-mcp / Bash.

## STEP 1 — candidate

`find_reel_candidate` (substack-mcp)
`{ source: 'suggestions', account: 'readsinmotion', topK: 25, daysBack: 30, excludeRecentAuthorDays: 7 }`.

Scans Substack's suggested newsletters' archives by engagement, excludes articles
already done + authors tapped in the last 7 days (GLOBAL across both accounts and
BOTH RiM routines) AND authors whose publication has >30k subscribers (default).

Take THE TOP candidate with a non-null `authorHandle` AND `authorUserId` = THE PICK.
If none, Bash-curl the success notify (title `Reads in Motion — no candidate (suggestions)`,
text `Suggestions pool returned nothing new this run.`) and exit.

## STEP 2 — render

`render_reel_from_url` (pc-mcp)
`{ url: <PICK.url>, publicationName: <PICK.publication>, animateHook: true, targetDurationSeconds: 30 }`
→ `{ jobId }`.

(`animateHook` ON: the hook + up to 2 image-bearing scenes are animated via LOCAL
Wan i2v; on failure they fall back to Ken Burns, never a static frame.)

Poll `render_reel_status({ jobId })`; between polls Bash `sleep 30`. Do NOT cap by
poll count. Keep polling and stop ONLY when one of these is true:

- `status='done'` → capture `r2Url` AND the returned `hookWarn`
- `status='error'` → FAILURE notify + exit
- the returned `elapsedMs` exceeds `2400000` (40 min) → treat as timeout, FAILURE notify + exit

Trust `elapsedMs` (real PC wall-clock time), NOT the number of polls — in the cloud
Bash `sleep` does NOT wait real time, so a poll-count limit would expire long before
a 20–40 min Wan render finishes.

## STEP 3 — record

`record_reel_outreach` (substack-mcp)
`{ authorHandle: <PICK.authorHandle>, articleUrl: <PICK.url>, account: 'readsinmotion' }`.

## STEP 4 — write a SHORT note (English)

TIGHT so the text doesn't steal attention from the reel:

1. credit the author with `@<authorHandle>`,
2. ONE short concrete sentence about what THIS post is about (no template, no hype),
3. a SHORT restack nudge on its own line that asks for a RESTACK specifically.
   VARY the wording run-to-run — e.g. `Restack to send it to more readers.` /
   `A restack carries it further than a like.` / `Worth a restack if it lands.` /
   `Restack it onward if it's useful.` Never reuse the exact same sentence two runs in a row.
4. the article URL on its own line.

Keep it tight — mention + one sentence + restack nudge + link. No other CTA.

## STEP 5a — UPLOAD the reel ASYNC

`upload_reel_video` (substack-mcp)
`{ videoUrl: <r2Url>, videoDurationSeconds: 30, account: 'readsinmotion' }` → `{ jobId }`.

Poll `get_video_upload_status({ jobId })`; between polls Bash `sleep 6`. Keep polling
and stop ONLY when `status='done'` (capture `attachmentId`) or `status='error'`/timeout
(FAILURE notify with the status reason + exit). Use a HIGH safety cap of up to 600
polls — the upload itself finishes in <90s, but in the cloud Bash `sleep` does NOT
wait real time, so a low poll cap would false-timeout before the upload reports done.

## STEP 5b — AUTO-PUBLISH as Reads in Motion

`publish_note` (substack-mcp):

```
{
  content: <your SHORT note text from STEP 4, including the '@<authorHandle>' token,
            the restack nudge, and the article URL>,
  attachmentId: <attachmentId from STEP 5a>,
  articleUrl: <PICK.url>,
  mentions: [{ handle: <PICK.authorHandle>, userId: <PICK.authorUserId>, name: <PICK.authorName> }],
  account: 'readsinmotion'
}
```

Do NOT pass `videoUrl` here — use `attachmentId`. CAPTURE the returned `noteUrl`.

CRITICAL: if `publish_note` returns `ok:false` with errorCode `auth_expired` OR
errorCode `substack_rate_limit` OR errorMessage containing
`Something has gone terribly wrong` / `cloudflare` / `403`, this is almost always
Cloudflare's WAF intermittently rate-limiting the Fly IP — NOT a real auth failure.
Retry up to 3 times with INCREASING delays: Bash `sleep 60` then retry, on second
failure `sleep 180` then retry, on third failure `sleep 300` then retry. Only after
the third retry still fails send the FAILURE notify with the errorMessage and exit.
Do NOT classify these as auth_expired in the notify — say
`Cloudflare WAF block (~5min TTL); 3 retries exhausted`.

## STEP 5c — promo COMMENT from the danielrusnok account

`comment_on_note` (substack-mcp):

```
{
  targetNoteUrl: <noteUrl from STEP 5b>,
  body: "Made this with my Reel Pipeline Kit — it turns any Substack post into a vertical reel like this one, running locally on your own machine. The full build series and the kit's waiting list are here: https://danielrusnok.substack.com/p/reel-pipeline-series"
}
```

`comment_on_note` has NO account param and always posts as danielrusnok (intended).
If it returns `ok:false` with `auth_expired` or `rate_limit`, WAIT 60s and retry
`comment_on_note` ONCE. If it still fails, do NOT fail the run — just note
`promo comment failed` in the success notify.

## STEP 6 — success notify

```
curl -s -X POST "https://subhook.fly.dev/api/notify?key=$NOTIFY_KEY" -H 'Content-Type: application/json' \
  -d '{"title":"✅ Reads in Motion posted (big) — @<authorHandle>","text":"<the note text>\n\n<noteUrl from publish_note>\nreel <r2Url> · <PICK.publication>\nhook: <animated / Ken Burns fallback>\npromo comment from danielrusnok: <ok/failed>"}'
```

## FAILURE notify

```
curl -s -X POST "https://subhook.fly.dev/api/notify?key=$NOTIFY_KEY" -H 'Content-Type: application/json' \
  -d '{"title":"⚠️ Reads in Motion failed (suggestions) — <YYYY-MM-DD HH:MM>","text":"<short reason / stage. PC may be asleep or RPK/ComfyUI down.>"}'
```

## Wrap-up

Print a one-line summary and exit. Do NOT commit anything, do NOT open PRs,
do NOT use any connector other than substack-mcp / pc-mcp.
