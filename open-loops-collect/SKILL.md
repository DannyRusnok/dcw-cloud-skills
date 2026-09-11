---
name: open-loops-collect
description: |
  Cloud routine collector for Daniel's Open Loops board (substack-mcp /crm/loops).
  Every 2 hours it reads Gmail (Pygmalino threads with Ivana), Slack + Notion
  (Product Fruits stories, DMs, mentions) and the reel-pipeline-studio git
  checkout (RPS), turns each into "open loop" cards (whose move it is, what is
  next) and POSTs one snapshot per source to substack-mcp. The board keeps no
  state of its own — every run replaces the whole snapshot. Run when Daniel
  says "collect open loops", "refresh loops board", "open loops collect".
---

# open-loops-collect

Output = 3 snapshot publishes (Substack MCP tool `publish_open_loops_snapshot`), one per
source: `pygmalino`, `productfruits`, `rps`. Nothing else is written anywhere.
No Telegram, no Notion writes, no Gmail changes, no git pushes.

## Config (from the routine prompt)

- `LOOPS_INGEST_TOKEN` — bearer for the HTTP snapshot endpoint (unused on the MCP path). Never print it.
- Timezone for all "today" / weekday logic: **Europe/Prague**.
- Daniel = Gmail `danielrusnok@gmail.com`, Slack user `U098B8E3M0V`,
  Notion user `241d872b-594c-818d-a3bb-0002f80e749b`.
