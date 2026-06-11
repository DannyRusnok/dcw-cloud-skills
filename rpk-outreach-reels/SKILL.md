---
name: rpk-outreach-reels
description: >
  Autonomous reel-outreach routine (runs 3x/day) for the primary danielrusnok account.
  Picks ONE high-engagement foreign Substack article, writes a gift note, and ENQUEUES an
  async reel job. Does NOT render itself — the substack-mcp worker renders (one at a time,
  waits for GPU/RPK) and sends Daniel a Telegram draft he approves by REACTING. Self-contained:
  NEVER ask questions, NEVER wait for an ack-gate. Uses substack-mcp tools + Bash (notify only).
---

# rpk-outreach-reels

Async outreach routine. The slow render no longer runs inline — you ENQUEUE and exit; the
substack-mcp worker drains the queue, renders, and sends the Telegram draft. This never fails
on a busy GPU or a restarting render server: the render just waits its turn in the queue.

NOTIFY_KEY=3cebe32fb52d24f41f462aa793349b5d

## STEP 1 — candidate

find_reel_candidate (substack-mcp) `{ topK: 15, daysBack: 30, excludeRecentAuthorDays: 7 }`. It excludes official Substack pubs, holds the 5k–30k follower band, pulls subscriptions ∪ Suggestions, and skips articles/authors done in the last 7 days. Keep only REAL individual authors: DROP any whose subdomain is one of `[post, on, substack, support, reads]`, OR authorHandle is "substack", OR authorName is "Substack", AND drop any with null/missing authorHandle or authorUserId. Take the top remaining = THE PICK. If none qualify, Bash-curl the success notify (title `No new real-author candidate this run`) and exit.

## STEP 2 — note (English)

The note copy is EXACTLY (fill `<authorHandle>`, `<PICK.title>`):

```
I built a Digital Craft Workshop algorithm that picks one Substack post a day and turns it into a gift. Today it chose @<authorHandle>'s "<PICK.title>" — for two reasons: it had the highest engagement in my feed, and its visuals aren't just text cards but real graphics that animate beautifully. So here's your post as a fully-animated vertical reel, made end-to-end from the URL. Restack it if you'd use it.
```

## STEP 3 — ENQUEUE + exit

enqueue_reel_outreach (substack-mcp) `{ account: 'primary', url: <PICK.url>, publicationName: <PICK.publication>, authorHandle: <PICK.authorHandle>, authorUserId: <PICK.authorUserId>, authorName: <PICK.authorName>, content: <the exact note copy above> }`.

It returns immediately. **Do NOT render, do NOT poll, do NOT publish** — the worker renders the reel (serial, waits for the GPU/RPK; the hook MUST be truly Wan-animated for this primary account, the render errors rather than shipping a static fallback) and sends Daniel the Telegram draft. Daniel publishes by reacting to that draft.

## STEP 4 — success notify (Bash)

```
curl -s -X POST 'https://subhook.fly.dev/api/notify?key=3cebe32fb52d24f41f462aa793349b5d' -H 'Content-Type: application/json' -d '{"title":"✅ Outreach reel queued — @<authorHandle>","text":"Queued for async render; Telegram draft will arrive when ready. <PICK.publication>"}'
```

Print a one-line summary and exit. Do NOT commit, do NOT open PRs, do NOT use any connector other than substack-mcp.
