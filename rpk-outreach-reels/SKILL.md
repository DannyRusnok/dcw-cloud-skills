---
name: rpk-outreach-reels
description: >
  Autonomous reel-outreach routine (runs 3x/day) — turn a high-engagement foreign
  Substack article into a branded animated Reel Pipeline Kit reel and send Daniel a
  Telegram draft he approves by REACTING to it. Self-contained: NEVER ask questions,
  NEVER wait for an ack-gate. Uses substack-mcp + pc-mcp connector tools and Bash
  (only for the FAILURE notify curl + sleeps). Does NOT publish to Substack itself —
  Daniel publishes by reacting to the Telegram draft.
---

# rpk-outreach-reels

Reel outreach from top foreign Substack articles, posted as Telegram drafts from
Daniel's direct **danielrusnok** account context.

**Inputs from the routine prompt (NOT in this file — public repo):**
- `NOTIFY_KEY` — subhook Telegram relay key. If missing, skip notify steps.

Self-contained: NEVER ask questions, NEVER wait for an ack-gate. Do NOT publish to
Substack yourself — Daniel publishes by reacting to the Telegram draft.

## STEPS

### 1 — candidates

`find_reel_candidate` (substack-mcp) `{ topK: 15, daysBack: 30, excludeRecentAuthorDays: 7 }`.

It already excludes official Substack pubs, holds the 2k–30k follower band, pulls
subscriptions ∪ Suggestions, and skips articles done + authors tapped in the last
7 days. Returns candidates with title, url, publication, subdomain, authorName,
authorHandle, authorUserId, reactions, comments, restacks, score.

### 2 — filter to REAL individual authors

DROP any whose `subdomain` is one of `[post, on, substack, support, reads]`, OR
`authorHandle` is `"substack"`, OR `authorName` is `"Substack"`, AND drop any with
null/missing `authorHandle` or `authorUserId`. Take the top remaining = THE PICK.

If none qualify, Bash-curl the success notify with text
`No new real-author candidate this run` and exit.

### 3 — render

`render_reel_from_url` (pc-mcp)
`{ url: <PICK.url>, publicationName: <PICK.publication>, animateHook: true, requireHookAnimation: true, targetDurationSeconds: 30 }`
→ `{ jobId }`.

(`animateHook: true` now FULLY animates the reel — the hook plus every scene with a
Wan-friendly image; renders take longer, ~10–20 min. `requireHookAnimation: true` —
this is Daniel's direct danielrusnok account, so the hook MUST be truly Wan-animated;
the render ERRORS rather than silently falling back to a static Ken Burns hook if
the GPU queue is busy. Quality must never degrade here.)

Poll `render_reel_status({ jobId })`; between polls Bash `sleep 30`; up to 60 polls
(~30 min — multi-scene Wan + busy GPU queue can take 20+ min). On done capture `r2Url`.

If the render ERRORS with a hook-animation / GPU-busy message, WAIT 3 min
(Bash `sleep 180`) and retry `render_reel_from_url` ONCE with the same params; if it
errors again, send the FAILURE notify (step 6) and exit — do NOT draft a
non-animated reel. On any other error/timeout send the FAILURE notify and exit.

### 4 — record

`record_reel_outreach` (substack-mcp) `{ authorHandle: <PICK.authorHandle>, articleUrl: <PICK.url> }`.

### 5 — Telegram draft

The note copy is EXACTLY (fill `<authorHandle>`, `<PICK.title>`):

> I built a Digital Craft Workshop algorithm that picks one Substack post a day and
> turns it into a gift. Today it chose @\<authorHandle\>'s "\<PICK.title\>" — for two
> reasons: it had the highest engagement in my feed, and its visuals aren't just text
> cards but real graphics that animate beautifully. So here's your post as a
> fully-animated vertical reel, made end-to-end from the URL. Restack it if you'd use it.

Then call `send_reel_draft` (substack-mcp):

```
{
  content: <the exact note copy above>,
  videoUrl: <r2Url>,
  videoDurationSeconds: 30,
  articleUrl: <PICK.url>,
  authorHandle: <PICK.authorHandle>,
  authorUserId: <PICK.authorUserId>,
  authorName: <PICK.authorName>,
  caption: "🎬 Reel draft — @<authorHandle> · React 👍 to publish (text + @mention ping + video)\n\n<the exact note copy above>\n\n— Article: <PICK.url>\nCandidate: @<authorHandle> · R<reactions> C<comments> RS<restacks> · score <score> · <PICK.publication>"
}
```

Keep the caption under 1024 chars (trim the title in the copy if needed). This posts
the reel to Telegram; Daniel publishes by reacting to that message. Do NOT call
`publish_note` yourself.

### 6 — FAILURE notify only (Bash)

```
curl -s -X POST "https://subhook.fly.dev/api/notify?key=$NOTIFY_KEY" -H 'Content-Type: application/json' \
  -d '{"title":"⚠️ Reel routine failed — <YYYY-MM-DD HH:MM>","text":"<short reason / stage. If render_reel_from_url errored, the PC may be asleep or RPK / ComfyUI down — wake the PC and re-run from claude.ai.>"}'
```

### 7 — wrap-up

Print a one-line summary and exit. Do NOT publish to Substack, do NOT commit
anything, do NOT open PRs, do NOT use any connector other than substack-mcp / pc-mcp.
