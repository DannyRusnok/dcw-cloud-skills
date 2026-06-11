---
name: substack-auto-like
description: >
  Auto-like recent Substack notes from people in Daniel's network — LOW VOLUME,
  targeted 'I see you' signal, a quiet-presence complement to his manual engagement.
  Reciprocity first: people who recently interacted with him get priority.
  Self-contained cloud task — NEVER ask questions, NEVER wait for an ack-gate.
  Uses ONLY the substack-mcp connector tools + Bash (for the final notify curl).
  Runs 5x/day with a hard cap of 5 likes per run (≈15–25/day total), so each run
  only likes notes published in the last few hours.
---

# substack-auto-like

**Inputs from the routine prompt (NOT in this file — public repo):**
- `NOTIFY_KEY` — subhook Telegram relay key. If missing, skip notify steps.

Self-contained: NEVER ask questions, NEVER wait for an ack-gate. Use ONLY
substack-mcp + Bash (notify curl).

## Steps

### 1 — gather the network from THREE sources

a) `get_recent_interactors({sinceHours: 72})` → `{ ok, interactors:[...] }`, each entry
   `{ userId, handle, name, types, interactionCount, lastInteractionAt }` — people who
   liked / restacked / replied / commented / followed Daniel in the last 3 days.
   Reciprocal likes are the strongest use case.

b) `get_recommendations({include:"both"})` → `{ outgoing:[...], incoming:[...] }`, each
   entry `{ publicationId, name, subdomain, userId, isMutual, isActive, xpSignups }`.
   From outgoing+incoming KEEP ONLY entries where `isActive === true`.

c) `get_subscriptions()` → `{ ok, subscriptions:[...] }`, each entry
   `{ publicationId, name, subdomain, userId, membershipState }` (newsletters Daniel
   reads; platform pub + his own already excluded).

If ALL THREE calls fail / return `ok:false` (e.g. cookie expired), send the failure
Telegram (step 6b) and STOP. If only some fail, continue with the rest.

### 2 — build the target list in PRIORITY TIERS

Deduped by `userId` (first tier a person appears in wins; drop entries with
null/missing `userId`):

- tier 1 = recent interactors (1a) — reciprocal "I see you back"
- tier 2 = mutual recommendations (1b, `isMutual === true`)
- tier 3 = subscriptions (1c)
- tier 4 = one-way recommendations (1b, rest)

Within each tier shuffle the order (rotate, don't always start from the same person).
Process tier 1 fully before tier 2, etc. — the like budget is small, so it goes to
the people where the signal matters most.

### 3 — fetch notes per target

For each target (process serially, do NOT parallelize), call
`get_user_notes({ userId: <userId>, limit: 3 })`. It returns an array of notes,
each with `{ noteId, url, text, publishedAt, likesCount }`.

### 4 — like fresh notes only

For each returned note, like it ONLY IF `publishedAt` is within the last 6 hours
(`publishedAt >= now minus 6h`) — EXCEPTION: for tier-1 interactors extend the window
to 24 hours (their notes are worth a slightly older like). Since this routine fires
5x/day the 6h window keeps each run to genuinely new notes and avoids re-liking.

For each qualifying note call `like_note({ noteId: <noteId> })`. `like_note` is
idempotent (re-liking returns ok). Keep a running count of likes attempted +
succeeded, and collect up to 5 sample `name — first 40 chars of note text` lines.

### 5 — safety caps (HARD)

Like at most 2 notes per person and AT MOST 5 likes total per run. Once 5 total
likes are done, stop liking and go to the notify step. If a `like_note` returns an
auth/cookie error, stop immediately and go to step 6b. If it returns a rate-limit
error, wait briefly and continue to the next person.

### 6a — SUCCESS notify

```
curl -s -X POST "https://subhook.fly.dev/api/notify?key=$NOTIFY_KEY" -H 'Content-Type: application/json' \
  -d '{"title":"❤️ Substack auto-like — <YYYY-MM-DD HH:MM>","text":"Liked <succeeded>/<attempted> fresh notes across <targetCount> people (interactors > mutuals > subs > one-way).\n<up to 5 sample lines>"}'
```

If 0 notes qualified (nothing new), still send a short success note saying
`0 new notes this run`.

### 6b — FAILURE notify (cookie/auth error or all source calls failed)

```
curl -s -X POST "https://subhook.fly.dev/api/notify?key=$NOTIFY_KEY" -H 'Content-Type: application/json' \
  -d '{"title":"⚠️ Substack auto-like FAILED — <YYYY-MM-DD HH:MM>","text":"<short reason, e.g. cookie expired — rotate via set_substack_cookie>"}'
```

### 7 — wrap-up

Print a one-line summary to stdout and exit. Do NOT commit anything, do NOT open
PRs, do NOT use any MCP other than substack-mcp.
