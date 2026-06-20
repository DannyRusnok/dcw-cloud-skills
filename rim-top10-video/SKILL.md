---
name: rim-top10-video
description: >
  On-demand "Reads in Motion — Top 10 Reels" pipeline: build the weekly TOP 10
  leaderboard of the most-engaging reels the curation account `readsinmotion`
  posted in the last 7 days, draft a publish-ready Substack Post in Article Forge,
  and render the branded 14:10 TOP 10 leaderboard VIDEO (hook + 10 ranked cards,
  Kokoro narration + karaoke captions + own Codex-generated backgrounds) via
  `article-forge/scripts/render-leaderboard-video.ts` on the home PC, then embed
  the video into the draft. Manual sibling of the `rim-top-reels-weekly` cron.
  Use when Daniel says: "udělej RiM top 10", "reads in motion top 10",
  "top 10 reels video", "leaderboard video", "vyrob top 10 video", "RiM žebříček",
  "weekly top 10 reels", "rim top 10 článek a video". NEVER publishes — leaves a
  DRAFT + video URL for Daniel to publish manually.
---

# rim-top10-video

Builds this week's **Reads in Motion Top 10 reels** as a publish-ready Substack
Post draft **+** a branded leaderboard video, on demand. This is the interactive,
manually-invokable version of the `rim-top-reels-weekly` PC cron
(`dcw-context-hub/ops/rim-top-reels-weekly-prompt.md`) — same ranking logic, same
renderer. **It NEVER publishes** (RiM Post/note endpoints are anti-spam blocked);
Daniel publishes from the Article Forge draft manually.

The leaderboard VIDEO is the centerpiece and the reason this skill exists:
`article-forge/scripts/render-leaderboard-video.ts` (pure ffmpeg + Sharp +
kokoro-js + Codex image gen, NO ComfyUI/Wan/RPK). It MUST run on the home PC
(`aivideo-pc`) — Codex CLI image gen, ffmpeg, kokoro-js and R2 creds live there.

## Tooling (load via ToolSearch — most are deferred)

- substack-mcp: `get_user_notes`, `get_note_stats`, `send_telegram_message`,
  `get_cookie_status`
- article-forge: `create_article`, `get_article`, `update_article`
- pc-mcp: `ping` (liveness)
- Bash / SSH to `aivideo-pc` (see the `aivideo-pc-ssh` skill) to run the renderer

## STEP 0 — preflight

- `ping` (pc-mcp) → PC must answer. If asleep, wake it / abort with a note.
- `get_cookie_status` → if no cookie or stale and any substack call 401s, run the
  `substack-cookie-heal` skill with `account: "readsinmotion"`, then retry once.

## STEP 1 — collect reels (last 7 days)

`get_user_notes` `{ handle: "readsinmotion", limit: 100 }`. Keep only notes with
`hasVideo: true` AND `publishedAt` within the last 7 days (now − 7d → now, UTC).
Each kept note = one reel. If fewer than 3 reels are in the window, STOP — send a
Telegram "RiM: only <N> reels in 7 days, leaderboard skipped" and exit.

## STEP 2 — rank (authoritative stats, no shortcuts)

For **every** reel in the window call `get_note_stats`
`{ account: "readsinmotion", noteExternalId: "c-<noteId>" }` and read
`impressions`, `interactions`, `videoPlays`.

⚠️ GOTCHA: `interactions` from note_stats counts likes + restacks + replies +
**link clicks + profile visits** — it is NOT `likesCount+restacksCount+commentsCount`
from `get_user_notes`. So you CANNOT pre-filter candidates by the like counts;
a low-like reel with high click-through can outrank a high-like one. Fetch
note_stats for ALL window reels, then rank.

Sort by `interactions` desc, tiebreak `impressions` desc. Take the **TOP 10**.
For each keep: clean article title (~5–8 words), author name without `@`, the
reel note `url`, the original post URL (last https link in the note text),
impressions / interactions / videoPlays.

If `get_note_stats` fails for a reel, fall back to
`likesCount+restacksCount+commentsCount` and mark it `*` (approx).

## STEP 3 — build the Substack Post draft (publish-ready, clean HTML)

HARD RULE: `create_article` / `update_article` store the body **VERBATIM** (no
markdown→HTML conversion). Author the body as **clean semantic HTML** directly
(`<p>`, `<h3>`, `<strong>`, `<a href>`) — never markdown. Neutral 3rd-person RiM
curation voice (no "I/my", no restack-bait, no Daniel avatar/cover).

Structure (all English — publishing default):
- **Title**: `Reads in Motion — Top 10 Reels (Week of <range>)`.
- **Subtitle**: one line.
- **Intro** (2 sentences): what RiM does + this is the 10 reels that pulled the
  most engagement this week.
