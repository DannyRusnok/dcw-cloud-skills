---
name: substack-daily-review
description: |
  Interaktivní per-item review pipeline pro grownote naplánovaný Substack denní plán. Sister-skill k `substack-daily-pipeline` (který scheduleuje 22 items pro daný den). Tento skill projde každý naplánovaný item v pořadí podle skutečného `scheduled_for` ASC, vždy předloží Danielovi target + draft + (povinně CZ vysvětlení u restacků/komentářů), počká na akci (approve / redraft / flag+redraft / edit / delete / swap target), aplikuje ji přes grownote MCP a postoupí na další item. Použij kdykoli Daniel řekne: "review dnešní plán", "review notes", "projdi naplánované items", "review schedule", "projdi co máme na dnes", "review todays substack", "daily review", "review grownote schedule", "interactive review", "projdeme to". Aktivuj se i automaticky 30-60 minut po doběhnutí `substack-daily-pipeline` pokud Daniel řekne "teď to projdeme".
---

# substack-daily-review

Interactive per-item review of today's grownote schedule. Replaces ad-hoc "send me one at a time" requests.

## Inputs

- **Target date** (default: today CEST). Daniel says "review dnešek" / "review zítřek" / "review 19.5.".
- **Scope** (optional): "jen notes" / "jen restacks" / "jen comments" — default: all 3.

## Mandatory memory checks (read at start)

Apply silently:
- `feedback_engagement_simple_english.md` — engagement copy plain EN
- Daniel's preference (mem0 2026-05-19): **always provide Czech-language explanation of both target note and drafted reaction** for restacks/comments before asking action
- `feedback_publishing_language_english.md` — publishing output EN
- `feedback_promo_never_counts_as_original.md`
- Active corrections table — pull `SELECT content FROM grownote.corrections ORDER BY created_at DESC LIMIT 50` and use as no-go list when redrafting

## Workflow

### 1. List scheduled items for target date

Three parallel calls:
- `list_scheduled_items({actionType: "note", status: "scheduled", fromIso, toIso, limit: 50})`
- `list_scheduled_items({actionType: "restack", status: "scheduled", fromIso, toIso, limit: 50})`
- `list_scheduled_items({actionType: "comment", status: "scheduled", fromIso, toIso, limit: 50})`

