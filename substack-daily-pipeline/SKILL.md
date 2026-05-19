---
name: substack-daily-pipeline
description: |
  Single-pass orchestrator pro celý Danielův Substack denní plán — engine v2 (2026-05-18). Generates 5 originals (3 DCW-concrete + 2 generic-evergreen) + 0-N promo notes (auto z articles tabulky) + 4 commentary restacks + 8 pure restacks + 4 comments + 1 self-restack = 22 actions, validates a schedules vše naráz po jedné Danielově ack. NEPOUŽÍVÁ engagement_queue (wantlist-driven) — používá nový feed_pool (sourced z Substack home feed následovaných). Aplikuje memory feedback ihned (simple EN, anti-motivation filter, paraphrased originals, fact-check proti mem0/dcw-context-hub). Pre-flight: cookie health + refresh feed_pool + pending promo articles scan. Použij kdykoli Daniel řekne: "naplánuj zítřek", "daily pipeline", "naplánuj čtvrtek/pátek/sobotu/neděli/pondělí/úterý/středu", "spusť denní plán Substack", "připrav substack na zítra", "plán na zítra", "do daily plan", "celodenní substack plán". Default times pro originals: 8:30/11:30/14:30/17:30/20:30 CET. Engagement rozhozený 9:00–18:00 lokál.
---

# substack-daily-pipeline (v2)

Engine v2 — feed-driven engagement + bucket-based notes. Replaces engagement_queue with feed_pool, bumps originals from 3 → 5 (3 DCW concrete + 2 generic evergreen).

## Inputs

- **Target date** (default: tomorrow). "zítřek" / "čtvrtek" / "2026-05-14".
- **Time override** (optional): "notes 8/11/14/17/20" pokud chce jiné než default.

## Mandatory memory checks (read at start)

Apply silently — nikdy se neptej:
- `feedback_engagement_simple_english.md` → all engagement copy in plain short-sentence EN
- `feedback_engagement_daily_quota.md` → 5 originals + 0-N promos + 4 commentary + 8 pure + 4 comments + 1 self-restack
- `feedback_publishing_language_english.md` → all output EN
- `feedback_promo_never_counts_as_original.md` → promo content never counts toward 5 originals
- `feedback_notes_sentence_per_line.md` → blank line between every sentence (notes + engagement)

## Workflow

### 1. Pre-flight (silent, parallel)

- `mcp__grownote__trigger_substack_sync()` — own notes / subs data
- `POST /api/mcp/refresh-feed-pool` (Bearer `GROWNOTE_MCP_TOKEN`, body `{ownHandle: "danielrusnok"}`) — pulls latest 100 notes from following feed, scores, dedups against `restacks_log` 60d, GCs stale used items >7d
- `GET /api/mcp/pending-promo-articles?days=14` — returns articles + uncovered offsets
- Cookie health check: `mcp__grownote__get_scheduled_item({id: <any recent>, actionType: "note"})` — if `last_error: auth_expired` → **STOP** and surface to Daniel: "Cookie expired — refresh in grownote /settings. Pipeline aborted."

### 2. DCW tip extraction (parallel, silent)

Goal: 3 atomic practical takeaways for the DCW bucket (each = something a reader can use this week).

Pull in parallel:
- **mem0** — `mcp__c59fb103-b450-449c-95ee-94246e90f70e__mem0_search({query: "decision OR discovery OR learning", user_id: "daniel"})` last 30d, filter category=decision|discovery|learning
- **git commits across foundary-tools** — `git -C ~/foundary-tools/<repo> log --since=7.days --oneline` for: grownote, drippery, framelock, article-forge, archieve-concierge, subhook, dcw-context-hub. Take 10 most interesting (skip "docs:", "wip:", merges).
- **dcw-context-hub** — `mcp__dcw-context-hub__get_context({project: "<each-DCW-project>"})` for recent state changes worth surfacing
- **articleforge.articles** — most recent 5 published (Medium/Substack), extract 1 atomic takeaway each via inline reasoning

Distill into 3 DCW tips, each shape: `{category: "skill-hack|hook-pattern|memory-trick|cheap-infra|ai-workflow|mcp-tip|commit-learning|postmortem", text: "<concrete actionable sentence>"}`.