- **`How this was ranked`** (`<h3>` + 2 short `<p>`): window = last 7 days; each
  reel = one RiM note featuring one Substack post; numbers from Substack per-note
  stats; ranked by interactions (likes/restacks/replies/link clicks/profile
  visits) with impressions as tiebreaker; define impressions, interactions, plays
  (note plays can exceed impressions via replays). If any reel used the `*`
  fallback, say so in one sentence.
- **Ranked list 1–10**, per entry:
  - `<h3>#N — <author> · <title></h3>`
  - `<p><strong>imp</strong> impressions · <strong>int</strong> interactions · <strong>plays</strong> plays</p>`
  - one interpretation sentence grounded ONLY in the numbers (engagement rate =
    interactions/impressions %, play-through = plays/impressions %, hook
    strength). Do not invent external causes.
  - `<p><a href="reelUrl">Watch the reel</a> · <a href="postUrl">Read the original</a> by <author>.</p>`
- **Outro** (1 `<p>`): gentle subscribe CTA.

`create_article` `{ platform: "substack", title, subtitle, content: <HTML> }`.
Save the returned `id`. Then `get_article(id)` → grab `userId` AND verify the
content stored as HTML (starts with `<p>`/`<h3>`, no leftover `##`/`**`). If
markdown leaked, re-send corrected HTML via `update_article` once (or run the
`af-draft-format-polish` skill on the id).

## STEP 4 — render the leaderboard VIDEO (on PC)

Write `tmp-rim-leaderboard.json` in the PC's `%USERPROFILE%\foundary-tools\article-forge`:

```json
{ "weekOf":"<range, e.g. Jun 13-20>", "userId":"<userId>", "articleId":"<id>",
  "voice":"af_bella",
  "entries":[ {"rank":1,"title":"<clean title>","author":"<author, no @>",
    "imagePrompt":"<1 short EN sentence: the POST's visual concept, symbolic/abstract>",
    "impressions":<imp>,"interactions":<int>,"plays":<plays>}, … 10 by rank ] }
```

`imagePrompt` is KEY: one short concept derived from what THAT post is about, so
each card's background evokes that post (the renderer wraps it in RiM brand style
— navy+amber, abstract, no text/faces — and generates it via Codex). No image
URLs; the renderer generates its own (hook bg is the bundled `assets/rim-hook-bg.png`).

Then on `aivideo-pc`, in `%USERPROFILE%\foundary-tools\article-forge`:
`git pull --rebase --autostash`, then run the renderer. It generates all 10 Codex
backgrounds + xfade transitions ⇒ ~15–20 min on a cold cache. Run it
**in the background** (the foreground Bash 10-min cap will time out a cold run)
and poll, e.g.:

```
npx tsx scripts/render-leaderboard-video.ts tmp-rim-leaderboard.json > /tmp/rim-lb.log 2>&1 &
```

then poll `/tmp/rim-lb.log` for `RESULT_URL: <url>`. If it dies on a missing
module (`kokoro-js`), run `npm install --no-audit --no-fund` once and retry.

Success = a line `RESULT_URL: <url>`. `IMAGE_HITS: x/10` = how many cards got a
Codex background (rest are branded gradient — fine). onnxruntime may print a
benign `mutex lock failed` AFTER a successful upload — ignore a non-zero exit if
`RESULT_URL` is present. No `RESULT_URL` → continue without the video, note it.

## STEP 5 — embed the video into the draft

Only if you have a video URL: `get_article(id)`, then after the first intro `<p>`
insert `<p>🎬 <a href="<videoURL>">Watch this week's Top 10 as a 30-second video</a></p>`
and immediately after it the bare URL on its own line
`<p><videoURL></p>` (so Substack auto-embeds the player on copy). Save via
`update_article(id, content=<HTML>)`.

## STEP 6 — notify + log

- `send_telegram_message` (omit account → Daniel's primary chat): short message,
  NO leaderboard dump: AF draft link
  `https://articleforge.digitalcraftworkshop.com/articles/<id>`, video URL (or
  "render failed"), and a one-line `#1: <author> (<int> int / <imp> imp), <N>
  reels in window`.
- `mem0_add`: `"rim-top10-video <YYYY-MM-DD>: top10 of <N> reels (7d), AF draft
  <ok|fail>, video <ok|fail>"` metadata `{"project":"reel-pipeline-kit","category":"fact"}`.

## Guardrails

- NEVER publish (no publish_* calls, no POST to /publish or /comment/feed). No
  notes, restacks, comments, likes. This skill only drafts + renders.
- NEVER invent numbers — every stat comes from `get_note_stats` (or the `*`
  fallback). Interpretation sentences stay within what the numbers show.
- The render runs on the PC only; do not attempt to render from the Mac.
