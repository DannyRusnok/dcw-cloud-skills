---
name: mem0-weekly-consolidation
description: >
  Weekly mem0 consolidation. Self-contained cloud task — NO clarifying questions,
  NO ack-gate. Uses only mem0 MCP tools (mem0_get_all, mem0_search, mem0_delete,
  mem0_add) and Bash for the final notify + heartbeat curls. Dedup is bounded to a
  weekly cohort so the run stays cheap; the backlog drains over multiple weeks.
---

# mem0-weekly-consolidation

**Inputs from the routine prompt (NOT in this file — public repo):**
- `NOTIFY_KEY` — subhook Telegram relay key. If missing, skip the Telegram step.
- `HEARTBEAT_TOKEN` — craft-os Infra Fleet Bearer token. If missing, skip the heartbeat.

CONTEXT (infra v3, 2026-06-11): the index holds ~2000+ memories (incl. a one-time
backfill of 384 historical sessions). NEVER pull full entries — always use compact mode.

Scopes (alphabetical here, but you process by cohort, not per-scope pulls):
drippery, grownote, article-forge, archieve-concierge, subhook, craft-os, umami,
dcw-web, global, secondbrain, claude-config, infra

## STEP 1 — PULL (one call total)

`mem0_get_all({user_id: "daniel", compact: true})`

Each entry has: `id, memory, scope, category, created_at, migrated_from`.
- `scope` may be null (legacy entries) → treat as `"global"`.
- If the call fails, send the fail heartbeat (step 8) and abort.

## STEP 2 — BUILD COHORT (in-memory, no extra calls)

- cohort = entries with `created_at` between 21 and 7 days ago (older than 7d = safe
  to touch, newer than 21d = not yet processed by previous runs + backlog tail).
- Sort cohort oldest-first. HARD CAP: process at most 150 cohort entries per run; if
  more exist, note `backlog: N deferred` in the summary (picked up next week).
- SAFETY FILTERS: drop from cohort any entry with `migrated_from == "chroma"` whose
  scope is `"global"`/null AND whose memory text mentions any project slug above
  (possibly misclassified).

## STEP 3 — DEDUP PASS (per cohort entry, serially)

- `mem0_search({query: entry.memory, user_id: "daniel", limit: 5})`
- Keep hits with `score >= 0.92` AND `id != entry.id` AND same scope (null scope == "global").
- For each pair, the NEWER `created_at` wins (tie → keep the one with non-null scope;
  still tie → keep entry, delete hit). `mem0_delete` the older id. Increment `merged[scope]`.
- Track deleted ids; never search or delete an id twice.
- SAFETY CAP: max 50 deletes per scope per run; on hitting it, stop deleting in that
  scope and note it in the summary.

## STEP 4 — DECISION CONTRADICTION PASS (reasoning only, no extra mem0 calls)

- From the FULL compact list (not just cohort), group `category == "decision"` by scope.
- Within each scope, pair-compare decisions using your reasoning. CONTRADICTION =
  opposing concrete choices on the same topic, e.g.:
  - "use Redis for caching X" vs "use Postgres for caching X"
  - "deploy Drippery to Render" vs "deploy Drippery to Fly"
  - "primary LLM is Gemini" vs "primary LLM is OpenAI gpt-4o-mini"

  Different topics are NOT contradictions. When in doubt, do nothing.
- Only act when at least one of the pair is older than 7 days; never delete the newer one.
- For each contradicting pair: newer = canonical. For the older: `mem0_add` the same
  text with metadata `{scope: <scope>, category: "archived", superseded_by: <newer_id>,
  original_id: <older_id>}`, then `mem0_delete` the older id. Increment `archived[scope]`.
- Same 50-deletes-per-scope cap (shared with step 3).

## STEP 5 — SUMMARY

```
Line 1: "Weekly mem0 consolidation — <YYYY-MM-DD UTC>"
Line 2: "Total memories: <count_from_step1> | cohort processed: <N>/<cohort_size>"
Line 3: "Total pairs merged: <sum_merged>"
Line 4: "Total decisions archived: <sum_archived>"
Then one line per scope with activity: "  <scope>: <merged> merged, <archived> archived"
Plus "backlog: N deferred" and/or "safety cap hit in: <scopes>" if applicable.
```

## STEP 6 — Telegram push via Bash

`curl -s -X POST "https://subhook.fly.dev/api/notify?key=$NOTIFY_KEY" -d "<summary text — newlines OK>"`

## STEP 7 — OPTIONAL session journal

If the dcw-context-hub MCP tool `log_session` is available, call it with
session_id `mem0-weekly-consolidation-<YYYY-MM-DD>`, machine `claude-ai-routine`,
recap = the summary text. If unavailable, skip silently.

## STEP 8 — craft-os Infra Fleet heartbeat via Bash (ALWAYS, even on zero activity)

```
curl -s -m 10 -X POST 'https://craft-os.fly.dev/api/heartbeat' -H "Authorization: Bearer $HEARTBEAT_TOKEN" -H 'Content-Type: application/json' -d '{"unit":"mem0-weekly-consolidation","status":"ok"}'
```

On fatal error (mem0 unreachable, cap logic broken): same curl with `"status":"fail"`,
then still print whatever summary you have.

## STEP 9 — Print the summary to stdout. Exit.

## DO NOT

- Pull without `compact: true` (full payload is too large).
- Run `mem0_search` for entries outside the cohort.
- Open PRs, commit anything, or ask for confirmation before deletes.
- Delete more than 50 entries per scope, or process more than 150 cohort entries per run.