Merge + sort by `scheduled_for` ASC (real DB time — NOT intended time, even if there's a known DST/offset bug on note scheduling).

### 2. Per-item presentation loop

For each item, format Daniel-facing block:

**Original notes (format != 'article_promo'):**
```
[N/TOTAL] HH:MM CEST — Original (<bucket> · <category>) · note id <id>

> <full content body>

⚠ <warn flags: ends with question, banned opener, missing sentence-per-line breaks, etc.>

Action? (approve / redraft / edit `<text>` / delete)
```

**Article promo notes (format = 'article_promo', has articleId + promoDayOffset):**
```
[N/TOTAL] HH:MM CEST — Article promo (D+<offset>) · note id <id>

**Source article (id <articleId>):** "<article title>" published YYYY-MM-DD
**Article URL:** <substackUrl>

> <full content body>

⚠ <warn flags + check: does body contain the article URL on its own line at the end?>

Action? (approve / redraft / edit `<text>` / delete)
```

Detect article promo: `format === 'article_promo'` OR (`article_id` is not null AND `promo_day_offset` is not null). Pull source article info via `articles` table JOIN (or call grownote's article listing).

**Self-restack (own note):**
```
[N/TOTAL] HH:MM — Self-restack · scheduled_actions id <id>

**Target (vlastní original z YYYY-MM-DD HH:MM):**
> <target content>

**Commentary:**
> <body>

Action? (approve / redraft / edit `<text>` / delete)
```

**Commentary restacks (external):**
```
[N/TOTAL] HH:MM — Commentary restack · scheduled_actions id <id>

**Target (@<handle>, score <score>, <date>):**
> <target note text, full>

**Commentary:**
> <body>

**CZ vysvětlení:** (MANDATORY)
*Target:* <2-3 věty co target říká, hlavní myšlenka>
*Tvá reakce:* <2-3 věty co commentary tvrdí + co o Danielovi implikuje>

Action? (approve / redraft / flag+redraft / edit `<text>` / delete / swap target)
```

**Pure restacks:**
```
[N/TOTAL] HH:MM — Pure restack · scheduled_actions id <id>

**Target (@<handle>, score <score>):**
> <target note text>

*Pure restack — bez commentary.*

Action? (approve / swap target / delete)
```

Optimalization: pokud Daniel řekne "pure restacky rovnou approve všechny" (nebo podobnou bulk-approve frázi), označit všechny zbývající pure jako approved a skipnout je v reportu (jen jednou rekapitulovat handle list).

**Comments:**
```
[N/TOTAL] HH:MM — Comment · scheduled_actions id <id>

**Target (@<handle>):**
> <target note text, full>

**Comment:**
> <body>

**CZ vysvětlení:** (MANDATORY)
*Target:* <2-3 věty>
*Tvá reakce:* <2-3 věty>

Action? (approve / redraft / flag+redraft / edit `<text>` / delete)
```

### 3. Action handlers

- **`approve` / `a`** — no-op, advance to next.
- **`approved` / `ok` / `y`** — synonyms for approve.
- **`edit <text>`** — `update_scheduled_item({id, actionType, changes: {content/body/commentary: "<text>"}})` (field name varies: notes use `content`, restacks use `commentary`, comments use `body`).
- **`edit`** (no text) — Daniel will follow up with edit text; if he just says general feedback, draft a proposed edit and confirm before applying.
- **`redraft`** — for notes: manually craft a new draft based on Daniel's stated direction (no MCP redraft for notes — `redraft_scheduled_item` skips notes); for restacks/comments: `redraft_scheduled_item({id, kind, swapTarget: false})` for body-only rewrite.
- **`flag+redraft`** — insert into `grownote.corrections` via psql (item_kind, item_id, content describing the hallucination, source_excerpt = current body), then redraft. Use psql since no MCP tool for corrections.
- **`swap target`** — `redraft_scheduled_item({id, kind, swapTarget: true})` to pull a different target from queue/pool + regenerate body. Note: current implementation pulls from old `engagement_queue` not `feed_pool` — tech debt.
- **`delete`** — `delete_scheduled_item({id, actionType})`.
- **`skip`** — advance without action (leave as-is).
- **`stop`** / **`pause`** — exit loop, show partial summary.

### 4. CZ vysvětlení (mandatory for restacks + comments)

Always include before asking action. Two short paragraphs:
- **Target:** what the author is saying, main thesis in 2-3 Czech sentences
- **Tvá reakce:** what the commentary/comment claims + what it implicitly says about Daniel (career claims, numerical claims, personal experience claims)

This catches hallucinations faster — Daniel reads Czech recap faster than raw English drafts.

### 5. Hallucination flag workflow

When Daniel says "halucinace" / "lež" / "flag" / "to není pravda":

1. Insert correction row:
   ```sql
   INSERT INTO grownote.corrections (content, reason, item_kind, item_id, source_excerpt)
   VALUES ('<concrete fact correction — what Daniel actually does/has, NOT what was claimed>',
           'flagged YYYY-MM-DD during restack/comment review — <one-line failure type>',
           '<note|restack|comment>', <id>, '<the offending text snippet>');
   ```
2. Confirm flagged.
3. If `flag+redraft`, proceed to redraft after insert.

### 6. Final summary

After loop ends (last item or `stop`):

```
**Review kompletní: X/Y.**

Summary:
- N originals (X edited + Y recreated + Z approved)
- N restacks: ... (X swap+approve, Y edit, Z approve)
- N pure restacks (bulk approved)
- N comments (X approve, Y edit, Z redraft+approve)
- N halucinace flagnuty do corrections table (<3-5 word labels>)

Žádný další item k review. Hotovo.
```

## Mandatory pre-display checks per note

Before showing each note, verify:
- **Sentence-per-line:** does content contain `\n\n` blank-line separators? If not, surface ⚠ "missing sentence-per-line formatting" — propose auto-reformat via `formatSentencesPerLine` (or just edit content to add breaks before display). Stored content should already have breaks; if it doesn't, `lib/format-sentences.ts` enforcement was bypassed somewhere.
- **Question in body:** if body ends with `?`, surface ⚠ "ends with question".
- **Banned opener:** first 4 words match any of: "This morning", "Today I", "Just shipped", "Good morning". Surface ⚠.
- **Banned phrase:** "unlock", "game-changer", "amazing", "incredible", "10x", "leverage". Surface ⚠.

These are display warnings — they don't block, they prompt Daniel to choose redraft/edit.

## Anti-patterns

- **Never** sort by "intended" time — always real `scheduled_for` from DB. Note slots may be off by an hour due to DST bug; restacks/comments use explicit `+02:00` offsets and are correct. Sort treats both honestly.
- **Never** auto-approve without showing item.
- **Never** schedule new items — this skill is review-only. New items come from `substack-daily-pipeline`.
- **Never** skip CZ vysvětlení on engagement items — it's the primary hallucination filter.
- **Never** use `redraft_scheduled_item` with `kind: "note"` — tool skips notes. Manually craft new note body and use `update_scheduled_item`.
- **Never** flag without inserting into corrections table — verbal flag without DB write means next drafter run repeats the same hallucination.
- **Never** edit a published item (`status='published'`) — only `scheduled`.

## Sister skill

`substack-daily-pipeline` — generates the schedule this skill reviews.
`sync-skill-to-hub` — run after editing this skill so cloud routines pick up the latest version.
