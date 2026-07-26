---
name: substack-auto-like
description: >
  Auto-like recent Substack notes to SUPPORT Daniel's mutual-recommendation partners
  first — a steady "I see you" signal to the people whose recommendation cards actually
  send him subscribers. Mutuals get guaranteed daily coverage via deterministic
  bucketing (nobody starves), leftover budget goes to reciprocal interactors and
  one-way recommenders.
  Self-contained cloud/PC task — NEVER ask questions, NEVER wait for an ack-gate.
  Uses ONLY the substack-mcp connector tools + Bash (date + the final notify curl).
  Runs 5x/day with a hard cap of 7 likes per run.
---

# substack-auto-like

**Inputs from the routine prompt (NOT in this file — public repo):**
- `NOTIFY_KEY` — subhook Telegram relay key. If missing, skip notify steps.

Self-contained: NEVER ask questions, NEVER wait for an ack-gate. Use ONLY
substack-mcp + Bash (`date`, notify curl).

**Design intent (read this before changing tiers):** mutual recommendations are the
only engagement target with proven subscriber attribution (`xpSignups` on incoming
recs). Likes are cheap, so the goal is *coverage* of every mutual partner every day,
not volume on whoever happens to be loudest. Daniel handles comments manually — this
routine only does likes.

## Steps

### 0 — figure out which run this is

Run `date +%H` (Bash). Compute `runIndex = clamp(floor((hour - 6) / 3), 0, 4)`.
Scheduled runs are 06:37 / 09:37 / 12:37 / 15:37 / 18:37 CET → runIndex 0–4.
An off-schedule manual run just lands on whichever bucket its hour maps to.

### 1 — gather the network from TWO sources

a) `get_recommendations({include:"both"})` → `{ outgoing:[...], incoming:[...] }`, each
   entry `{ publicationId, name, subdomain, userId, isMutual, isActive, xpSignups }`.
   Keep only `isActive === true`.

b) `get_recent_interactors({sinceHours: 72})` → `{ ok, interactors:[...] }`, each entry
   `{ userId, handle, name, types, interactionCount, lastInteractionAt }` — people who
   liked / restacked / replied / commented / followed Daniel in the last 3 days.

Do NOT call `get_subscriptions` — plain subscriptions were the weakest tier and are
dropped (they burned budget that belongs to mutuals).

If BOTH calls fail / return `ok:false` (e.g. cookie expired), send the failure Telegram
(step 5b) and STOP. If only one fails, continue with the other.

### 2 — build the target list

Dedupe by `userId` across all tiers (first tier a person appears in wins; drop entries
with null/missing `userId`).

**Tier A — mutual recommendations (the point of this routine).**
All entries with `isMutual === true` (they appear in both directions; dedupe them).
Sort ascending by `userId` — this ordering must be stable across runs, so no shuffling
here. Then keep only the entries where `index % 5 === runIndex`.

That gives each mutual partner exactly one checked slot per day (~4 people per run out
of ~19 mutuals) and guarantees nobody gets starved by a noisy neighbour eating the cap.
Within the bucket, process highest `xpSignups` first.

**Tier B — reciprocal interactors** from (1b) who are NOT already in tier A. Shuffle.
These are people worth converting into future mutuals.

**Tier C — one-way recommendations** from (1a) with `isMutual === false`. Shuffle.

Process tier A fully, then B, then C, until the cap is hit.

### 3 — fetch notes per target

For each target (serially, do NOT parallelize) call
`get_user_notes({ userId: <userId>, limit: 3 })` → notes with
`{ noteId, url, text, publishedAt, likesCount }`.

### 4 — like fresh notes only

Freshness window depends on tier, because tier A is checked once a day while B/C get
looked at every run:

- tier A → `publishedAt` within the last **26 hours**
- tier B → within the last **24 hours**
- tier C → within the last **12 hours**

For each qualifying note call `like_note({ noteId: <noteId> })`. It is idempotent
(re-liking returns ok), so an occasional overlap is harmless — but it still costs a
budget slot, so respect the per-person limit below.

Keep a running count of likes attempted + succeeded, and collect up to 5 sample
`name — first 40 chars of note text` lines.

### 5 — safety caps (HARD)

At most **2 notes per person** and **AT MOST 7 likes total per run** (≈35/day ceiling,
realistically 10–20 since not everyone posts daily). Once 7 likes are done, stop and go
to notify.

If a `like_note` returns an auth/cookie error, stop immediately → step 5b. If it returns
a rate-limit error, wait briefly and continue with the next person.

### 5a — SUCCESS notify

```
curl -s -X POST "https://subhook.fly.dev/api/notify?key=$NOTIFY_KEY" -H 'Content-Type: application/json' \
  -d '{"title":"❤️ Substack auto-like — <YYYY-MM-DD HH:MM>","text":"Liked <succeeded>/<attempted> notes. Mutual bucket <runIndex>/5: <N> partners checked, <M> liked.\n<up to 5 sample lines>"}'
```

If 0 notes qualified, still send a short success note saying `0 new notes this run`
plus which mutual bucket was checked — a bucket that is repeatedly empty is a signal
those partners went quiet.

### 5b — FAILURE notify (cookie/auth error or all source calls failed)

```
curl -s -X POST "https://subhook.fly.dev/api/notify?key=$NOTIFY_KEY" -H 'Content-Type: application/json' \
  -d '{"title":"⚠️ Substack auto-like FAILED — <YYYY-MM-DD HH:MM>","text":"<short reason, e.g. cookie expired — rotate via set_substack_cookie>"}'
```

### 6 — wrap-up

Print a one-line summary to stdout and exit. Do NOT commit anything, do NOT open PRs,
do NOT use any MCP other than substack-mcp.
