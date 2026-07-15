---
name: reads-in-motion-big
description: >
  Autonomous routine for the 'Reads in Motion' curation account (account='readsinmotion').
  Runs 5x/day: pick ONE article from a BIG newsletter in Substack's Suggestions, write a
  short note, and ENQUEUE an async reel job. Does NOT render or publish itself — the
  substack-mcp worker renders (one at a time, waits for GPU/RPK) and auto-publishes as
  Reads in Motion + a danielrusnok promo comment. Self-contained: NEVER ask questions,
  NEVER wait for an ack-gate. Uses substack-mcp tools + Bash (notify only).
---

# reads-in-motion-big

Async outreach routine. The slow render no longer runs inline — you ENQUEUE and exit; the
substack-mcp worker drains the queue, renders, and posts. This never fails on a busy GPU or
a restarting render server: the render just waits its turn in the queue.

`NOTIFY_KEY` — klíč pro subhook Telegram relay. **NENÍ v tomto skillu** (public repo) — routine prompt ho dodá.

## Self-heal on Substack auth errors

If ANY substack-mcp call in this routine (find_reel_candidate, enqueue_reel_outreach,
or any later call) returns an auth error — `auth_expired`, HTTP 401/403,
"subscriptions returned 401 (cookie expired)", "recommendations could not resolve
publication id", or "Substack session cookie has expired" — DO NOT fail. Instead:

1. WebFetch `https://raw.githubusercontent.com/DannyRusnok/dcw-cloud-skills/main/substack-cookie-heal/SKILL.md`
   and follow it with `account: "readsinmotion"` (this routine always runs as that
   account).
2. Then retry the original failed action ONCE.
3. Only if the heal itself fails (`needsLogin: true`, PC unreachable, or the
   retry still 401s) → send a failure notify via subhook and exit.

One refresh per run; no retry loops.

## STEP 1 — candidate

find_reel_candidate (substack-mcp) `{ source: 'suggestions', account: 'readsinmotion', topK: 25, daysBack: 30, excludeRecentAuthorDays: 7 }`. It excludes official Substack pubs, holds the follower band, and skips articles already done + authors tapped in the last 7 days (global across both accounts). Take THE TOP candidate with a non-null `authorHandle` AND `authorUserId` = THE PICK. If none qualify, Bash-curl the success notify (title `Reads in Motion — no candidate`, text `Suggestions pool returned nothing new this run.`) and exit.

## STEP 2 — note (English)

Write a SHORT note, TIGHT so the text doesn't steal attention from the reel:

- credit the author with `@<authorHandle>`,
- ONE short concrete sentence about what THIS post is about (no template, no hype),
- a SHORT restack nudge on its own line — VARY it run-to-run (e.g. `Restack to send it to more readers.` / `A restack carries it further than a like.` / `Worth a restack if it lands.` / `Restack it onward if it's useful.`); never repeat the same one twice in a row,
- the article URL on its own line.

## STEP 3 — ENQUEUE + exit

enqueue_reel_outreach (substack-mcp) `{ account: 'readsinmotion', url: <PICK.url>, publicationName: <PICK.publication>, authorHandle: <PICK.authorHandle>, authorUserId: <PICK.authorUserId>, authorName: <PICK.authorName>, content: <your STEP 2 note text, including the '@<authorHandle>' token and the URL> }`.

It returns immediately. **Do NOT render, do NOT poll, do NOT upload, do NOT publish** — the worker renders the reel (serial, waits for the GPU/RPK), auto-publishes it as Reads in Motion, and adds the danielrusnok promo comment, all asynchronously.

## STEP 4 — exit (no queued notify)

Do NOT send any "queued" success notify — Daniel only wants ONE Telegram message: the finished reel, which the substack-mcp worker delivers when the render is done. Silently enqueue and exit. (The failure notify earlier in this skill still fires on hard errors so failures are not silent.)

Print a one-line summary and exit. Do NOT commit, do NOT open PRs, do NOT use any connector other than substack-mcp.