- Ivana (Pygmalino e-shop, Daniel's wife) = `ivana.heczkova@gmail.com`.

## Snapshot format (exact)

```json
{
  "source": "pygmalino",
  "generatedAt": "<ISO 8601 UTC now>",
  "ok": true,
  "error": null,
  "cards": [
    {
      "id": "gmail:<threadId>",
      "area": "pygmalino",
      "title": "Alza listing · RC 18857188",
      "source": "Gmail · Ivana",
      "turn": "me",
      "turnLabel": "Your move · 1 d",
      "next": "Ivana sent the category list. Map it in pygmalino-feeds.",
      "lastActivity": "last: Ivana, Wed 18:05",
      "lastAt": "<ISO 8601 of the last message>",
      "url": "https://mail.google.com/mail/u/0/#inbox/<threadId>",
      "urlLabel": "open thread"
    }
  ],
  "rhythm": [],
  "health": [ { "name": "Gmail", "ok": true, "note": "4 threads in 30 d", "at": "<ISO now>" } ]
}
```

Rules that the board relies on:
- `area` ∈ `pygmalino | productfruits | rps`. `turn` ∈ `me | them | auto | stale`.
- `me` = the other side acted last and Daniel owes a reply/decision.
  `them` = Daniel acted last, waiting on someone. `auto` = a machine is working
  on it. `stale` = no movement for 7+ days (either side) or overdue.
- `turnLabel` always carries the age: `Your move · 2 d`, `Waiting on Ivana · 3 d`,
  `Silent · 9 d`.
- `title` ≤ 70 chars, English, names the topic (never just a person).
- `next` = one plain English sentence, ≤ 14 words, what Daniel does next or what
  he is waiting for. No "consider", no fluff.
- Max **8 cards per source**. Fewer is better. Drop noise. When over the cap keep in this
  order: `me` first, then `stale`, then `them`, then `auto`; newest activity first within a group.
- Drop anything whose last activity is older than 30 days unless it is a `stale` card
  for work Daniel is supposed to be doing (status In progress / Fix needed / Ready to merge).
- Every source posts even when it has 0 cards (that is how "nothing open" shows).
- If a source's read fails, still POST it with `ok:false`, `error:"…"`,
  `cards:[]`, `health:[{name, ok:false, note}]` — the board shows the failure
  instead of stale data.

Publish each snapshot through the **Substack MCP connector** tool
`publish_open_loops_snapshot` with `{ "snapshot": <the object above> }` — one call per
source. Expect `{"ok":true,...}`; if it returns `ok:false`, report the `error` verbatim.
The routine sandbox cannot reach `substack-mcp.fly.dev` over plain HTTPS (egress policy
403), so **do not use curl** for this; the MCP tool is the only path. If the tool is not
available in the session, say so in the run summary and stop — do not try other routes.
`LOOPS_INGEST_TOKEN` is not needed for the MCP path (kept in the prompt only for a
future direct-HTTP fallback).

## Source 1 — Pygmalino (Gmail)

1. `search_threads` query: `(from:ivana.heczkova@gmail.com OR to:ivana.heczkova@gmail.com) newer_than:30d`,
   pageSize 30. Fallback if the OR form errors: run the two halves separately and merge
   by threadId.
2. For each thread (max 12, newest first) `get_thread`. Use only headers + the first
   ~600 chars of the newest 2 messages (`plaintextBody`); never load whole HTML bodies
   into context. Emails can be 100k+ — read the saved file with Python and slice.
3. Determine the **last sender**: `From` header of the newest message.
   - Ivana last → `turn: "me"`, `turnLabel: "Your move · N d"`.
   - Daniel last → `turn: "them"`, `turnLabel: "Waiting on Ivana · N d"`.
   - Either side, last message ≥ 7 days old → `turn: "stale"`, `turnLabel: "Silent · N d"`.
   - N = whole days since the last message (Prague).
4. Skip threads that are clearly closed: the newest message says thanks/done/hotovo
   and nothing is asked, or the subject is a receipt/notification/forwarded newsletter.
5. Group threads about the same project (same subject stem or same product/feed)
   into ONE card; mention the count in `lastActivity` (`3 threads`).
6. `title` names the project (e.g. `Christmas Heureka feed`, `Alza listing · RC 18857188`,
   `VO feed #2 photos`). `next` names the concrete thing (send photos, map categories,
   confirm price).
7. `url` = `https://mail.google.com/mail/u/0/#inbox/<threadId>`.
8. `health`: `{ name: "Gmail", ok: true, note: "<n> threads in 30 d", at }`.
9. If the Gmail connector exposes no read tools (`search_threads` / `get_thread` missing —
   find them with ToolSearch "Gmail" first), post the source with `ok:false`,
   `error: "Gmail connector has no read tools"`, `cards: []` and move on. Do not stop the run.

## Source 2 — Product Fruits (Notion + Slack)

### 2a Notion stories owned by Daniel

`notion-query-data-sources` SQL mode on `collection://1238073e-0c8c-4052-bf60-0485acf53a67`:

```sql
SELECT "userDefined:ID" AS id, "Story name" AS name, "Status" AS status,
       "Last edited time" AS edited, url
FROM "collection://1238073e-0c8c-4052-bf60-0485acf53a67"
WHERE "Owner" LIKE '%241d872b-594c-818d-a3bb-0002f80e749b%'
  AND ("Status" IS NULL OR "Status" NOT IN ('Done','Closed'))
  AND ("Archived" IS NULL OR "Archived" = '__NO__')
ORDER BY "Last edited time" DESC LIMIT 30
```

Map status → card (one card per story, title `STORY-<id> · <name ≤ 45 chars>`):
- `In progress`, `Fix needed`, `Ready for dev` → `turn: "me"`, label `Your move · <status>`.
  `next`: `Fix needed` → "QA found a problem, fix and move to For testing";
  `In progress` → "Finish and move to For testing"; `Ready for dev` → "Start it or move it to To-do".
- `For testing`, `In testing` → `turn: "them"`, label `Waiting on QA · <status>`,
  `next`: "Nothing for you until QA reports back".
- `Ready to merge` → `turn: "me"`, label `Your move · merge`, `next`: "Merge it and move to Done".
- `To-do` → skip unless edited in the last 3 days (then `turn: "them"`, label `Queued`).
- Any story with `edited` older than 10 days and status in (In progress, Fix needed,
  Ready to merge) → `turn: "stale"`, label `Stale · N d`, `next`: "Either push it or say in Notion it moves later".
- Stories in `For testing` / `In testing` edited more than 30 days ago are abandoned QA
  items, not loops → skip them.
- `lastActivity`: `edited <weekday HH:mm>`; `lastAt` = edited; `url` = the Notion url; `urlLabel` "story".
- If the SQL query is refused (plan limit), fall back to rows mode with filter
  `Owner person_contains user://241d872b-594c-818d-a3bb-0002f80e749b`, same mapping.

### 2b Slack — things waiting on Daniel

- `slack_search_public_and_private` with `filters: "to:<@U098B8E3M0V> after:<7 days ago YYYY-MM-DD>"`,
  `sort: "timestamp"`, `limit: 20`, `include_context: false`, `channel_types: "im,mpim"`.
- Also `filters: "<@U098B8E3M0V> after:<7 days ago>"` with `keywords: []` for channel mentions
  (limit 20). If the mention search errors, skip it.
- Group results by conversation (DM partner / channel). For each conversation whose
  **newest message is not from Daniel** and reads like a question, request, or review
  ping addressed to him → one card, `turn: "me"`, `turnLabel: "Your move · N d"`,
  `title`: `<Name> · <topic ≤ 40 chars>`, `source: "Slack DM"` or `"Slack #channel"`,
  `next`: what he should answer/do. Skip small talk, FYIs, and anything he already
  answered later in the same conversation.
- Do NOT create cards for conversations where Daniel wrote last (no "waiting on" from Slack;
  too noisy).
- Max 4 Slack cards. `url`: the message permalink if the result gives one, else omit.

`health`: `{ name: "Notion PF", ok }`, `{ name: "Slack PF", ok }`.

## Source 3 — RPS (reel-pipeline-studio checkout)

The routine's environment has `https://github.com/DannyRusnok/reel-pipeline-studio`
checked out (find it with `ls ~` / `ls /` — it sits next to `dcw-cloud-skills`).

```bash
cd <checkout> && git log -1 --format='%ci|%s' && git log --since=7.days --oneline | wc -l \
  && git log --since=30.days --format='%ad' --date=short | sort -u | wc -l
```

Cards:
- Always one card `Studio · activity`, `source: "git"`:
  - last commit ≤ 3 days ago → `turn: "auto"`, label `Active · <n> commits in 7 d`,
    `next`: "<last commit subject>" (≤ 90 chars).
  - 4–6 days → `turn: "them"`, label `Quiet · N d`, `next`: "Last: <subject>".
  - ≥ 7 days → `turn: "stale"`, label `Untouched · N d`, `next`:
    "Walk the studio with the UX AI method library and list where the UI hurts."
  - `lastActivity`: `last commit <YYYY-MM-DD>`; `url`: `https://github.com/DannyRusnok/reel-pipeline-studio/commits/main`.
- If `git log --since=2.days --grep='^fix\|^revert\|hotfix' -i --oneline | wc -l` ≥ 3 →
  extra card `Studio · fix churn`, `turn: "me"`, label `<n> fixes in 48 h`,
  `next`: "Check the studio is still healthy on the PC before deploying more."

`health`: `{ name: "RPS git", ok }`. Rhythm array stays empty for all three sources.

## Output of the run

Last message of the run, plain text, ≤ 6 lines:

```
open-loops-collect <ISO now>
pygmalino: <n> cards (<ok|error>)
productfruits: <n> cards (<ok|error>)
rps: <n> cards (<ok|error>)
```

No other artifacts. Do not open PRs, do not edit repos, do not send messages.
