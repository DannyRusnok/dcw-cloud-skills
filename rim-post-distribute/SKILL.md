---
name: rim-post-distribute
description: >
  Post-publish distribution of an already-published Reads in Motion post: share it
  into the RiM Substack chat, publish a link-card note from `readsinmotion`, and
  plain-restack that note from `danielrusnok` (NO commentary). Companion to
  `rim-top10-video`, which stops at the draft. Use when Daniel says: "rozešli to
  do RiM chatu", "distribuuj ten RiM post", "rozešli RiM top 10", "udělej note a
  restackni to", "post to chat + note + restack", "rozjeď distribuci RiM postu",
  "sdílej ten post". Activates whenever Daniel pastes a published
  readsinmotion.substack.com/p/... URL with intent to distribute it. Runs all three
  steps without asking — Daniel invoking the skill IS the authorization.
---

# rim-post-distribute

Takes one **already-published** RiM post URL and fans it out in three steps:
chat → note → restack. Nothing here drafts or edits the post itself — if the post
isn't live yet, stop and say so.

## Tooling (deferred — load in ONE ToolSearch call)

```
select:mcp__substack-mcp__share_post_to_chat,mcp__substack-mcp__share_post_as_note,mcp__substack-mcp__restack_note
```

## STEP 1 — RiM chat

`share_post_to_chat(account='readsinmotion', postUrl=<url>, message=<lead-in>)`

Lead-in = one sentence, plain English, no link (the URL is appended automatically).
Chat notifies subscribers without burning an email send.

## STEP 2 — note from readsinmotion

`share_post_as_note(account='readsinmotion', postUrl=<url>, text=<body>)`

Body rules (all mandatory):

- **English**, plain short sentences — no metaphors, no jargon, no hype.
- **One sentence per line, blank line between every sentence.** No wall-of-text
  paragraph. See [[feedback_notes_sentence_per_line]].
- 4–6 sentences. Open with what the post is, then **two concrete numbers pulled
  from the post itself** (never invented, never rounded differently than the post).
- No "check it out", no trailing link — the link card is the attachment.

Returns the note URL — you need it for step 3.

## STEP 3 — plain restack from danielrusnok

`restack_note(targetNoteUrl=<note url from step 2>)`

**NO `commentary` argument. Ever.** Daniel restacks RiM posts bare — the note copy
already carries the message, and commentary on your own cross-account restack reads
as self-promotion stacked on self-promotion. This overrides the
"[[feedback_restack_commentary_default]]" rule, which is about restacking *other
people's* notes during daily engagement.

`restack_note` has no `account` param — it always posts as the primary account
(`danielrusnok`), which is what we want.

### Expected gotcha

`restack_note` returns the full note payload (~80k chars) and will blow the tool
result limit. That is **not a failure**. The harness saves it to a file; read the
first ~400 chars and confirm `"ok": true` + grab `noteUrl`:

```
python3 -c "print(open('<saved path>').read()[:400])"
```

## STEP 4 — report

Three lines back to Daniel: chat threadId, note URL, restack URL. No summary
paragraph.

## Guardrails

- Post must already be **published**. Never publish or edit the post from here.
- Restack target = the note *you* just created in step 2, never the post URL.
- Never restack a note that was already restacked — if re-running the skill on the
  same post, check for an existing note before creating a duplicate
  ([[feedback_restack_dedup_against_history]]).
- Numbers in the note copy come from the post body only. No estimates, no
  recomputed percentages.
- RiM note/restack endpoints work fine as of 2026-07-18 — the "anti-spam blocked"
  warning in `rim-top10-video` is stale for this path.