### 3. Originals generation (single call to grownote v2 endpoint)

`POST /api/mcp/schedule-daily-notes-v2` body:
```json
{
  "date": "<target ISO date>",
  "dcwTips": [{"category": "...", "text": "..."}, ...3 items],
  "model": "gemini-2.0-flash-lite"
}
```

Endpoint internally:
- Picks 2 generic tips from `seed-tips.json` (LRU rotation via `app_config.v2_seed_tip_usage`, category diversity)
- Drafts 5 notes via `generateNoteDraft` with anti-motivation filter + avoidAngles=last 15 originals
- Schedules into free slots: 8:30, 11:30, 14:30, 17:30, 20:30 CET (skip occupied)
- Returns `{scheduled: [...], skippedSlots: [...], errors: [...]}`

**DO NOT** also call legacy `schedule-note` for originals — v2 handles all 5.

### 4. Promo notes (auto)

For each pending article from step 1:
`POST /api/mcp/schedule-article-promo-batch` body `{article_ids: [<id1>, <id2>...], auto_schedule: true}`.
Endpoint computes PROMO_PLAN (D+0/+1/+2/+3/+5 @ 14:30 CET per offset), drafts via `generateNoteDraft` with full article body, inserts into `notes_log` with `format: "article_promo"`, `articleId`, `promoDayOffset`. Skips offsets already covered.

If `pending-promo-articles` returned 0 items → skip step entirely (silent).

### 5. Engagement pool pick

`GET /api/mcp/feed-pool-batch?commentary=4&pure=8&comments=4` →
```json
{
  "batch": {
    "commentaryRestacks": [...4 items],
    "pureRestacks": [...8 items],
    "comments": [...4 items]
  }
}
```

Each item: `{id, noteId, authorHandle, authorDisplayName, noteText, noteUrl, score}`.

**Per-author cap is enforced server-side** (max 1/day, 2/7d per handle) — pool already deduped against `restacks_log` 60d + own handle, so no extra dedup needed in skill.

If `pureRestacks` < 8 or `comments` < 4: re-trigger `POST /api/mcp/refresh-feed-pool` once and re-pick. If still thin → schedule what's available, note shortfall in summary.

### 6. Drafting engagement copy

For each batch item:
- **commentaryRestacks (4)** — generate 10-25w commentary in plain EN, fresh reaction to `noteText` (do NOT rewrite anyone else's draft); apply `feedback_restack_redraft_fresh_reaction.md`
- **pureRestacks (8)** — no text, just URL
- **comments (4)** — 2-4 sentence plain EN comment reacting to `noteText`; no questions; no vague praise

After scheduling each, `POST /api/mcp/mark-feed-pool-used {id, kind: "commentary_restack|pure_restack|comment"}` to update feed_pool status.

### 7. Self-restack (1)

**Call `GET /api/mcp/yesterday-top-original?baseDate=<today ISO>`** — endpoint picks Daniel's yesterday top-engagement **clean original** Note and returns `{candidate: {noteUrl, content, format, likes, restacks, comments, score}}`.

**Server-side rules** (do NOT re-implement in skill):
- Only ORIGINAL notes — restacks-with-note responses to others are excluded via heuristic (`scheduled_for IS NOT NULL` OR `length(content) > 250`). TODO: capture Substack `parent_id` in sync for exact discriminator.
- `format NOT IN ('restack', 'article_promo')` — engagement actions + promo notes don't count.
- `external_id IS NOT NULL` — need URL to restack.
- `self_restacked_at IS NULL` AND URL not in `restacks_log` where type='self' — dedup.
- ORDER BY `3*restacks + 2*comments + likes DESC, published_at DESC`.

If `found: false` → skip self-restack with single-line note in output ("no eligible yesterday original — pool empty"). Do not walk back further than yesterday in this skill — if Daniel wants older banger, he asks for `self_banger` rationale separately.

Generate **2 angles (A and B)** as fresh commentary on the candidate, 10-25 words each, plain EN, no questions. Default angle A is used by cloud routine; Daniel picks A or B in interactive mode.

### 8. Light review (internal, max 2 rounds)

Quality gates per item:
- **Originals**: anti-motivation filter (already enforced server-side, but verify), 30-80 words, sentence-per-line, no banned openers ("This morning", "Today I", "Just shipped"), one concrete actionable takeaway per note
- **Engagement**: plain EN, no questions in body, length cap, fact-check on personal claims (gate 9 — see below)

Round 1 = critique. Round 2 = rewrite failing. Round 3 → drop.

## Fact-checking (gate 9)

[Unchanged from v1 — query mem0 + dcw-context-hub + Notion in parallel for personal claims with numbers/named tools/durations. ✅ verified / ❌ contradicts auto-rewrite / ⚠️ unverifiable flag + Daniel confirms.]

### 9. Time distribution

Default CET slots:
- **Originals**: 8:30, 11:30, 14:30, 17:30, 20:30 (v2 endpoint handles)
- **Promo notes**: `<article.published_at> + dayOffset @ 14:30 CET` (batch endpoint handles; may collide with original slot → batch skips that offset for that article)
- **Engagement (17 actions)**: spread 09:00–18:00 CET, min 15-min gaps, never within 15 min of any note slot

### 10. Single output to Daniel

```
[TARGET DATE]

⚠️ Cookie OK / expired (warning)
Feed pool: <N inserted> fresh / <M total pending>
Promo articles: <K pending> (or "none")

Originals (5 = 3 DCW + 2 generic):
  08:30  N1  dcw       #skill-hack       <first 60 chars…>   [fact-check]
  11:30  N2  dcw       #postmortem       <first 60 chars…>   [fact-check]
  14:30  N3  dcw       #cheap-infra      <first 60 chars…>   [fact-check]
  17:30  N4  generic   #substack-growth  <first 60 chars…>
  20:30  N5  generic   #ddd-architecture <first 60 chars…>

Promo notes (auto, 0-N from pending articles):
  14:30  P1  promo (d+0)  "<article title>" → <first 60 chars…>   [fact-check]

Engagement (17 actions, 09:00–18:00):
  09:30  self-restack    yesterday's "<note snippet>"   [fact-check]
  10:15  commentary      @handle  score 24  "<target one-liner>"  → "<commentary 60c>"
  ...
  17:30  comment         @handle  score 18  "<target one-liner>"  → "<comment 60c>"

Self-restack angles:
  A — <angle A, plain EN>   [fact-check]
  B — <angle B, plain EN>   [fact-check]

Fact-check totals: ✅ N / ⚠️ N / ❌ N
```

End with: **"Pošli `ok a` / `ok b` / `drop N` / `edit N <text>` / `stop`."**

### 11. After Daniel's ack — schedule

- `ok a` or `ok b` → originals already scheduled by v2 endpoint in step 3; promo notes already scheduled by batch endpoint in step 4. **Only engagement needs scheduling now**: 4 commentary + 8 pure via `schedule_restack`, 4 comments via `schedule_comment`, 1 self-restack via `schedule_restack`. After each: `mark-feed-pool-used`.
- `drop N` → if N is original/promo: call `delete_scheduled_item` on its inserted ID. If engagement: just don't schedule that item.
- `edit N <new text>` → if N is original/promo: call `update_scheduled_item`. If engagement: swap text before schedule.
- `stop` → roll back step 3+4 inserts (`delete_scheduled_item` for each ID), return drafts as markdown.

Cron `scheduledItemsCron` in grownote (every 1 min) auto-publishes each item at its `scheduledFor`.

## Anti-patterns

- Never ask clarifying questions during generation — memory has defaults
- Never use motivational filler in originals ("you've got this", "embrace the grind", "unlock", "game-changer")
- Never open original with "This morning", "Today I", "Just shipped", "Good morning"
- Never use advanced EN in engagement copy (jargon, metaphors, idioms)
- Never present pure restacks with prose summary (they have no text to review)
- Never schedule before user ack (except step 3+4 server-side which are auto-rolled-back on `stop`)
- Never run 3-round review — 2 rounds max, skip-on-fail
- Never pull from `engagement_queue` (deprecated for daily pipeline — use `feed_pool`)
- Never restack same author 2× in one day or 3× in a week (server-side cap, but skill should not retry)

## Sister skill

`substack-add-handle <handle>` — quick wantlist insertion (separate skill; wantlist now used only for discovery/warming tracking, NOT for daily engagement source).
